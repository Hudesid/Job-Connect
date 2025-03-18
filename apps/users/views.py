from datetime import timedelta
from django.db import transaction
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers, models, tasks, versioning
from .paginations import CompanyPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils.translation import gettext_lazy as _


class RegisterAPIView(CreateAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    versioning_class = versioning.CustomHeaderVersioning


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = models.Token.objects.create(user=user)
            verification_link = reverse("verify-email", kwargs={"pk": user.id, "token": token.token})
            current_site = get_current_site(request).domain
            full_link = f"http://{current_site}{verification_link}"

            tasks.send_verify_email_token.delay(user.email, full_link)

            return Response({
                "status": True,
                "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tkazildi",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    'email': user.email,
                    "user_type": user.user_type,
                    "date_joined": user.date_joined,
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "status": False,
                "message": "Ro'yxatdan o'tishda xatolik yuz berdi",
                "errors": {
                    "username or email": ["Bu email manzil yoki username bilan foydalanuvchi allaqachon ro'yxatdan o'tgan."],
                    "password": ["Parol kamida 8 ta belgidan iborat bo'lishi kerak."]
                }
            }, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailAPIView(APIView):
    versioning_class = versioning.CustomHeaderVersioning

    def get(self, request, pk, token, *args, **kwargs):

        try:
            user = models.User.objects.get(id=pk)
            token = models.Token.objects.get(token=token)

        except models.User.DoesNotExist:
            return Response({"error": "The user ID is wrong"}, status=status.HTTP_400_BAD_REQUEST)

        except models.Token.DoesNotExist:
            return Response({"error": "The token is wrong"}, status=status.HTTP_400_BAD_REQUEST)

        if token.expires_at <= timezone.now() and not user.is_verify_email:
            with transaction.atomic():
                token.delete()
                user.delete()
            return Response({"message": _(f"Token vaqti o'tib ketdi shu sababli {user.username} o'chirib tashlandi.")}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.is_verify_email = True
        user.save()

        return Response({"message": _(f"Email '{user.email}' tekshirishdan muvaffaqiyatli o'tdi.")}, status=status.HTTP_200_OK)



class ForgotPasswordAPIView(APIView):
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email kiritish muhum."}, status==status.HTTP_400_BAD_REQUEST)

        try:
            user = models.User.objects.get(email=email)

        except models.User.DoesNotExist:
            return Response({"error": "Foydalanuvchi bunday email bilan topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        token = models.Token.objects.create(user=user)
        verification_link = reverse('recovery-password', kwargs={'pk': user.id, 'token': token.token})
        current_site = get_current_site(request).domain
        full_link = f"http://{current_site}{verification_link}"

        tasks.send_password_reset_email.delay(email, full_link)

        return Response(
            {"message": "Emailga xabar yuborildi!"},
            status=status.HTTP_200_OK
        )


class RecoveryPasswordAPIView(APIView):
    versioning_class = versioning.CustomHeaderVersioning

    def get(self, request, pk=None, token=None, *args, **kwargs):
        token_data = models.Token.objects.get(token=token)

        if token is None:
            return Response({'error': _("Token bo'lishi shart.")}, status=status.HTTP_400_BAD_REQUEST)

        if not token_data:
            return Response({'error': _("Token serverda topilmadi.")}, status=status.HTTP_400_BAD_REQUEST)

        elif token_data.expires_at <= timezone.now():
            token_data.delete()
            return Response({'error': "Token vaqti o'tib ketdi shu sababli token o'chirib tashaldi."}, status=status.HTTP_400_BAD_REQUEST)

        user = models.User.objects.get(id=pk)

        if user is None:
            return Response({'message': "Foydalanuvchi bunday ID bilan topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Token muvaffaqiyatli tasdiqlandi."})


    def post(self, request, pk=None, token=None, *args, **kwargs):
        new_password = request.data.get('new_password')
        user = models.User.objects.get(id=pk)
        user.set_password(new_password)
        user.save()
        return Response({'message': "Password muvaffaqiyatli yangilandi."})


class LoginAPIView(TokenObtainPairView):
    serializer_class = serializers.CustomTokenObtainSerializer
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            response = super().post(request, *args, **kwargs)
            access_token = response.data.get('access')
            refresh_token = response.data.get('refresh')

            if access_token and refresh_token:
                return Response({
                    "status": True,
                    "message": "Tizimga muvaffaqiyatli kirildi.",
                    "data": {
                        "access": f"{access_token}",
                        "refresh": f"{refresh_token}"
                    }
                }, status=status.HTTP_200_OK)

            else:
                return Response({
                    "status": False,
                    "message": "Tizimga kirishda xatolik yuz berdi.",
                    "errors": {
                        "detail": "Email yoki parol noto'g'ri.",
                    }
                }, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshAPIView(TokenRefreshView):
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        access_token = response.data.get('access', None)

        if access_token:
            return Response({
                "status": True,
                "message": "Token muvaffaqiyatli yangilandi.",
                "data": {
                    "access": access_token,
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": False,
                "message": "Token yangilashda xatolik yuz berdi.",
                "errors": {
                    "detail": "Token yaroqsiz yoki eskirgan.",
                }
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication,]
    versioning_class = versioning.CustomHeaderVersioning

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = self.request.data['refresh']
            if not refresh_token:
                return Response({
                    "status": False,
                    "errors": "Refresh token is required.",
                }, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({
                "status": True,
                "message": "Successfully logged out.",
            }, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response({
                "status": False,
                "errors": f"Token error: {str(e)}",
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "errors": f"An error occurred: {str(e)}",
            }, status=status.HTTP_400_BAD_REQUEST)


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
                profile = serializer.save()
                return Response({
                    "status": True,
                    "message": "Ish qidiruvchi profili muvaffaqiyatli yaratildi.",
                    "data": serializer.validated_data
                }, status=status.HTTP_201_CREATED)

            else:
                return Response({
                    "status": False,
                    "message": "Noto'g'ri malumot kiritilgan",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.JobSeeker.objects.all()
    serializer_class = serializers.JobSeekerSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def get_object(self):
        try:
            return models.JobSeeker.objects.get(user=self.request.user)

        except models.JobSeeker.DoesNotExist:
            return Response({"message": "User profile topilmadi."}, status=status.HTTP_404_NOT_FOUND)


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object().user

        user_data = serializers.UserSerializer(instance).data

        return Response({
            "status": True,
            "message": "Foydalanuvchi malumotlari muvaffaqiyatli olindi.",
            "data": {user_data}
        }, status=status.HTTP_200_OK)




    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        if serializer.is_valid():
            user_profile = serializer.save()
            return Response({
                "status": True,
                "message": "Foydalanuvchi ma'lumotlari muvaffaqiyatli yangilandi.",
                "data": {
                    "id": user_profile.id,
                    "username": user_profile.user.username,
                    "email": user_profile.user.email,
                    "user_type": user_profile.user.user_type,
                    "date_joined": user_profile.user.date_joined,
                    "is_active": user_profile.user.is_active
                }
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": False,
                "message": "Noto'g'ri ma'lumot kiritilgan.",
            }, status=status.HTTP_400_BAD_REQUEST)


    def test_func(self):
        user_profile = self.get_object()
        return self.request.user == user_profile.user


class UserProfileRetrieveAPIView(RegisterAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserDataForGetRequestsSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


class ResumeUploadingAPIView(APIView, UserPassesTestMixin):
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def post(self, request, *args, **kwargs):
        try:
            user_profile = models.JobSeeker.objects.get(id=self.kwargs['id'])
        except models.JobSeeker.DoesNotExist:
            return Response({"error": "User profile topilmadi."}, status=status.HTTP_404_NOT_FOUND)

        resume = request.data.get("resume")

        if resume:
            user_profile.resume = resume
            user_profile.save()
            return Response({
                "status": True,
                "message": "Rezyume muvaffaqiyatli yuklandi.",
                "data": {"id": user_profile.id, "resume": user_profile.resume}
            }, status=status.HTTP_200_OK)

        else:
            return Response({
                "status": False,
                "error": "Rezyume yuklamagan.",
            }, status=status.HTTP_400_BAD_REQUEST)

    def test_func(self):
        try:
            user_profile = models.JobSeeker.objects.get(id=self.kwargs['id'])
        except models.JobSeeker.DoesNotExist:
            return False
        return self.request.user == user_profile.user


class CompanyCreateAPIView(CreateAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            company = serializer.save()
            company_data = serializers.CompanySerializer(company).data
            return Response({
                "status": True,
                "message": "Kompaniya profili muvaffaqiyatli yaratildi.",
                "data": {company_data}
            }, status=status.HTTP_201_CREATED)

        else:
            return Response({
                "status":  False,
                "message": "Kiritlgan malumot noto'g'ri",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)


class CompanyListAPIView(ListAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    pagination_class = CompanyPageNumberPagination
    versioning_class = versioning.CustomHeaderVersioning
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'industry']
    filterset_fields = ['location', 'created_at', 'updated_at', 'employees_count']

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)

        return Response({
            "status": True,
            "message": "Kompaniyalar ro'yxati muvaffiqiyatli olindi.",
            "data": {
                "count": response.data['count'],
                "next": response.data['next'],
                "previous": response.data['previous'],
                "results": response.data['results']
            }}, status=status.HTTP_200_OK)


class CompanyRetrieveAPIView(RetrieveAPIView):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    versioning_class = versioning.CustomHeaderVersioning


    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        company_data = self.get_serializer(instance).data

        return Response({
            "status": True,
            "message": "Companiya ma'lumoti muvaffaqiyatli olindi.",
            "data": {company_data}
        }, status=status.HTTP_200_OK)


class CompanyRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView, UserPassesTestMixin):
    queryset = models.Company.objects.all()
    serializer_class = serializers.CompanySerializer
    permission_classes = [IsAuthenticated]
    versioning_class = versioning.CustomHeaderVersioning


    def test_func(self):
        company = self.get_object()
        return self.request.user == company.user



class UsersStatsListAPIView(ListAPIView):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CompanyPageNumberPagination
    versioning_class = versioning.CustomHeaderVersioning


    def list(self, request, *args, **kwargs):
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
            "status": True,
            "message": "Foydalanuvchilar statistikasi muvaffaqiyatli olindi.",
            "data": {
                "total_users": users.count(),
                "job_seekers": models.JobSeeker.objects.count(),
                "employers": models.Company.objects.count(),
                "new_users_last_month": new_users_last_month,
                "active_users_last_week": active_users_last_week,
                "users_by_location": [{"location": location['location'], "count": location["count"]} for location in users_locations],
                "user_by_registration_date": user_by_registration_date
            }
        }, status=status.HTTP_200_OK)


