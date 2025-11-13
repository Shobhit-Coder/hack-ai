from django.urls import path
from . import views

urlpatterns = [
    path('create-candidates', views.CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('update-candidates/<uuid:pk>', views.CandidateRetrieveUpdateDestroyView.as_view(), name='candidate-detail'),
    # Resumes
    path('create-resumes', views.ResumeListCreateView.as_view(), name='resume-list-create'),
    path('update-resumes/<uuid:pk>', views.ResumeRetrieveUpdateDestroyView.as_view(), name='resume-detail'),
]
