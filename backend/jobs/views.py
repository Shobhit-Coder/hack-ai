from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Job
from .serializers import JobSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "results": data,
            "total": self.page.paginator.count,
            "page": self.page.number,
            "page_size": self.get_page_size(self.request),
            "total_pages": self.page.paginator.num_pages,
        })


class JobListCreateView(ListCreateAPIView):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    pagination_class = CustomPageNumberPagination

class JobRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = "pk"

class JobCategoryListView(APIView):
    def get(self, request):
        categories = sorted(Job.objects.values_list('category', flat=True).distinct())
        return Response({"categories": categories})

