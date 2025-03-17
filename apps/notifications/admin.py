from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'related_object_id', 'created_at')
    search_fields = ('message',)