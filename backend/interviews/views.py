import os
import requests
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from twilio.rest import Client
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListAPIView ,ListCreateAPIView, RetrieveUpdateDestroyAPIView
from interviews.models import Interview, InterviewQuestion, SMSMessages
from interviews.serializers import InterviewSerializer, InterviewQuestionSerializer, SMSMessagesSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from candidates.models import Candidate

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10               # default if limit= is not provided
    page_size_query_param = 'page_size'
    max_page_size = 100    


class InterviewListCreateView(ListCreateAPIView):
    queryset = Interview.objects.all().order_by("-created_at")
    serializer_class = InterviewSerializer
    pagination_class = CustomPageNumberPagination
    

class InterviewRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Interview.objects.all().prefetch_related('sms_messages')
    serializer_class = InterviewSerializer
    lookup_field = "pk"

    def retrieve(self, request, *args, **kwargs):
        """
        Return interview data plus all related SMS messages.
        """
        interview = self.get_object()
        interview_data = self.get_serializer(interview).data
        messages_qs = interview.sms_messages.all().order_by('-created_at')
        messages_data = SMSMessagesSerializer(messages_qs, many=True).data
        return Response({
            "interview": interview_data,
            "messages": messages_data
        })

class InterviewQuestionListCreateView(ListCreateAPIView):
    serializer_class = InterviewQuestionSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = InterviewQuestion.objects.all().order_by("-created_at")
        candidate_id = self.kwargs.get("candidate_id")
        return queryset.filter(candidate_id=candidate_id) if candidate_id else queryset

    def perform_create(self, serializer):
        candidate_id = self.kwargs.get("candidate_id")
        if not candidate_id:
            raise ValidationError({"candidate_id": "Candidate ID must be supplied in the URL."})
        candidate = get_object_or_404(Candidate, pk=candidate_id)
        serializer.save(candidate=candidate)

class InterviewQuestionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = InterviewQuestion.objects.all()
    serializer_class = InterviewQuestionSerializer
    lookup_field = "pk"

class SMSMessagesListCreateView(ListAPIView):
    queryset = SMSMessages.objects.all().order_by("-created_at")
    serializer_class = SMSMessagesSerializer
    pagination_class = CustomPageNumberPagination

class SMSMessagesRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SMSMessages.objects.all()
    serializer_class = SMSMessagesSerializer
    lookup_field = "pk"

class StartInterviewView(APIView):
    """
    Call this API to trigger the initial SMS:
    "Would you like to start the interview?"
    """
    def post(self, request, pk):
        # 1. Fetch the Interview
        interview = get_object_or_404(Interview, pk=pk)
        
        # Validation: Only start if it's scheduled
        if interview.status != 'scheduled':
            return Response(
                {"detail": f"Cannot start interview. Current status is {interview.status}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set scheduled_at now and move to in_progress
        interview.scheduled_at = timezone.now()
        interview.started_at = interview.scheduled_at
        interview.save(update_fields=["scheduled_at", "started_at"])

        candidate = interview.candidate
        
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
            return Response({"detail": "Twilio credentials missing"}, status=500)

        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

        # 3. Prepare the Initial Message
        initial_message = f"Hi {candidate.first_name}, this is the automated interview assistant. Would you like to start your interview now? (Reply Yes/No)"

        try:
            # 4. Send via Twilio API
            message = client.messages.create(
                body=initial_message,
                from_=TWILIO_PHONE_NUMBER,
                to=candidate.phone_number
            )
            
            # 5. Record the Outbound SMS in DB
            # Note: related_question is None because this is the preamble
            SMSMessages.objects.create(
                interview=interview,
                direction='outbound',
                message_text=initial_message,
                status='sent',
                related_question=None 
            )

            return Response({
                "detail": "Invitation sent successfully", 
                "twilio_sid": message.sid
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

