from django.urls import path
from . import views

urlpatterns = [
    path('create-interviews', views.InterviewListCreateView.as_view(), name='interview-list-create'),
    path('update-interviews/<uuid:pk>', views.InterviewRetrieveUpdateDestroyView.as_view(), name='interview-detail'),
    # Interview Questions
    path('create-questions', views.InterviewQuestionListCreateView.as_view(), name='interviewquestion-list-create'),
    path('update-questions/<uuid:pk>', views.InterviewQuestionRetrieveUpdateDestroyView.as_view(), name='interviewquestion-detail'),
    # SMS Messages
    path('create-sms-messages', views.SMSMessagesListCreateView.as_view(), name='smsmessages-list-create'),
    path('update-sms-messages/<uuid:pk>', views.SMSMessagesRetrieveUpdateDestroyView.as_view(), name='smsmessages-detail'),
]
