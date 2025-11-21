from rest_framework.views import APIView
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from interviews.models import Interview, InterviewQuestion, SMSMessages
from candidates.models import Candidate
from django.utils import timezone
from interviews.gemini import classify_answer_quality


class IncomingSMSWebhookView(APIView):

    def post(self, request, *args, **kwargs):
        print("\n--- Incoming Twilio Webhook ---")
        print("POST DATA:", request.POST)

        data = request.POST
        incoming_msg = (data.get('Body') or '').strip()
        sender_phone = data.get('From')
        msg_status = (data.get('MessageStatus') or data.get('SmsStatus') or '').lower()
        msg_sid = data.get('MessageSid')

        resp = MessagingResponse()

        # ============================================================
        # 1. HANDLE UNDELIVERED BEFORE *ANYTHING ELSE*
        # ============================================================
        if msg_status == "undelivered":
            print(f"[UNDELIVERED] Message SID {msg_sid} failed. Resending…")

            user_phone = data.get('To') or sender_phone
            candidate = Candidate.objects.filter(phone_number=user_phone).first()

            if not candidate:
                print("No candidate found for phone:", user_phone)
                resp.message("Delivery issue detected. Please wait.")
                return HttpResponse(str(resp), content_type='application/xml')

            interview = Interview.objects.filter(
                candidate=candidate,
                status__in=['scheduled', 'in_progress']
            ).first()

            if not interview:
                print("No active interview for undelivered resend.")
                resp.message("Delivery issue occurred, but no active interview exists.")
                return HttpResponse(str(resp), content_type='application/xml')

            last_outbound = SMSMessages.objects.filter(
                interview=interview,
                direction='outbound'
            ).order_by('-created_at').first()

            if not last_outbound:
                print("No outbound message to resend.")
                resp.message("Temporary issue occurred. Please try again.")
                return HttpResponse(str(resp), content_type='application/xml')

            resend_text = last_outbound.message_text
            print("Resending:", resend_text)

            resp.message(resend_text)

            SMSMessages.objects.create(
                interview=interview,
                direction='outbound',
                message_text=resend_text,
                status='sent',
                related_question=last_outbound.related_question
            )

            return HttpResponse(str(resp), content_type='application/xml')

        # ============================================================
        # 2. NORMAL INCOMING SMS (A USER REPLY)
        # ============================================================
        print("[INCOMING USER MESSAGE]:", incoming_msg)

        candidate = Candidate.objects.filter(phone_number=sender_phone).first()
        if not candidate:
            print("Unknown sender:", sender_phone)
            resp.message("We could not find an application linked to this phone number.")
            return HttpResponse(str(resp), content_type='application/xml')

        interview = Interview.objects.filter(
            candidate=candidate,
            status__in=['scheduled', 'in_progress']
        ).first()

        if not interview:
            print("No active interview.")
            resp.message(f"Hi {candidate.first_name}, you don't have an active interview session.")
            return HttpResponse(str(resp), content_type='application/xml')

        print("Interview status:", interview.status)

        # Find last outbound → determine which question user replied to
        last_outbound = SMSMessages.objects.filter(
            interview=interview,
            direction='outbound'
        ).order_by('-created_at').first()

        related_q = last_outbound.related_question if last_outbound else None

        # Save inbound message
        SMSMessages.objects.create(
            interview=interview,
            direction='inbound',
            message_text=incoming_msg,
            status='received',
            related_question=related_q
        )

        # ============================================================
        # CASE 1 — INTERVIEW WAITING FOR YES/NO CONFIRMATION
        # ============================================================
        if interview.status == "scheduled":
            print("Interview is scheduled → expecting YES/NO")

            lowered = incoming_msg.lower()

            if lowered in ["yes", "y", "ok", "sure"]:
                interview.status = "in_progress"
                interview.save()
                print("Interview started.")

                first_q = InterviewQuestion.objects.filter(
                    interview=interview,
                    sequence_number=1
                ).first()

                if not first_q:
                    resp.message("No questions configured. Please contact support.")
                    return HttpResponse(str(resp), content_type='application/xml')

                msg = f"Great! Let's begin.\n\n{first_q.question_text}"
                self._reply(resp, interview, msg, first_q)
                return HttpResponse(str(resp), content_type='application/xml')

            elif lowered in ["no", "n", "cancel", "stop"]:
                interview.status = "canceled"
                interview.save()
                print("Interview cancelled by user.")

                self._reply(resp, interview, "Interview cancelled. Have a great day!", None)
                return HttpResponse(str(resp), content_type='application/xml')

            else:
                print("Invalid reply for scheduled interview.")
                self._reply(resp, interview, "Please reply YES or NO.", None)
                return HttpResponse(str(resp), content_type='application/xml')

        # ============================================================
        # CASE 2 — INTERVIEW IN PROGRESS
        # ============================================================
        if interview.status == "in_progress":
            print("Interview in progress → parsing user's answer")

            current_seq = related_q.sequence_number if related_q else 0

            next_q = InterviewQuestion.objects.filter(
                interview=interview,
                sequence_number__gt=current_seq
            ).order_by('sequence_number').first()

            # --- Added Monitoring Override Logic ---
            if next_q and next_q.sequence_number == 4:
                if self._should_reschedule(interview):
                    cancel_msg = (
                        "It seems you may not be fully prepared today, so let's reschedule your interview. "
                        "You will be notified soon with the updated date. Thank you."
                    )
                    interview.status = "canceled"
                    interview.ended_at = timezone.now()
                    interview.save(update_fields=["status", "ended_at"])
                    self._reply(resp, interview, cancel_msg, None)
                    return HttpResponse(str(resp), content_type='application/xml')
            # --- End Added Logic ---

            if next_q:
                print("Sending next question:", next_q.sequence_number)
                self._reply(resp, interview, next_q.question_text, next_q)
                return HttpResponse(str(resp), content_type='application/xml')

            # No more questions → mark complete
            interview.status = "completed"
            interview.save()

            self._reply(resp, interview,
                        "Thank you! That was the last question. We will review your answers.",
                        None)
            return HttpResponse(str(resp), content_type='application/xml')

        print("Unexpected state.")
        resp.message("Unexpected error. Please try again.")
        return HttpResponse(str(resp), content_type='application/xml')

    # ============================================================
    # HELPER TO SEND OUTBOUND + SAVE
    # ============================================================
    def _reply(self, resp, interview, text, question):
        resp.message(text)
        SMSMessages.objects.create(
            interview=interview,
            direction='outbound',
            message_text=text,
            status='sent',
            related_question=question
        )

    # ============================================================
    # ADDED: Monitoring helper
    # ============================================================
    def _should_reschedule(self, interview):
        """
        Returns True if first three answered questions are all weak.
        Conditions:
          - Must have 3 inbound answers mapped to sequence 1..3
          - Each classified weak by heuristic/Gemini
        """
        inbound_first_three = (
            SMSMessages.objects.filter(
                interview=interview,
                direction='inbound',
                related_question__sequence_number__in=[1, 2, 3]
            )
            .select_related("related_question")
            .order_by("related_question__sequence_number")
        )

        # Ensure all three distinct question sequences answered
        sequences = {m.related_question.sequence_number for m in inbound_first_three if m.related_question}
        if sequences != {1, 2, 3}:
            return False

        # Classify each
        for msg in inbound_first_three:
            if not classify_answer_quality(msg.message_text):
                return False  # Any strong answer aborts reschedule
        return True
