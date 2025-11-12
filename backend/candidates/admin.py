from django.contrib import admin
from .models import Candidate, Resume

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'applied_job', 'status', 'application_date')
    list_filter = ('status', 'applied_job', 'application_date')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('-application_date',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('candidate__first_name', 'candidate__last_name', 'candidate__email')
    ordering = ('-uploaded_at',)
