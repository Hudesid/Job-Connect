from django.urls import path
from . import views


urlpatterns = [
    path("notifications/my-notification/", views.MyNotificationListAPIView.as_view(), name="my_notification"),
    path("notifications/<int:id>/", views.NotificationListAPIView.as_view(), name="my_notification"),
    path("notifications/<int:id>/read/", views.NotificationUpdateAPIView.as_view(), name="notification_status_update"),
    path("notifications/read-all/", views.NotificationsUpdateAPIView.as_view(), name="notifications_status_update"),
]