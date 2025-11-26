import uuid
from django.db import models
from jobs.base_models import TimestampedModel

class Job(TimestampedModel):
    """
    Model representing a job posting.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100)
    description = models.TextField()
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    is_remote = models.BooleanField(default=False)
    posted_date = models.DateTimeField(auto_now_add=True)
    application_deadline = models.DateTimeField(null=True, blank=True)
    job_status = models.CharField(
        max_length=50,
        choices=[
            ('open', 'Open'),
            ('closed', 'Closed'),
            ('paused', 'Paused')
        ],
        default='open'
    )

    def __str__(self):
        return f"{self.title} at {self.company_name}"


