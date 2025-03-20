from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings


@shared_task
def send_password_reset_email(email, full_link):
    message = f"Yangi password kiritish uchun shu link bo'yicha o'ting: {full_link}."
    try:
        send_mail(
            'Job Connect dan xabar!',
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

    except Exception as e:
        return f"Email yuborishda xatolik yuzberdi {e}."


@shared_task
def send_verify_email_token(email, full_link):
    message = _(
        f"Sizning emailgiz Job Connect saytida ro'yxatdan o'tdi.\\Email sizga tegishligini tasdiqlash uchun ushbu link orqali saytga o'tsangiz bo'ladi: {full_link}")

    try:
        send_mail(
            "Job Connect saytidan xabar!",
            message,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

    except Exception as e:
        return f"Email yuborishda xatolik yuzberdi {e}."


@shared_task
def delete_tokens_expired():
    from .models import Token
    try:
        tokens = Token.objects.filter(expires_at__lte=timezone.now())
        tokens.delete()
    except Exception as e:
        return "Token o'chirishda hato yuz berdi."