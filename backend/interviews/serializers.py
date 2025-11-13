from rest_framework import serializers
from .models import Interview, InterviewQuestion, SMSMessages

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = "__all__"

class InterviewQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = "__all__"

class SMSMessagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSMessages
        fields = "__all__"
