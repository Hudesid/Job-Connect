from datetime import timedelta
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
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
from apps.users.versioning import CustomHeaderVersioning
from apps.users.custom_response_decorator import custom_response


class CompanyActiveBasePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        company = Company.objects.get(user=request.user)
        if company is not None and company.is_active:
            return True
        else:
            return False


@custom_response("post_create")
class JobPostingCreateAPIView(CreateAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    versioning_class = CustomHeaderVersioning
    permission_classes = [IsAuthenticated, CompanyActiveBasePermission]


    def create(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(data=request.data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                post = self.serializer_class(serializer.instance).data
                tasks.new_posting_notification.delay(post['id'], post['title'], post['company']['id'])
                return Response(post)


@custom_response("posts_list")
class JobPostingListAPIView(ListAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    pagination_class = paginations.JobPostPageNumberPagination
    versioning_class = CustomHeaderVersioning
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    ordering_fields = ['posted_date', 'deadline']
    ordering = ['is_active']
    filterset_fields = [
        'company',
        'location',
        'job_type',
        'experience_level',
        'education_required',
        'salary_min',
        'salary_max',
        'deadline',
        'views_count',
        'is_active'
    ]
    search_fields = ['title', 'company', 'location']


    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return self.list(request, *args, **kwargs)


@custom_response("post_detail")
class JobPostingRetrieveAPIView(RetrieveAPIView):
    queryset = models.JobPosting.objects.all()
    versioning_class = CustomHeaderVersioning
    serializer_class = serializers.JopPostingSerializer


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            instance.views_count += 1
            instance.save()

            if request.user.is_authenticated:
                viewed_jobs = request.session.get('viewed_jobs', [])
                if instance.id not in viewed_jobs:
                    viewed_jobs.append(instance.id)
                    request.session['viewed_jobs'] = viewed_jobs
                    request.session.save()

            post = self.serializer_class(instance).data
            return Response(post)


@custom_response("post_detail")
class JobPostingRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.JobPosting.objects.all()
    versioning_class = CustomHeaderVersioning
    serializer_class = serializers.JopPostingSerializer
    permission_classes = [IsAuthenticated]

    def test_func(self):
        version = self.request.version
        if version == '1.0':
            post = self.get_object()
            return post.company.user == self.request.user


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            post = self.serializer_class(instance).data
            return Response(post)


    def update(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(self.get_object(), data=request.data, context={"request": request}, partial=True)
            if serializer.is_valid(raise_exception=True):
                post = serializer.save()
                post_data = self.serializer_class(post).data
                return Response(post_data)


    def delete(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            instance.delete()
            return Response()


@custom_response("posts_recommended")
class JobPostingRecommendedListAPIView(ListAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    pagination_class = paginations.JobPostPageNumberPagination
    versioning_class = CustomHeaderVersioning
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title', 'company']
    ordering_fields = ['deadline', 'posted_date']
    ordering = ['is_active']
    filterset_fields = [
        'company',
        'location',
        'job_type',
        'experience_level',
        'education_required',
        'salary_min',
        'salary_max',
        'deadline',
        'views_count',
        'is_active'
    ]


    def get_queryset(self):
        version = self.request.version
        if version == '1.0':
            viewed_jobs_ids = self.request.session.get("viewed_jobs", [])

            if not viewed_jobs_ids:
                try:
                    user = JobSeeker.objects.get(user=self.request.user)
                    posts = models.JobPosting.objects.filter(skills_required__in=user.skills.all())
                except JobSeeker.DoesNotExist:
                    posts = models.JobPosting.objects.none()
            else:
                viewed_jobs = models.JobPosting.objects.filter(id__in=viewed_jobs_ids)

                viewed_job_skills = set()
                viewed_job_locations = set()
                viewed_job_experiences = set()
                viewed_job_education_required = set()

                for job in viewed_jobs:
                    viewed_job_skills.update(job.skills_required.all())
                    viewed_job_locations.add(job.location)
                    viewed_job_experiences.add(job.experience_level)
                    viewed_job_education_required.add(job.education_required)

                posts = models.JobPosting.objects.filter(
                    Q(skills_required__in=viewed_job_skills) |
                    Q(location__in=viewed_job_locations) |
                    Q(experience_level__in=viewed_job_experiences) |
                    Q(education_required__in=viewed_job_education_required)
                ).distinct()

            return posts


    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return self.list(request, *args, **kwargs)


@custom_response("job_application_list_and_post")
class JobApplicationListCreateAPIView(ListCreateAPIView):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['job_posting__title']
    ordering_fields = ['applied_date', 'updated_at']
    ordering = ['status']
    filterset_fields = ['status', 'job_seeker__first_name']


    def create(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(data=request.data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                job_application = serializer.save()
                job_application_data = self.serializer_class(job_application).data
                return Response(job_application_data)


    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return self.list(request, *args, **kwargs)


@custom_response("job_application_detail")
class JobApplicationRetrieveAPIView(RetrieveAPIView):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            job_application_data = self.serializer_class(instance).data
            return Response(job_application_data)


@custom_response("my_application")
class JobApplicationRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            job_application_data = self.serializer_class(instance).data
            return Response(job_application_data)


    def update(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(self.get_object(), data=request.data, context={"request": request}, partial=True)
            if serializer.is_valid(raise_exception=True):
                job_application = serializer.save()
                job_application_data = self.serializer_class(job_application).data
                return Response(job_application_data)


    def delete(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            instance.delete()
            return Response()


@custom_response("my_application")
class JobApplicationUpdateAPIView(UpdateAPIView, UserPassesTestMixin):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated, CompanyActiveBasePermission]
    versioning_class = CustomHeaderVersioning


    def test_func(self):
        version = self.request.version
        if version == '1.0':
            job_application = self.get_object()
            company = Company.objects.filter(user=self.request.user)
            exist = company.filter(job_posts__in=job_application.job_posting)

            if exist.exists():
                return True
            else:
                return False


    def update(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(self.get_object(), data=request.data, context={"request": request}, partial=True)
            if serializer.is_valid(raise_exception=True):
                job_application = serializer.save()

                tasks.update_status_application_notification.delay(
                    request.user.id,
                    job_application.id,
                    job_application.job_posting.title
                )

                return Response({
                    "id": job_application.id,
                    "status": job_application.status,
                    "updated_date": job_application.updated_at
                })


@custom_response("post_applications")
class JobPostingApplicationListAPIView(ListAPIView):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter, DjangoFilterBackend]
    search_fields = ['job_posting__title']
    ordering_fields = ['applied_date', 'updated_at']
    ordering = ['status']
    filterset_fields = ['status', 'job_seeker__first_name']


    def get_queryset(self):
        version = self.request.version
        if version == '1.0':
            post = get_object_or_404(models.JobPosting, id=self.kwargs['pk'])
            return models.JobApplication.objects.filter(job_posting=post)


    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return self.list(request, *args, **kwargs)


@custom_response("saved_job_list")
class SavedJobListAPIView(ListAPIView):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning
    pagination_class = paginations.JobPostPageNumberPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['job_posting__title']
    ordering_fields = ['saved_date']


    def get_queryset(self):
        version = self.request.version
        if version == '1.0':
            job_seeker = JobSeeker.objects.get(user=self.request.user)
            return models.SavedJob.objects.filter(job_seeker=job_seeker)


    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return self.list(request, *args, **kwargs)


@custom_response("saved_job")
class SavedJobCreateAPIView(CreateAPIView):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning


    def create(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(data=request.data, context={"request": request})
            if serializer.is_valid(raise_exception=True):
                job = serializer.save()
                job_data = self.serializer_class(job).data
                return Response(job_data)


@custom_response("saved_job_delete")
class SavedJobDestroyAPIView(DestroyAPIView, UserPassesTestMixin):
    queryset = models.SavedJob.objects.all()
    serializer_class = serializers.SavedJobSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning


    def test_func(self):
        version = self.request.version
        if version == '1.0':
            job = self.get_object()
            user = JobSeeker.objects.get(user=self.request.user)
            return job.job_seeker == user


    def delete(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            instance.delete()
            return Response()


@custom_response("job_posting_stats")
class JobPostingStatsListAPIView(ListAPIView):
    queryset = models.JobPosting.objects.all()
    serializer_class = serializers.JopPostingSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
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

            response_data = {
                "total_job_postings": posts.count(),
                "active_job_postings": active_posts.count(),
                "expired_job_postings": expired_posts.count(),
                "new_job_postings_last_month": new_job_postings_last_month.count(),
                "job_postings_by_type": [{"type": post['job_type'], "count": post['count']} for post in job_postings_by_type],
                "job_posting_by_experience_level": [{"level": post['experience_level'], "count": post['count']} for post in job_posting_by_experience_level],
                "job_postings_by_location": [{"location": post["location"], "count": post["count"]} for post in job_postings_by_location],
                "most_demanded_skills": [{"skill": skill.name, "count": skill.count} for skill in most_demanded_skills]
            }

            return Response(response_data)


@custom_response("job_application_stats")
class JobApplicationStatsListAPIView(ListAPIView):
    queryset = models.JobApplication.objects.all()
    serializer_class = serializers.JobApplicationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
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
            average_application_per_job = applications.count() / total_job_postings if total_job_postings > 0 else 0

            most_applied_jobs = models.JobPosting.objects.annotate(
                num_applications=Count('job_applications')
            ).order_by('-num_applications')[:10]

            response_data = {
                "total_applications": applications.count(),
                "applications_last_month": applications_last_month.count(),
                "applications_by_status": [{"status": application['status'], "count": application['count']} for application in applications_by_status],
                "applications_by_job_type": [{"type": post.job_type, "count": post.count} for post in applications_by_job_type],
                "average_application_per_job": average_application_per_job,
                "most_applied_jobs": [{"id": job.id, "title": job.title, "company": job.company.name, "applications_count": job.num_applications} for job in most_applied_jobs]
            }

            return Response(response_data)
