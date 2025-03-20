from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from . import models, serializers, paginations
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.versioning import CustomHeaderVersioning


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
            notifications = self.queryset.filter(user=self.request.user)
            if not notifications:
                return Response({
                    "status": False,
                    "errors": "Hali bildirishnoma yo'q."
                }, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True).data
            return Response({
                "status": True,
                "message": "Bildirishnomalar ro'yxati muvaffaqiyatli olindi.",
                "data": {serializer}
            }, status=status.HTTP_200_OK)


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
            notifications = self.queryset.filter(user=self.kwargs['id'])
            if not notifications:
                return Response({
                    "status": False,
                    "errors": "Hali bildirishnoma yo'q."
                }, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True).data
            return Response({
                "status": True,
                "message": "Bildirishnomalar ro'yxati muvaffaqiyatli olindi.",
                "data": {serializer}
            }, status=status.HTTP_200_OK)


class NotificationUpdateAPIView(APIView):
    versioning_class = CustomHeaderVersioning

    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            notification = models.Notification.objects.get(id=self.kwargs['id'])

            if not notification:
                return Response({
                    "status": False,
                    "message": "Bildirishnomalar hali yo'q."
                }, status=status.HTTP_404_NOT_FOUND)

            if notification.user != request.user:
                return Response({
                    "status": False,
                    "errors": "Siz bu bildirishnomaga huquqingiz yo'q."
                }, status=status.HTTP_400_BAD_REQUEST)

            notification.is_read = True
            notification.save()
            return Response({
                "status": True,
                "message": "Bildirishnoma o'qilgan deb belgilandi.",
                "data": {"id": notification.id, "is_read": notification.is_read}
            }, status=status.HTTP_200_OK)


class NotificationsUpdateAPIView(APIView):
    versioning_class = CustomHeaderVersioning

    def get(self, request, *args, **kwargs):
        version = self.request.version
        if version == '1.0':
            notifications = models.Notification.objects.filter(user=request.user)

            if not notifications.exists():
                return Response({
                    "status": False,
                    "message": "Bildirishnomalar hali yo'q."
                }, status=status.HTTP_404_NOT_FOUND)

            if notifications.filter(user=request.user).count() != notifications.count():
                return Response({
                    "status": False,
                    "errors": "Siz bu bildirishnomaga huquqingiz yo'q."
                }, status=status.HTTP_400_BAD_REQUEST)

            notifications.update(is_read=True)
            notifications.save()
            return Response({
                "status": True,
                "message": "Barcha bildirishnomalar o'qilgan deb belgilandi.",
                "data": {"count": notifications.count()}
            }, status=status.HTTP_200_OK)




