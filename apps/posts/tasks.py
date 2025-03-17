from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils import timezone


@shared_task
def update_status_application_notification(user_id, id, post_title):
    message = f"Sizning '{post_title}' vakansiyasiga topshirgan arizangiz ko'rib chiqilmoqda."
    from apps.notifications.models import Notification
    from apps.users.models import User
    user = User.objects.get(id=user_id)
    Notification.objects.create(user=user, message=message, notification_type=Notification.NotificationType.APPLICATION_STATUS_CHANGE, related_object_id=id)


@shared_task
def new_posting_notification(post_id, post_title, company_id):
    from apps.users.models import Company
    from apps.notifications.models import Notification
    from .models import JobApplication, JobPosting

    company = Company.objects.get(id=company_id)
    posts = JobPosting.objects.filter(company=company)
    users_to_notify = set()

    for post in posts:
        applications = JobApplication.objects.filter(job_posting=post)

        for application in applications:
            users_to_notify.add(application.job_seeker.user)

    message = f"Yangi vakansiya: {post_title} - {company.name}"

    for user in users_to_notify:
        Notification.objects.create(
            user=user,
            message=message,
            notification_type=Notification.NotificationType.JOB_POSTING,
            related_object_id=post_id
        )

@shared_task
def update_active_post():
    from .models import JobPosting
    posts = JobPosting.objects.filter(deadline__lte=timezone.now().date(), is_active=True)
    posts.update(is_active=False)
