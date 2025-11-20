from django.urls import path
from dashboard import views
from dashboard.views import DashboardDataAPIView

urlpatterns = [
    path("", DashboardDataAPIView.as_view(), name="dashboard-data"),
]
