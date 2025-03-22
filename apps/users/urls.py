from django.urls import path
from . import views


urlpatterns = [
    path("auth/register/", views.RegisterAPIView.as_view(), name='register'),
    path("auth/login/", views.LoginAPIView.as_view(), name='login'),
    path("auth/refresh/", views.TokenRefreshAPIView.as_view(), name='refresh_token'),
    path("auth/logout/", views.LogoutAPIView.as_view(), name='logout'),
    path("user/verify-email/<int:pk>/<str:token>/", views.VerifyEmailAPIView.as_view(), name='verify-email'),
    path("user/forgot-password/", views.ForgotPasswordAPIView.as_view(), name='forgot_password'),
    path("user/recovery-password/<int:pk>/<str:token>/", views.RecoveryPasswordAPIView.as_view(), name='recovery_password'),
    path("user/me/", views.UserProfileRetrieveUpdateDestroyAPIView.as_view(), name='my_profile'),
    path("user/profile/<int:pk>/", views.UserProfileRetrieveAPIView.as_view(), name='user_profile'),
    path("companies/create/", views.CompanyCreateAPIView.as_view(), name='company_create'),
    path("companies/list/", views.CompanyListAPIView.as_view(), name='company_list'),
    path("companies/detail/<int:pk>/", views.CompanyRetrieveAPIView.as_view(), name='company_detail'),
    path("companies/my-company/<int:pk>/", views.CompanyRetrieveUpdateDestroyAPIView.as_view(), name='my_company_detail'),
    path("job-seeker/create/", views.UserProfileCreateAPIView.as_view(), name='user_profile_create'),
    path("job-seeker/<int:pk>/upload-resume/", views.ResumeUploadingAPIView.as_view(), name='resume_upload'),
    path("stats/users/", views.UsersStatsListAPIView.as_view(), name="users_stats")
]