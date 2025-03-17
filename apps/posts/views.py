from datetime import timedelta
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework.generics import CreateAPIView, UpdateAPIView, DestroyAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from . import serializers, models, paginations, tasks
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.models import JobSeeker,Company
from apps.skills.models import Skill


class CompanyActiveBasePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        company = Company.objects.filter(user=request.user)
        if company is not None and company.is_active:
            return True
        else:
            return False



class JobPostingCreateAPIView(CreateAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    permission_classes = [IsAuthenticated, CompanyActiveBasePermission]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            tasks.new_posting_notification.delay(post.id, post.title, post.company.id)
            return Response({
                "status": True,
                "message": "Vakansiya muvaffaqiyatli e'lon qilindi.",
                "data": {post}
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "status": False,
                "error": "Noto'g'ri ma'lumot kiritlgan."
            }, status=status.HTTP_400_BAD_REQUEST)


class JobPostingListAPIView(ListAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['posted_date', 'deadline']
    ordering = ['is_active']
    filterset_fields = [
        'company',
        'location',
        'job_type',
        'experience_level'
        'education_required',
        'salary_min',
        'salary_max',
        'deadline',
        'views_count',
        'is_active'
    ]
    search_fields = ['title', 'company', 'location']


    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        return Response({
            "status": True,
            "message": "Vakansiyalar ro'yxati muvaffaqiyatli olindi.",
            "data": {response.data['results']}
        }, status=status.HTTP_200_OK)


class JobPostingRetrieveAPIView(RetrieveAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    permission_classes = [IsAuthenticated]


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        viewed_jobs = request.session.get('viewed_jobs', [])

        if instance.id not in viewed_jobs:
            viewed_jobs.add(instance.id)
            request.session['viewed_jobs'] = viewed_jobs

        post = self.get_serializer(instance).data
        return Response({
            "status": True,
            "message": "Vakansiya ma'lumotlari muvaffaqiyatli olindi.",
            "data": {post}
        }, status=status.HTTP_200_OK)


class JobPostingRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    permission_classes = [IsAuthenticated]

    def test_func(self):
        post = self.get_object()
        return post.company.user == self.request.user


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        post = self.get_serializer(instance).data
        return Response({
            "status": True,
            "message": "Vakansiya ma'lumotlari muvaffaqiyatli olindi.",
            "data": {post}
        }, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            return Response({
                "status": True,
                "message": "Vakansiya ma'lumotlari muvaffaqiyatli yangilandi.",
                "data": {post}
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": True,
                "errors": "Noto'g'ri ma'lumotlar kiritilgan."
            }, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            "status": True,
            "message": "Vakansiya muvaffaqiyatli o'chirildi."
        }, status=status.HTTP_200_OK)


class JobPostingRecommendedListAPIView(ListAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title', 'company']
    ordering_fields = ['deadline', 'posted_date']
    ordering = ['is_active']
    filterset_fields = [
        'company',
        'location',
        'job_type',
        'experience_level'
        'education_required',
        'salary_min',
        'salary_max',
        'deadline',
        'views_count',
        'is_active'
    ]

    def get_queryset(self):
        viewed_jobs_ids = self.request.session.get("viewed_jobs", [])

        if not viewed_jobs_ids:
            user = JobSeeker.objects.get(user=self.request.user)
            posts = models.JobPosting.objects.filter(skills_required=user.skills)
            posts_data = self.get_serializer(posts, many=True).data
            return Response({
                "status": True,
                "message": "Tavsiya etilgan vakansiyalar muvaffaqiyatli olindi.",
                "data": {posts_data}
            }, status=status.HTTP_200_OK)

        else:
            viewed_jobs = models.JobPosting.objects.filter(id__in=viewed_jobs_ids)
            viewed_job_skills = set()
            for job in viewed_jobs:
                for skill in job.skills_required.all():
                    viewed_job_skills.add(skill)

            return models.JobPosting.objects.filter(skills_required__in=viewed_job_skills)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True).data
        return Response({
            "status": True,
            "message": "Tavsiya etilgan vakansiyalar muvaffaqiyatli olindi.",
            "data": {serializer}
        }, status=status.HTTP_200_OK)


class JobApplicationListCreateAPIView(ListCreateAPIView, UserPassesTestMixin):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['job_posting__title']
    ordering_fields = ['applied_date', 'updated_at']
    ordering = ['status']
    filterset_fields = ['status']


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job_application = serializer.save()
            job_application_data = self.get_serializer(job_application).data
            return Response({
                "status": True,
                "message": "Ariza muvaffaqiyatli topshirildi.",
                "data": {job_application_data}
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "status": False,
                "message": "Ariza topshirishda xatolik yuz berdi.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


    def get_object(self):
        try:
            job_seeker = JobSeeker.objects.get(user=self.request.user)
            return models.JobApplication.objects.filter(job_seeker=job_seeker)

        except JobSeeker.DoesNotExist:
            return models.JobApplication.objects.none()


    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        return Response({
            "status": True,
            "message": "Arizalar ro'yxati muvaffaqiyatli olindi.",
            "data": {response.data}
        }, status=status.HTTP_200_OK)


    def test_func(self):
        job_application = self.get_object()
        job_seeker = JobSeeker.objects.get(user=self.request.user)
        if isinstance(job_application, models.QuerySet):
            return job_application.filter(job_seeker=job_seeker).exists()

        return job_application.job_seeker == job_seeker


class JobApplicationRetrieveAPIView(RetrieveAPIView):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        job_application_data = self.get_serializer(instance).data
        return Response({
            "status": True,
            "message": "Ariza ma'lumotlari muvaffaqiyatli olindi.",
            "data": {job_application_data}
        }, status=status.HTTP_200_OK)


class JobApplicationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        job_application_data = self.get_serializer(instance).data
        return Response({
            "status": True,
            "message": "Ariza ma'lumotlari muvaffaqiyatli olindi.",
            "data": {job_application_data}
        }, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job_application = serializer.save()
            job_application_data = self.get_serializer(job_application).data
            return Response({
                "status": True,
                "message": "Ariza muvaffaqiyatli yangilandi.",
                "data": {job_application_data}
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": False,
                "message": "Noto'g'ri ma'lumot kiritilgan",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            "status": True,
            "message": "Ariza muvaffaqiyatli o'chirildi."
        }, status=status.HTTP_200_OK)


class JobApplicationUpdateAPIView(UpdateAPIView, UserPassesTestMixin):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated, CompanyActiveBasePermission]


    def test_func(self):
        job_application = self.get_object()
        company = Company.objects.filter(user=self.request.user)
        exist = company.filter(job_posts__in=job_application.job_posting)

        if exist.exists():
            return True
        else:
            return False


    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job_application = serializer.save()
            tasks.update_status_application_notification.delay(request.user.id, job_application.id, job_application.job_posting.title)
            return Response({
                "status": True,
                "message": "Ariza statusi muvaffaqiyatli o'zgartirildi.",
                "data": {
                    "id": job_application.id,
                    "status": job_application.status,
                    "updated_date": job_application.updated_at
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": False,
                "message": "Noto'g'ri ma'lumot kiritilgan.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class JobPostingApplicationListAPIView(ListAPIView, UserPassesTestMixin):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['job_posting__title']
    ordering_fields = ['applied_date', 'updated_at']
    ordering = ['status']
    filterset_fields = ['status']


    def test_func(self):
        company = Company.objects.get(user=self.request.user)
        if self.get_queryset().filter(job_posting__company=company).exists():
            return True
        raise False


    def get_queryset(self):
        post = models.JobPosting.objects.get(id=self.kwargs['id'])
        if not post:
            return Response({
                "status": False,
                "message": "Noto'g'ri ID kiritilgan"
            }, status=status.HTTP_400_BAD_REQUEST)
        return models.JobApplication.objects.filter(job_posting=post)


    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True).data
        return Response({
            "status": True,
            "message": "Vakansiyaga kelib tushgan arizalar ro'yxati muvaffaqiyali olindi.",
            "data": {serializer}
        }, status=status.HTTP_200_OK)


class SavedJobListAPIView(ListAPIView):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['job_posting__title']
    ordering_fields = ['saved_date']


    def list(self, request, *args, **kwargs):
        job_seeker = JobSeeker.objects.get(user=self.request.user)
        queryset = self.get_queryset().filter(job_seeker=job_seeker)
        serializer = self.get_serializer(queryset, many=True).data
        return Response({
            "status": True,
            "message": "Saqlangan vakansiyalar ro'yxati olindi.",
            "data": {serializer}
        }, status=status.HTTP_200_OK)


class SavedJobCreateAPIView(CreateAPIView):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer
    permission_classes = [IsAuthenticated]


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            job = serializer.save()
            job_data = self.get_serializer(job).data
            return Response({
                "status": True,
                "message": "Vakansiya muvaffaqiyatli saqlandi.",
                "data": {job_data}
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "status": False,
                "message": "Noto'g'ri ma'lumot kiritilgan.",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class SavedJobDestroyAPIView(DestroyAPIView, UserPassesTestMixin):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer
    permission_classes = [IsAuthenticated]


    def test_func(self):
        job = self.get_object()
        user = JobSeeker.objects.get(user=self.request.user)
        return job.job_seeker == user


    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({
            "status": True,
            "message": "Saqlangan vakansiya muvaffaqiyatli o'chirildi.",
            "data": {instance}
        }, status=status.HTTP_200_OK)


class JobPostingStatsListAPIView(ListAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    permission_classes = [IsAuthenticated]


    def list(self, request, *args, **kwargs):
        posts = self.get_queryset()
        today = timezone.now()
        one_month_ago = today - timedelta(days=30)
        active_posts = models.JobPosting.objects.filter(is_active=True)
        expired_posts = models.JobPosting.objects.filter(deadline__lte=today)
        new_job_postings_last_month = models.JobPosting.objects.filter(posted_date__gte=one_month_ago)
        job_postings_by_type = models.JobPosting.objects.values("job_type") \
            .annotate(count=Count("job_type")) \
            .order_by("-count")

        job_posting_by_experience_level = models.JobPosting.objects.values("experience_level") \
            .annotate(count=Count("experience_level")) \
            .order_by("-count")

        job_postings_by_location = models.JobPosting.objects.values("location") \
            .annotate(count=Count("location")) \
            .order_by("-count")

        most_demanded_skills = Skill.objects \
            .annotate(count=Count("job_posts")) \
            .order_by("-count")


        return Response({
            "status": True,
            "message": "Vakansiyalar statistikasi muvaffaqiyatli olindi.",
            "data": {
                "total_job_postings": posts.count(),
                "active_job_postings": active_posts.count(),
                "expired_job_postings": expired_posts.count(),
                "new_job_postings_last_month": new_job_postings_last_month.count(),
                "job_postings_by_type": [{"type": post['job_type'], "count": post['count']} for post in job_postings_by_type],
                "job_posting_by_experience_level": [{"level": post['experience_level'], "count": post['count']} for post in job_posting_by_experience_level],
                "job_postings_by_location": [{"location": post["location"], "count": post["count"]} for post in job_postings_by_location],
                "most_demanded_skills": [{"skill": post.skill_name, "count": post["count"]} for post in most_demanded_skills]
            }
        }, status=status.HTTP_200_OK)


class JobApplicationStatsListAPIView(ListAPIView):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]


    def list(self, request, *args, **kwargs):
        applications = self.get_queryset()
        today = timezone.now()
        one_month_ago = today - timedelta(days=30)
        applications_last_month = models.JobApplication.objects.filter(applied_date__gte=one_month_ago)
        applications_by_status = models.JobApplication.objects.values("status") \
            .annotate(count=Count("status")) \
            .order_by("-count")

        applications_by_job_type = models.JobPosting.objects \
            .annotate(count=Count("job_applications")) \
            .order_by("-count")

        total_job_postings = models.JobPosting.objects.count()
        if total_job_postings > 0:
            average_application_per_job = applications.count() / total_job_postings
        else:
            average_application_per_job = 0

        most_applied_jobs = models.JobPosting.objects.annotate(
            num_applications=Count('job_applications')
        ).order_by('-num_applications')[:10]


        return Response({
            "status": True,
            "message": "Arizalar statistikasi muvaffaqiyatli olindi.",
            "data": {
                "total_applications": applications.count(),
                "applications_last_month": applications_last_month.count(),
                "applications_by_status": [{"status": application['status'], "count": applications_by_status['count']} for application in applications_by_status],
                "applications_by_job_type": [{"type": post.job_type, "count": post.count} for post in applications_by_job_type],
                "application_by_experience_level": [{"level": post.experience_level, "count": post.count} for post in applications_by_job_type],
                "average_application_per_job": average_application_per_job,
                "most_applied_jobs": [{"id": job.id, "title": job.title, "company": job.company.name, "applications_count": job.num_applications} for job in most_applied_jobs]
            }
        }, status=status.HTTP_200_OK)