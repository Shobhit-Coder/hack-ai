import logging
from rest_framework.views import APIView
from django.http import HttpResponse
from twilio.twiml.messaging_response import MessagingResponse
from interviews.models import Interview, InterviewQuestion, SMSMessages
from candidates.models import Candidate

logger = logging.getLogger(__name__)

class IncomingSMSWebhookView(APIView):
    """
    Handles incoming SMS webhooks from Twilio.
    1. Identifies Candidate & Active Interview.
    2. Saves the Incoming SMS (linking it to the previous question if possible).
    3. Logic:
       - If Scheduled + 'Yes': Start Interview (Send Q1).
       - If Scheduled + 'No': Cancel/Exit.
       - If In Progress: Save Answer -> Find Next Sequence -> Send Next Question.
    """
    
    def post(self, request, *args, **kwargs):
        # 1. Parse Twilio Payload
        data = request.POST 
        incoming_msg = data.get('Body', '').strip()
        sender_phone = data.get('From', '') 
        
        logger.info(f"Incoming SMS from {sender_phone}: {incoming_msg}")

        resp = MessagingResponse()

        # 2. Validate Candidate and Interview
        candidate = Candidate.objects.filter(phone_number=sender_phone).first()
        
        if not candidate:
            # If unknown number, ignore or send generic help
            resp.message("We could not find an application linked to this phone number.")
            return HttpResponse(str(resp), content_type='application/xml')

        # Look for an interview that is Scheduled or In Progress
        active_interview = Interview.objects.filter(
            candidate=candidate, 
            status__in=['scheduled', 'in_progress']
        ).first()

        if not active_interview:
            # No active session, silent fail or polite generic msg
            resp.message(f"Hi {candidate.first_name}, you don't have an active interview session at the moment.")
            return HttpResponse(str(resp), content_type='application/xml')

        # 3. Save the Incoming Message (The Answer)
        # We try to find the question this message is answering by looking at the last Outbound SMS
        last_outbound_sms = SMSMessages.objects.filter(
            interview=active_interview, 
            direction='outbound'
        ).order_by('-created_at').first()
        
        related_q = last_outbound_sms.related_question if last_outbound_sms else None

        SMSMessages.objects.create(
            interview=active_interview,
            direction='inbound',
            message_text=incoming_msg,
            status='received',
            related_question=related_q
        )

        # 4. Core Logic Flow
        
        # --- CASE A: INTERVIEW IS SCHEDULED (Waiting for User Confirmation) ---
        if active_interview.status == 'scheduled':
            if incoming_msg.lower() in ['yes', 'y', 'sure', 'ok']:
                # User said YES. Start the interview.
                active_interview.status = 'in_progress'
                active_interview.save()
                
                # Find Question with sequence_number = 1
                first_question = InterviewQuestion.objects.filter(
                    interview=active_interview, 
                    sequence_number=1
                ).first()
                
                if first_question:
                    msg_text = f"Great! Let's begin.\n\n{first_question.question_text}"
                    self._save_and_reply(resp, active_interview, msg_text, first_question)
                else:
                    # Error handling if no questions exist
                    self._save_and_reply(resp, active_interview, "System Error: No questions configured for this interview.", None)
            
            elif incoming_msg.lower() in ['no', 'n', 'stop', 'cancel']:
                # User said NO.
                active_interview.status = 'canceled'
                active_interview.save()
                self._save_and_reply(resp, active_interview, "Understood. We have canceled the interview session. Have a great day.", None)
            
            else:
                # User said something else (e.g., "Who is this?")
                self._save_and_reply(resp, active_interview, "Please reply 'Yes' to start the interview or 'No' to cancel.", None)


        # --- CASE B: INTERVIEW IS IN PROGRESS (Answering Questions) ---
        elif active_interview.status == 'in_progress':
            # The incoming message was the ANSWER to 'related_q' (calculated above).
            
            current_seq = 0
            if related_q:
                current_seq = related_q.sequence_number
            
            # Find the NEXT question (Sequence > Current Sequence)
            next_question = InterviewQuestion.objects.filter(
                interview=active_interview,
                sequence_number__gt=current_seq
            ).order_by('sequence_number').first()

            if next_question:
                # Ask the next question
                self._save_and_reply(resp, active_interview, next_question.question_text, next_question)
            else:
                # No more questions found. Interview Complete.
                active_interview.status = 'completed'
                active_interview.save()
                msg_text = "Thank you! That was the last question. We will review your answers and get back to you shortly."
                self._save_and_reply(resp, active_interview, msg_text, None)

        return HttpResponse(str(resp), content_type='application/xml')

    def _save_and_reply(self, resp_obj, interview, text, question_obj):
        """
        Helper: Adds text to Twilio response AND saves it to DB as outbound.
        """
        # 1. Add to TwiML response (This sends the SMS)
        resp_obj.message(text)
        
        # 2. Save record to DB
        SMSMessages.objects.create(
            interview=interview,
            direction='outbound',
            message_text=text,
            status='sent',
            related_question=question_obj
        )


