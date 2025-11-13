from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Candidate, Resume
from .serializers import CandidateSerializer, ResumeSerializer
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10               # default if limit= is not provided
    page_size_query_param = 'limit'
    max_page_size = 100    


class CandidateListCreateView(ListCreateAPIView):
    queryset = Candidate.objects.all().order_by("-application_date")
    serializer_class = CandidateSerializer
    pagination_class = CustomPageNumberPagination

class CandidateRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    lookup_field = "pk"

class ResumeListCreateView(ListCreateAPIView):
    queryset = Resume.objects.all().order_by("-uploaded_at")
    serializer_class = ResumeSerializer
    pagination_class = CustomPageNumberPagination

class ResumeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    lookup_field = "pk"
