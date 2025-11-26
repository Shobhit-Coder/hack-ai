from rest_framework import serializers

class JobStatusDataSerializer(serializers.Serializer):
    ts = serializers.CharField()
    score = serializers.IntegerField()

class CategoryDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    value = serializers.IntegerField()

class MetricsDataSerializer(serializers.Serializer):
    active_interviews = serializers.IntegerField()
    average_score_7d = serializers.IntegerField()
    completion_rate = serializers.IntegerField()
    median_time_minutes = serializers.IntegerField()
