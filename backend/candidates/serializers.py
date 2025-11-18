from rest_framework import serializers
from .models import Candidate, Resume

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = "__all__"

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'candidate', 'file', 'resume_text', 'parsed_data', 'uploaded_at']
        read_only_fields = ['candidate', 'file', 'uploaded_at']