from django.contrib import admin

from .models import JobApplication, JobPosting, SavedJob


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'job_type', 'salary_max', 'salary_min', 'is_active', 'deadline')
    list_filter = ('job_type', 'salary_max', 'salary_min', 'is_active', 'deadline', 'experience_level', 'education_required', 'posted_date', 'updated_at', 'views_count', "skills_required")
    search_fields = ('id', 'title', 'company__name')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'applied_date', 'updated_at')
    list_filter = ('status', 'applied_date', 'updated_at')


@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'saved_date')
    list_filter = ('saved_date',)
