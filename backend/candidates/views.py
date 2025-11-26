import os
from datetime import datetime
from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from jobs.models import Job
from candidates.models import Candidate, Resume
from candidates.serializers import CandidateSerializer, ResumeSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers

from candidates.azure_storage_utils import upload_file_to_azure_blob 
from rest_framework.parsers import MultiPartParser, FormParser


BLOB_CONTAINER_NAME = "hackai"

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10               # default if limit= is not provided
    page_size_query_param = 'page_size'
    max_page_size = 100    


class CandidateListCreateView(ListCreateAPIView):
    queryset = Candidate.objects.all().order_by("-application_date")
    serializer_class = CandidateSerializer
    pagination_class = CustomPageNumberPagination

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            candidate = serializer.save()
        except IntegrityError as exc:
            raise serializers.ValidationError({"detail": "Candidate creation failed. Ensure the email is unique and data is valid."}) from exc
        except Exception as exc:
            # Ensure 4xx instead of 500 for any unexpected validation issues
            raise serializers.ValidationError({"detail": "Candidate creation failed.", "error": str(exc)})
        return Response({"candidate_id": str(candidate.id)}, status=201)

class CandidateRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    lookup_field = "pk"

class ResumeListCreateView(ListCreateAPIView):
    queryset = Resume.objects.all().order_by("-uploaded_at")
    serializer_class = ResumeSerializer
    pagination_class = CustomPageNumberPagination
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        """
        Upload resume into 'resumes/' folder.
        File name format:
        <resume_id>.<extension>
        """

        # 1. Validate resume file
        file_obj = self.request.FILES.get("file")
        if not file_obj:
            raise serializers.ValidationError({"file": "Resume file is required."})

        # 2. Validate job_id
        job_id = self.request.data.get("job_id")
        if not job_id:
            raise serializers.ValidationError({"job_id": "job_id is required."})

        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            raise serializers.ValidationError({"job_id": "Invalid job_id."})

        # 3. Save resume FIRST (empty file) to generate resume_id
        resume_instance = serializer.save(job=job)

        resume_id = str(resume_instance.id)

        # 4. Prepare filename
        _, file_extension = os.path.splitext(file_obj.name)
        if not file_extension:
            file_extension = ".pdf"

        filename = f"{resume_id}{file_extension}".replace(" ", "_")

        # 5. Blob upload path
        blob_path = f"resumes/{filename}"

        # 6. Upload to Azure Blob Storage
        try:
            blob_url = upload_file_to_azure_blob(
                file_obj=file_obj,
                container_name=BLOB_CONTAINER_NAME,
                blob_name=blob_path
            )
        except Exception as e:
            raise serializers.ValidationError({"file": f"Azure upload failed: {e}"})

        # 7. Save filename in DB
        resume_instance.file = filename
        resume_instance.save()

class ResumeRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    lookup_field = "pk"

class ResumeJobInfoView(APIView):
    def get(self, request, pk):
        resume = get_object_or_404(Resume, pk=pk)
        if not resume.job:
            return Response({"detail": "Job not linked to this resume."}, status=404)
        job = resume.job
        return Response({
            "resume_id": str(resume.id),
            "job_id": str(job.id),
            "job_description": job.description
        })


