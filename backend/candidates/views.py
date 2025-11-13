from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Candidate, Resume
from .serializers import CandidateSerializer, ResumeSerializer


class CandidateListCreateView(ListCreateAPIView):
    queryset = Candidate.objects.all().order_by("-application_date")
    serializer_class = CandidateSerializer

class CandidateRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    lookup_field = "pk"

class ResumeListCreateView(ListCreateAPIView):
    queryset = Resume.objects.all().order_by("-uploaded_at")
    serializer_class = ResumeSerializer

class ResumeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    lookup_field = "pk"
