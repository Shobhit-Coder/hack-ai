from django.urls import path
from . import views

urlpatterns = [
    path('', views.InterviewListCreateView.as_view(), name='interview-list-create'),
    path('<uuid:pk>', views.InterviewRetrieveUpdateDestroyView.as_view(), name='interview-detail'),
    # Interview Questions
    path('questions', views.InterviewQuestionListCreateView.as_view(), name='interviewquestion-list-create'),
    path('questions/<uuid:pk>', views.InterviewQuestionRetrieveUpdateDestroyView.as_view(), name='interviewquestion-detail'),
    # SMS Messages
    path('sms-messages', views.SMSMessagesListCreateView.as_view(), name='smsmessages-list-create'),
    path('sms-messages/<uuid:pk>', views.SMSMessagesRetrieveUpdateDestroyView.as_view(), name='smsmessages-detail'),
]
