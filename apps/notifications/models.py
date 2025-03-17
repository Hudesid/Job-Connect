from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        APPLICATION_STATUS_CHANGE = "Application status change", _("Application status change")
        JOB_POSTING = "Job Posting", _("Job Posting")
        MESSAGE = "Message", _("Message")
        SYSTEM = "System", _("System Notification")

    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    related_object_id = models.IntegerField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

