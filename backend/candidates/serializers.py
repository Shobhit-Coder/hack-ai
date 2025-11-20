from rest_framework import serializers
from .models import Candidate, Resume
from jobs.models import Job

class CandidateSerializer(serializers.ModelSerializer):
    applied_job = serializers.PrimaryKeyRelatedField(
        queryset=Job.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Candidate
        fields = "__all__"

class ResumeSerializer(serializers.ModelSerializer):
    resume_job_score = serializers.FloatField(required=False, allow_null=True, min_value=0.0, max_value=100.0)

    class Meta:
        model = Resume
        fields = ['id', 'candidate', 'job', 'file', 'resume_text', 'parsed_data', 'resume_job_score', 'uploaded_at']
        read_only_fields = ['candidate', 'job', 'file', 'uploaded_at']