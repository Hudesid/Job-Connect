from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="Job-Connect",
        default_version="v1",
        description="Job-Connect where you can post vacations.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@myapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,)
)


urlpatterns = [
    path("notifications/my-notification/", views.MyNotificationListAPIView.as_view(), name="my_notification"),
    path("notifications/<int:pk>/", views.NotificationListAPIView.as_view(), name="my_notification"),
    path("notifications/<int:pk>/read/", views.NotificationUpdateAPIView.as_view(), name="notification_status_update"),
    path("notifications/read-all/", views.NotificationsUpdateAPIView.as_view(), name="notifications_status_update"),
    path('swagger/', schema_view.as_view(), name='swagger-docs')
]
