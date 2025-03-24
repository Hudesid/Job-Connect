from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from . import models
from apps.users.models import JobSeeker


class JopPostingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobPosting
        fields = ('id', 'title', 'location', 'job_type', 'experience_level', 'salary_min', 'salary_max', 'deadline', 'requirements', 'responsibilities', 'education_required', 'skills_required')


    def create(self, validated_data):
        from apps.users.models import Company
        company = Company.objects.get(user=self.context['request'].user)
        if company.is_active == False:
            raise serializers.ValidationError({"error": "Sizga tegishli kompaniya profile tasdiqlanmagan."})
        skills = validated_data.pop("skills_required", [])
        post = models.JobPosting.objects.create(company=company, **validated_data)
        post.skills_required.set(skills)
        post.save()
        return post


    def update(self, instance, validated_data):
        from apps.users.models import Company
        company = Company.objects.get(user=self.context['request'].user)
        if company.is_active == False:
            raise serializers.ValidationError({"error": "Sizga tegishli kompaniya profile tasdiqlanmagan."})
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.company = company
        instance.save()
        return instance


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from apps.skills.serializers import SkillSerializer
        from apps.users.serializers import CompanySerializer
        representation['company'] = CompanySerializer(instance.company).data
        representation['skills_required'] = SkillSerializer(instance.skills_required, many=True).data
        representation['posted_date'] = instance.posted_date
        representation['updated_at'] = instance.updated_at
        representation['views_count'] = instance.views_count
        representation['is_active'] = instance.is_active
        return representation


class JobApplicationSerializer(serializers.ModelSerializer):
    resume = serializers.FileField(validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])])

    class Meta:
        model = models.JobApplication
        fields = ('id', 'job_posting', 'status', 'cover_later', 'resume')


    def validate_resume(self, value):
        max_size = 5 * 1024 * 1024  # 5 MB
        if value and value.size > max_size:
            raise serializers.ValidationError({"error": "Resume 5 MB dan katta bo'lishi mumkin emas."})
        return value


    def create(self, validated_data):
        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        job_posting = models.JobPosting.objects.get(id=validated_data['job_posting'])
        if models.JobApplication.objects.filter(job_posting=validated_data['job_posting'], job_seeker=job_seeker).exists():
            raise serializers.ValidationError({"error": "Siz bu post ga alaqachon ariza topshirgansiz."})
        from apps.users.models import Company
        company = Company.objects.get(user=self.context['request'].user)
        if job_posting.company in company:
            raise serializers.ValidationError({"error": "Siz o'znigizni postingizga ariza bera olmaysiz."})
        job_application = models.JobApplication.objects.create(job_seeker=job_seeker, **validated_data)
        return job_application


    def update(self, instance, validated_data):
        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        if job_seeker == self.instance.job_seeker:
            status = validated_data.get('status')

            if status and status != self.instance.status:
                raise serializers.ValidationError({"error": "Sizga tegishli arizalarni statusini o'zgartirishga huquqingiz yo'q."})

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
        representation['job_posting'] = JopPostingSerializer(instance.job_posting).data
        from apps.users.serializers import JobSeekerSerializer
        representation['job_seeker'] = JobSeekerSerializer(instance.job_seeker).data
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
        representation['saved_date'] = instance.saved_date
        return representation


    def create(self, validated_data):
        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        saved_job = models.SavedJob.objects.create(job_seeker=job_seeker, **validated_data)
        return saved_job


    def update(self, instance, validated_data):

        for key, value in validated_data.items():
            setattr(instance, key, value)

        job_seeker = JobSeeker.objects.get(user=self.context['request'].user)
        instance.job_seeker = job_seeker
        instance.save()
        return instance

