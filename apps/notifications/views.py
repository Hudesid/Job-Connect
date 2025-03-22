from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from . import models, serializers, paginations
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.versioning import CustomHeaderVersioning
from apps.users.custom_response_decorator import custom_response


@custom_response("notifications_list")
class MyNotificationListAPIView(ListAPIView):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning
    pagination_class = paginations.NotificationPageNumberPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering = ['created_at']
    filterset_fields = ['notification_type', 'is_read']


    def get_queryset(self):
        version = self.request.version
        if version == '1.0':
            return self.queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response({
                    "message": "Hali bildirishnoma yo'q."
                }, status=status.HTTP_404_NOT_FOUND)
            return super().list(request, *args, **kwargs)


@custom_response("notifications_list")
class NotificationListAPIView(ListAPIView):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationSerializer
    permission_classes = [IsAuthenticated]
    versioning_class = CustomHeaderVersioning
    pagination_class = paginations.NotificationPageNumberPagination
    filter_backends = [OrderingFilter, DjangoFilterBackend]
    ordering = ['created_at']
    filterset_fields = ['notification_type', 'is_read']


    def get_queryset(self):
        version = self.request.version
        if version == '1.0':
            return self.queryset.filter(user=self.kwargs['pk'])

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response({
                    "message": "Hali bildirishnoma yo'q."
                }, status=status.HTTP_404_NOT_FOUND)
            return super().list(request, *args, **kwargs)


@custom_response("notification_status_read")
class NotificationUpdateAPIView(APIView):
    versioning_class = CustomHeaderVersioning

    def get(self, request, pk, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            serializer = serializers.NotificationIsReadSerializer(data={'id': pk}, context={"request": self.request})
            serializer.is_valid(raise_exception=True)
            return Response(serializer.validated_data)


@custom_response("notifications_status_read")
class NotificationsUpdateAPIView(ListAPIView):
    queryset = models.Notification.objects.all()
    serializer_class = serializers.NotificationsIsReadSerializer
    versioning_class = CustomHeaderVersioning

    def get(self, request, *args, **kwargs):
        version = request.version
        if version == '1.0':
            notifications = models.Notification.objects.filter(user=request.user)
            if not notifications.exists():
                return Response({
                    "message": "Bildirishnomalar hali yo'q."
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = serializers.NotificationsIsReadSerializer(
                data={"user": request.user.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            return Response({
                "count": notifications.count()
            })




