import numpy as np
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.db.models import Count, Avg, F
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from jobs.models import Job
from interviews.models import Interview
from dashboard.serializers import JobStatusDataSerializer, CategoryDataSerializer, MetricsDataSerializer


class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'limit'

class JobStatusDataAPIView(ListAPIView):
    serializer_class = JobStatusDataSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        last_dates = (
            Job.objects
               .annotate(day=TruncDate("created_at"))
               .order_by("-day")
               .values_list("day", flat=True)
               .distinct()[:7]
        )

        last_dates = sorted([d for d in last_dates if d])

        daily_data = []

        for date in last_dates:
            # Calculate start and end of day
            start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end = start + timedelta(days=1)

            day_jobs = Job.objects.filter(
                created_at__gte=start,
                created_at__lt=end
            )

            total_jobs = day_jobs.count()
            closed_jobs = day_jobs.filter(job_status="closed").count()

            score = int((closed_jobs / total_jobs * 100)) if total_jobs > 0 else 0
            ts = date.strftime("%b %d")

            daily_data.append({
                "ts": ts,
                "score": score
            })

        return daily_data

class CategoryDataAPIView(ListAPIView):
    serializer_class = CategoryDataSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        category_counts = Job.objects.values('category').annotate(
            count=Count('category')
        ).order_by('-count')

        data = [
            {'name': item['category'], 'value': item['count']}
            for item in category_counts
        ]
        return data

class MetricsDataAPIView(ListAPIView):
    serializer_class = MetricsDataSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        active_interviews = Interview.objects.filter(status='in_progress').count()

        seven_days_ago = timezone.now() - timedelta(days=7)

        avg_score = Interview.objects.filter(
            created_at__gte=seven_days_ago
        ).aggregate(avg=Avg('job_fit_score'))['avg']

        average_score_7d = int(avg_score) if avg_score else 0

        total_interviews = Interview.objects.filter(
            created_at__gte=seven_days_ago
        ).count()

        completed_interviews = Interview.objects.filter(
            created_at__gte=seven_days_ago,
            status='completed'
        ).count()

        completion_rate = int((completed_interviews / total_interviews * 100)) if total_interviews > 0 else 0

        completed_interviews_with_time = Interview.objects.filter(
            created_at__gte=seven_days_ago,
            status='completed',
            started_at__isnull=False,
            ended_at__isnull=False
        ).exclude(started_at__gt=F('ended_at'))

        time_differences = []
        for interview in completed_interviews_with_time:
            time_diff = interview.ended_at - interview.started_at
            time_differences.append(time_diff.total_seconds() / 60)

        if time_differences:
            median_time_minutes = int(np.median(time_differences))
        else:
            median_time_minutes = 0

        data = {
            'active_interviews': active_interviews,
            'average_score_7d': average_score_7d,
            'completion_rate': completion_rate,
            'median_time_minutes': median_time_minutes
        }

        return [data]

