from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'user', 'message', 'notification_type', 'related_object_id', 'created_at', 'is_read')


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from apps.users.serializers import UserSerializer
        representation['user'] = UserSerializer(instance.user).data
        return representation