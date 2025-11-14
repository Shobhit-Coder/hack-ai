from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Interview, InterviewQuestion, SMSMessages
from .serializers import InterviewSerializer, InterviewQuestionSerializer, SMSMessagesSerializer
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10               # default if limit= is not provided
    page_size_query_param = 'limit'
    max_page_size = 100    


class InterviewListCreateView(ListCreateAPIView):
    queryset = Interview.objects.all().order_by("-created_at")
    serializer_class = InterviewSerializer
    pagination_class = CustomPageNumberPagination
    

class InterviewRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Interview.objects.all()
    serializer_class = InterviewSerializer
    lookup_field = "pk"

class InterviewQuestionListCreateView(ListCreateAPIView):
    queryset = InterviewQuestion.objects.all().order_by("-created_at")
    serializer_class = InterviewQuestionSerializer
    pagination_class = CustomPageNumberPagination

class InterviewQuestionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = InterviewQuestion.objects.all()
    serializer_class = InterviewQuestionSerializer
    lookup_field = "pk"

class SMSMessagesListCreateView(ListCreateAPIView):
    queryset = SMSMessages.objects.all().order_by("-created_at")
    serializer_class = SMSMessagesSerializer
    pagination_class = CustomPageNumberPagination

class SMSMessagesRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = SMSMessages.objects.all()
    serializer_class = SMSMessagesSerializer
    lookup_field = "pk"
