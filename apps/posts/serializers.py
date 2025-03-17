from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from . import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import JobSeeker


class JopPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobPosting
        fields = ('id', 'company', 'title', 'location', 'job_type', 'experience_level', 'salary_min', 'salary_max', 'deadline', 'requirements', 'responsibilities', 'education_required', 'skills_required')


    def perform_create(self, serializer):
        company = self.context['request'].user.company
        serializer.save(company=company)


    def perform_update(self, serializer):
        company = self.context['request'].user.company
        serializer.save(company=company)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from apps.users.serializers import CompanySerializer
        representation['company'] = CompanySerializer(instance.company).data
        representation['posted_date'] = instance.posted_date
        representation['updated_at'] = instance.updated_at
        representation['views_count'] = instance.views_count
        representation['is_active'] = instance.is_active
        return representation


class FileSizeValidator:
    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        if value.size > self.max_size:
            raise ValidationError(f"File size must not exceed {self.max_size / 1024 / 1024} MB.")


class JobApplicationSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'docx']),
            FileSizeValidator(max_size=5 * 1024 * 1024)
        ])

    class Meta:
        model = models.JobApplication
        fields = ('id', 'job_posting', 'status', 'cover_later', 'resume')


    def perform_create(self, serializer):
        job_seeker = self.context['request'].user.job_seeker
        if models.JobApplication.objects.filter(job_posting=self.instance.job_posting, job_seeker=job_seeker).exists():
            raise serializers.ValidationError(_("You have already applied for this job."))
        serializer.save(job_seeker=job_seeker)


    def update(self, instance, validated_data):
        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        if job_seeker == self.instance.job_seeker:
            status = validated_data.get('status')

            if status and status != self.instance.status:
                raise serializers.ValidationError(_("You can't replace status"))

            else:
                for key, value in validated_data.items():
                    setattr(instance, key, value)

                instance.job_seeker = job_seeker
                instance.save()

            return instance

        else:
            status = validated_data.get('status')
            instance.status = status
            instance.save()
            return instance


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['applied_date'] = instance.applied_date
        representation['updated_at'] = instance.updated_at
        return representation


class SavedJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SavedJob
        fields = ('id', 'job_posting')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from apps.users.serializers import JobSeekerSerializer
        representation['job_seeker'] = JobSeekerSerializer(instance.job_seeker).data
        representation['job_posting'] = JopPostingSerializer(instance.job_posting).data
        return representation

    def create(self, validated_data):
        saved_job = models.SavedJob.objects.create(**validated_data)
        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        saved_job.job_seeker = job_seeker
        saved_job.save()
        return saved_job

    def update(self, instance, validated_data):

        for key, value in validated_data.items():
            setattr(instance, key, value)

        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        instance.job_seeker = job_seeker
        instance.save()
        return instance

