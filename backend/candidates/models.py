import uuid
from datetime import datetime 
from django.db import models
from candidates.base_models import TimestampedModel
from jobs.models import Job

class Candidate(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=100, blank=True, null=True, default='Applicant')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    applied_job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applicants'
    )
    application_date = models.DateTimeField(default=datetime.now)
    status = models.CharField(
        max_length=50,
        choices=[
            ('applied', 'Applied'),
            ('interviewing', 'Interviewing'),
            ('offered', 'Offered'),
            ('hired', 'Hired'),
            ('rejected', 'Rejected'),
        ],
        default='applied'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status}"


class Resume(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='resumes', null=True, blank=True)
    job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.CharField(max_length=512)
    resume_text = models.TextField(blank=True, null=True)
    parsed_data = models.JSONField(blank=True, null=True)
    resume_job_score = models.FloatField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume of {self.candidate.first_name} {self.candidate.last_name}"

