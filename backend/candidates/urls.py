from django.urls import path
from . import views

urlpatterns = [
    path('', views.CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('<uuid:pk>', views.CandidateRetrieveUpdateDestroyView.as_view(), name='candidate-detail'),
    path('<uuid:pk>/', views.CandidateRetrieveUpdateDestroyView.as_view(), name='candidate-detail-slash'),
    # Resumes
    path('resumes', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('resumes/', views.ResumeListCreateView.as_view(), name='resume-list-create-slash'),
    path('resumes/<uuid:pk>', views.ResumeRetrieveUpdateDestroyView.as_view(), name='resume-detail'),
    path('resumes/<uuid:pk>/', views.ResumeRetrieveUpdateDestroyView.as_view(), name='resume-detail-slash'),
    path('resume/<uuid:pk>', views.ResumeRetrieveUpdateDestroyView.as_view(), name='resume-detail-alias'),
    path('resume/<uuid:pk>/', views.ResumeRetrieveUpdateDestroyView.as_view(), name='resume-detail-alias-slash'),
    path('resumes/<uuid:pk>/job-info', views.ResumeJobInfoView.as_view(), name='resume-job-info'),
    path('resumes/<uuid:pk>/job-info/', views.ResumeJobInfoView.as_view(), name='resume-job-info-slash'),
]
