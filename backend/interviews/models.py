import uuid
from django.db import models
from interviews.base_models import TimestampedModel
from candidates.models import Candidate
from jobs.models import Job

class Interview(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interviews')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='interviews')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    job_fit_score = models.FloatField(null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=[
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
    ])

    def __str__(self):
        return f"{self.candidate} - {self.job} ({self.status})"


class InterviewQuestion(TimestampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='interview_questions', null=True, blank=True)
    question_text = models.TextField()
    question_type = models.CharField(max_length=50, choices=[
        ('technical', 'Technical'),
        ('behavioral', 'Behavioral'),
        ('experience', 'Experience'),
        ('other', 'Other'),
    ])
    sequence_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Question for {self.interview.candidate} - {self.question_text[:30]}..."


class SMSMessages(TimestampedModel):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name='sms_messages')
    direction = models.CharField(max_length=10, choices=[
        ('inbound', 'Inbound'),
        ('outbound', 'Outbound'),
    ])
    message_text = models.TextField()
    status = models.CharField(max_length=50, choices=[
        ('sent', 'Sent'),
        ('received', 'Received'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ])
    related_question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_messages'
    )

    def __str__(self):
        return f"SMS {self.direction} for Interview {self.interview}"

