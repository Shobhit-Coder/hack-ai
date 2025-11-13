from django.contrib import admin
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'category', 'location', 'is_remote', 'job_status', 'posted_date')
    list_filter = ('category', 'is_remote', 'job_status', 'posted_date')
    search_fields = ('title', 'company_name', 'description')
    ordering = ('-posted_date',)
