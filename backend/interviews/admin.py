from django.contrib import admin
from .models import Interview, InterviewQuestion, SMSMessages

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('candidate', 'job', 'scheduled_at', 'status')
    list_filter = ('status', 'scheduled_at')
    search_fields = ('candidate__first_name', 'candidate__last_name', 'job__title')
    ordering = ('-scheduled_at',)

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('interview', 'question_text', 'question_type')
    list_filter = ('question_type',)
    search_fields = ('question_text', 'interview__candidate__first_name', 'interview__candidate__last_name')
    ordering = ('interview',)

@admin.register(SMSMessages)
class SMSMessagesAdmin(admin.ModelAdmin):
    list_display = ('interview', 'direction', 'status', 'message_text')
    list_filter = ('direction', 'status')
    search_fields = ('message_text', 'interview__candidate__first_name', 'interview__candidate__last_name')
    ordering = ('-created_at',)
