from django.urls import path
from . import views

urlpatterns = [
    path('jobs-create', views.JobListCreateView.as_view(), name='job-list-create'),
    path('update-jobs/<uuid:pk>', views.JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
]
