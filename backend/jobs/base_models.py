from django.db import models

class TimestampedModel(models.Model):
    """
    Abstract base class that provides self-updating `created_at` and `modified_at` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
