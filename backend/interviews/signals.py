from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from interviews.models import Interview
from interviews.tasks import queue_interview_analysis

@receiver(post_save, sender=Interview)
def trigger_analysis_on_completion(sender, instance, created, **kwargs):
    if instance.status != "completed":
        return

    # Ensure ended_at is set when interview completes (avoid recursive signal)
    if not instance.ended_at:
        Interview.objects.filter(pk=instance.id).update(ended_at=timezone.now())

    if instance.job_fit_score is not None:
        return

    queue_interview_analysis(instance.id)
