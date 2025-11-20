from django.urls import path
from jobs import views

urlpatterns = [
    path('', views.JobListCreateView.as_view(), name='job-list-create'),
    path('<uuid:pk>', views.JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
    path('categories', views.JobCategoryListView.as_view(), name='job-category-list'),
]
