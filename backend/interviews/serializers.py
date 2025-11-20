from rest_framework import serializers
from .models import Interview, InterviewQuestion, SMSMessages

class InterviewSerializer(serializers.ModelSerializer):
    candidate_name = serializers.SerializerMethodField()
    job_category = serializers.CharField(source='job.category', read_only=True)

    def get_candidate_name(self, obj):
        return f"{obj.candidate.first_name} {obj.candidate.last_name}"

    class Meta:
        model = Interview
        fields = "__all__"
        extra_fields = ['candidate_name', 'job_category']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['candidate_name'] = self.get_candidate_name(instance)
        data['job_category'] = instance.job.category if instance.job else None
        return data

class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = "__all__"

class SMSMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSMessages
        fields = "__all__"
