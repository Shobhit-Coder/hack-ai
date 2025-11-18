from django.urls import path
from . import views

urlpatterns = [
    path('', views.CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<uuid:pk>', views.CandidateRetrieveUpdateDestroyView.as_view(), name='candidate-detail'),
    # Resumes
    path('resumes', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('resumes/<uuid:pk>', views.ResumeRetrieveUpdateDestroyView.as_view(), name='resume-detail'),
    path('resumes/<uuid:pk>/job-info', views.ResumeJobInfoView.as_view(), name='resume-job-info'),
]
