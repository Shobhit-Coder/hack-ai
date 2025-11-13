# views.py
import numpy as np
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate
from django.db.models import Count, Avg, F

from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from jobs.models import Job
from interviews.models import Interview


class DashboardDataAPIView(ListAPIView):
    def list(self, request, *args, **kwargs):
        return Response({
            "job_status": self.get_job_status_data(),
            "category": self.get_category_data(),
            "metrics": self.get_metrics_data(),
        })

    # ------------------------------------------------
    # Job Status Data
    # ------------------------------------------------
    def get_job_status_data(self):
        last_dates = (
            Job.objects.annotate(day=TruncDate("created_at"))
            .order_by("-day")
            .values_list("day", flat=True)
            .distinct()[:7]
        )

        last_dates = sorted([d for d in last_dates if d])

        daily_data = []
        for date in last_dates:
            start = timezone.make_aware(datetime.combine(date, datetime.min.time()))
            end = start + timedelta(days=1)

            day_jobs = Job.objects.filter(created_at__gte=start, created_at__lt=end)
            total = day_jobs.count()
            closed = day_jobs.filter(job_status="closed").count()

            score = int((closed / total * 100)) if total > 0 else 0

            daily_data.append({
                "ts": date.strftime("%b %d"),
                "score": score
            })

        return daily_data

    # ------------------------------------------------
    # Category Data
    # ------------------------------------------------
    def get_category_data(self):
        category_counts = (
            Job.objects.values('category')
            .annotate(count=Count('category'))
            .order_by('-count')
        )

        return [
            {"name": item["category"], "value": item["count"]}
            for item in category_counts
        ]

    # ------------------------------------------------
    # Metrics Data
    # ------------------------------------------------
    def get_metrics_data(self):
        seven_days_ago = timezone.now() - timedelta(days=7)

        active_interviews = Interview.objects.filter(status='in_progress').count()

        avg_score = Interview.objects.filter(
            created_at__gte=seven_days_ago
        ).aggregate(avg=Avg('job_fit_score'))['avg']
        avg_score_7d = int(avg_score) if avg_score else 0

        total_interviews = Interview.objects.filter(created_at__gte=seven_days_ago).count()
        completed = Interview.objects.filter(
            created_at__gte=seven_days_ago,
            status='completed'
        ).count()

        completion_rate = int((completed / total_interviews * 100)) if total_interviews > 0 else 0

        completed_interviews = Interview.objects.filter(
            created_at__gte=seven_days_ago,
            status='completed',
            started_at__isnull=False,
            ended_at__isnull=False
        ).exclude(started_at__gt=F('ended_at'))

        durations = [
            (i.ended_at - i.started_at).total_seconds() / 60
            for i in completed_interviews
        ]

        median_time = int(np.median(durations)) if durations else 0

        return {
            "active_interviews": active_interviews,
            "average_score_7d": avg_score_7d,
            "completion_rate": completion_rate,
            "median_time_minutes": median_time
        }
