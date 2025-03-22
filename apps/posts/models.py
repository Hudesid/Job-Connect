from django.db import models
from django.utils.translation import gettext_lazy as _


class JobPosting(models.Model):
    class JobTypeChoice(models.TextChoices):
        FULL_TIME = "Full time", _("Full time")
        PART_TIME = "Part time", _("Part time")
        CONTRACT = "Contract", _("Contract")
        INTERNSHIP = "Internship", _("Internship")

    class ExperienceLevelChoice(models.TextChoices):
        ENTRY = "Entry", _("Entry")
        MIDDLE = "Middle", _("Middle")
        SENIOR = "Senior", _("Senior")
        EXECUTIVE = "Executive", _("Executive")

    class EducationRequiredChoice(models.TextChoices):
        HIGH_SCHOOL = "High School", _("High School")
        BACHELORS = "Bachelors", _("Bachelor's Degree")
        MASTERS = "Masters", _("Master's Degree")
        PHD = "PhD", _("PhD")

    company = models.ForeignKey("users.Company", on_delete=models.CASCADE, related_name="job_posts")
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    responsibilities = models.TextField()
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=30, choices=JobTypeChoice.choices)
    experience_level = models.CharField(max_length=20, choices=ExperienceLevelChoice.choices)
    education_required = models.CharField(max_length=30, choices=EducationRequiredChoice.choices)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    skills_required = models.ManyToManyField("skills.Skill", related_name="job_posts")
    is_active = models.BooleanField(default=False)
    posted_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateField()
    views_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.company.name}: {self.title}"


class JobApplication(models.Model):
    class StatusChoice(models.TextChoices):
        APPLIED = "Applied", _("Applied")
        UNDER_REVIEW = "Under review", _("Under review")
        SHORTLISTED = "Shortlisted", _("Shortlisted")
        REJECTED = "Rejected", _("Rejected")
        OFFERED = "Offered", _("Offered")
        HIRED = "Hired", _("Hired")

    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="job_applications")
    job_seeker = models.ForeignKey("users.JobSeeker", on_delete=models.CASCADE, related_name="job_applications")
    cover_later = models.TextField()
    resume = models.FileField(upload_to="job_application_resumes/")
    status = models.CharField(max_length=30, choices=StatusChoice.choices, default=StatusChoice.UNDER_REVIEW)
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SavedJob(models.Model):
    job_seeker = models.ForeignKey("users.JobSeeker", on_delete=models.CASCADE, related_name="saved_jobs")
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="saved_job")
    saved_date = models.DateTimeField(auto_now_add=True)


