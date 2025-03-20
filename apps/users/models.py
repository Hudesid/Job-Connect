import uuid
from datetime import timedelta
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from .managers import CustomUserManager
from apps.skills.models import Skill


class User(AbstractUser, PermissionsMixin):
    class UserTypeChoice(models.TextChoices):
        ADMIN = 'admin', _("ADMIN")
        JOB_SEEKER = 'job_seeker', _("JOB_SEEKER")
        EMPLOYER = "employer", _("EMPLOYER")

    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, blank=True)
    password = models.CharField(max_length=128)
    is_verify_email = models.BooleanField(default=False)
    user_type = models.CharField(max_length=50, choices=UserTypeChoice.choices, default=UserTypeChoice.JOB_SEEKER)
    date_joined = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


    class Meta:
        app_label = 'users'


class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    phone_number = models.CharField(max_length=30, validators=[RegexValidator(
            regex=r'^\+998\d{9}$',
            message="Phone number must start with '+9989' and be followed by 8 digits."
        )])
    location = models.CharField(max_length=255)
    bio = models.TextField()
    skills = models.ManyToManyField(Skill, related_name="job_seekers")
    experience_years = models.IntegerField()
    education_level = models.CharField(max_length=255)
    resume = models.FileField(upload_to="job_seeker_resumes/", blank=True, null=True)
    profile_photo = models.ImageField(upload_to="job_seeker_photos/", null=True)


    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="company")
    name = models.CharField(max_length=255)
    description = models.TextField()
    website = models.URLField(unique=True)
    industry = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    founded_year = models.IntegerField()
    logo = models.ImageField(upload_to="company_logos/")
    employees_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)


    def __str__(self):
        return f"Username:{self.user.username}, Name:{self.name}"


class Token(models.Model):
    token = models.CharField(max_length=50, unique=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(seconds=200))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4())
        super().save(*args, **kwargs)
