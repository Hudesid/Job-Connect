from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ('id', 'user', 'message', 'notification_type', 'related_object_id', 'created_at', 'is_read')


    def get_user(self, obj):
        from apps.users.serializers import UserSerializer
        return UserSerializer(obj.user).data


class NotificationIsReadSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, attrs):
        id = attrs['id']

        try:
            notification = Notification.objects.get(id=id)

        except Notification.DoesNotExist:
            raise serializers.ValidationError({"error": "Bu ID bo'yicha bildirishnoma yo'q."})

        if notification.user != self.context['request'].user:
            raise serializers.ValidationError({"error": "Bu bildirishnomaga huquqingiz yo'q"})

        notification.is_read = True
        notification.save()

        attrs.pop("id")
        attrs['notification'] = NotificationSerializer(notification).data
        return attrs


class NotificationsIsReadSerializer(serializers.Serializer):
    user = serializers.IntegerField()

    def validate(self, attrs):
        user_id = attrs['user']
        request_user = self.context['request'].user

        if user_id != request_user.id:
            raise serializers.ValidationError({"error": "Bu bildirishnomaga huquqingiz yo'q"})

        notifications = Notification.objects.filter(user=user_id)

        if not notifications.exists():
            raise serializers.ValidationError({"error": "Foydalanuvchi uchun bildirishnomalar topilmadi"})

        notifications.update(is_read=True)

        attrs['notifications'] = notifications
        return attrs

    def to_representation(self, instance):
        return NotificationSerializer(instance['notifications'], many=True).data
