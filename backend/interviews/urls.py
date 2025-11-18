from django.urls import path
from interviews import views
from interviews.webhook import IncomingSMSWebhookView

urlpatterns = [
    path('', views.InterviewListCreateView.as_view(), name='interview-list-create'),
    path('<uuid:pk>', views.InterviewRetrieveUpdateDestroyView.as_view(), name='interview-detail'),
    # Interview Questions
    path('questions', views.InterviewQuestionListCreateView.as_view(), name='interviewquestion-list-create'),
    path('questions/<uuid:pk>', views.InterviewQuestionRetrieveUpdateDestroyView.as_view(), name='interviewquestion-detail'),
    # SMS Messages
    path('sms-messages', views.SMSMessagesListCreateView.as_view(), name='smsmessages-list-create'),
    path('sms-messages/<uuid:pk>', views.SMSMessagesRetrieveUpdateDestroyView.as_view(), name='smsmessages-detail'),
    path('webhook', IncomingSMSWebhookView.as_view(), name='incoming-sms-webhook'),
    path('<uuid:pk>/start', views.StartInterviewView.as_view(), name='start_interview'),
]
