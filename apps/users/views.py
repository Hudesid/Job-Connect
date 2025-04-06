from datetime import timedelta

from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.urls import reverse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import models, serializers, tasks, versioning
from .custom_response_decorator import custom_response
from .paginations import CompanyPageNumberPagination


@custom_response("register")
class RegisterAPIView(CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    versioning_class = versioning.CustomHeaderVersioning


    def create(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                token = models.Token.objects.create(user=user)
                verification_link = reverse("verify-email", kwargs={"pk": user.id, "token": token.token})
                current_site = get_current_site(request).domain
                full_link = f"http://{current_site}{verification_link}"

                tasks.send_verify_email_token.delay(user.email, full_link)

                return Response(
                    {
                        "id": user.id,
                        "username": user.username,
                        'email': user.email,
                        "user_type": user.user_type,
                        "date_joined": user.date_joined,
                    })


@custom_response("verify_email")
class VerifyEmailAPIView(APIView):
    versioning_class = versioning.CustomHeaderVersioning

    def get(self, request, pk, token, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = serializers.VerifyEmailSerializer(data={'pk': pk, 'token': token})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)


@custom_response("forgot_password")
class ForgotPasswordAPIView(APIView):
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = serializers.ForgotPasswordSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                token = models.Token.objects.create(user=serializer.validated_data.get("user"))
                verification_link = reverse('recovery_password', kwargs={'pk': serializer.validated_data.get('user').id, 'token': token.token})
                current_site = get_current_site(request).domain
                full_link = f"http://{current_site}{verification_link}"
                tasks.send_password_reset_email.delay(serializer.validated_data.get('email'), full_link)
                serializer.validated_data.pop("user")
            return Response(serializer.validated_data)


@custom_response("recovery_password")
class RecoveryPasswordAPIView(APIView):
    versioning_class = versioning.CustomHeaderVersioning

    def get(self, request, pk=None, token=None, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = serializers.RecoveryPasswordGetSerializer(data={"pk": pk, "token": token})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)


    def post(self, request, pk=None, token=None, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = serializers.RecoveryPasswordPostSerializer(data=request.data, context={"pk": pk, "token": token})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)


@custom_response("login")
class LoginAPIView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainSerializer
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return super().post(request, *args, **kwargs)


@custom_response("refresh")
class TokenRefreshAPIView(TokenRefreshView):
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return super().post(request, *args, **kwargs)


@custom_response("logout")
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication,]
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = serializers.LogoutSerializer(data=request.data, context={"request": request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)


@custom_response("job_seeker_create")
class UserProfileCreateAPIView(CreateAPIView):
    queryset = models.JobSeeker.objects.all()
    serializer_class = serializers.JobSeekerSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def create(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                profile = self.serializer_class(serializer.instance).data
                return Response(profile)


@custom_response("my_profile")
class UserProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.JobSeeker.objects.all()
    serializer_class = serializers.JobSeekerSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def get_object(self):
        version = self.request.version
        if version == '1.0':
            try:
                return models.JobSeeker.objects.get(user=self.request.user)

            except models.JobSeeker.DoesNotExist:
                return Response({"status": False, "message": "User profile topilmadi."}, status=status.HTTP_404_NOT_FOUND)


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            user_data = self.serializer_class(instance).data
            return Response(user_data)


    def update(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(self.get_object(), data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                user_data = serializer.save()
                user_profile = self.serializer_class(user_data).data
                return Response(user_profile)



    def test_func(self):
        version = self.request.version
        if version == '1.0':
            user_profile = self.get_object()
            return self.request.user == user_profile.user


@custom_response("user_profile")
class UserProfileRetrieveAPIView(RetrieveAPIView):
    queryset = models.JobSeeker.objects.all()
    serializer_class = serializers.JobSeekerSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            user_data = self.serializer_class(instance).data
            return Response(user_data)


@custom_response("resume_upload")
class ResumeUploadingAPIView(APIView, UserPassesTestMixin):
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def post(self, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            pk = self.kwargs['pk']
            serializer = serializers.ResumeUploadingSerializer(data=self.request.data, context={'pk': pk, 'request': self.request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)


    def test_func(self):
        version = self.request.version
        if version == '1.0':
            try:
                user_profile = models.JobSeeker.objects.get(id=self.kwargs['pk'])
            except models.JobSeeker.DoesNotExist:
                return False
            return self.request.user == user_profile.user


@custom_response("company_create")
class CompanyCreateAPIView(CreateAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def post(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = self.serializer_class(data=request.data, context={"request": self.request})

            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.validated_data)


@custom_response("companies_list")
class CompanyListAPIView(ListAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    pagination_class = CompanyPageNumberPagination
    versioning_class = versioning.CustomHeaderVersioning
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'industry']
    filterset_fields = ['location', 'created_at', 'updated_at', 'employees_count']

    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            return super().get(request, *args, **kwargs)


@custom_response("company_detail")
class CompanyRetrieveAPIView(RetrieveAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    versioning_class = versioning.CustomHeaderVersioning


    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            company_data = self.serializer_class(instance).data
            return Response(company_data)


@custom_response("my_company")
class CompanyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning

    def retrieve(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            instance = self.get_object()
            company = self.serializer_class(instance).data
            return Response(company)

    def test_func(self):
        version = self.request.version
        if version == '1.0':
            company = self.get_object()
            return self.request.user == company.user


@custom_response("users_stats")
class UsersStatsListAPIView(ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CompanyPageNumberPagination
    versioning_class = versioning.CustomHeaderVersioning


    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            users = self.get_queryset()
            today = timezone.now()
            one_month_ago = today - timedelta(days=30)
            one_week_ago = today - timedelta(days=7)
            new_users_last_month = models.User.objects.filter(date_joined__gte=one_month_ago).count()
            active_users_last_week = models.User.objects.filter(last_login__gte=one_week_ago).count()
            users_locations = models.JobSeeker.objects.values("location") \
                .annotate(count=Count("location")) \
                .order_by("count")

            users_by_registration_date = models.User.objects.annotate(month=TruncMonth('date_joined')) \
                .values('month') \
                .annotate(count=Count('id')
                          )

            user_by_registration_date = {
                user['month'].strftime('%Y-%m'): user['count'] for user in users_by_registration_date
            }


            return Response({
                    "total_users": users.count(),
                    "job_seekers": models.JobSeeker.objects.count(),
                    "employers": models.Company.objects.count(),
                    "new_users_last_month": new_users_last_month,
                    "active_users_last_week": active_users_last_week,
                    "users_by_location": [{"location": location['location'], "count": location["count"]} for location in users_locations],
                    "user_by_registration_date": user_by_registration_date
                })
