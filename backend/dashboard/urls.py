from django.urls import path
from dashboard import views

urlpatterns = [
    path('job-status-data', views.JobStatusDataAPIView.as_view(), name='job-status-data'),
    path('category-data', views.CategoryDataAPIView.as_view(), name='category-data'),
    path('metrics-data', views.MetricsDataAPIView.as_view(), name='metrics-data'),
]
