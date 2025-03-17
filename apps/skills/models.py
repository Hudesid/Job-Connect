from django.db import models
from django.utils.translation import gettext_lazy as _


class Skill(models.Model):
    class SkillCategoryChoice(models.TextChoices):
        HARD_SKILL = 'Hard Skill', _('Hard Skill')
        SOFT_SKILL = 'Soft Skill', _('Soft Skill')
        PROGRAMMING = 'Programming', _('Programming')
        DESIGN = 'Design', _('Design')
        MANAGEMENT = 'Management', _('Management')
        DATA_SCIENCE = 'Data Science', _('Data Science')
        MARKETING = 'Marketing', _('Marketing')
        FRAMEWORK = 'Framework', _('Framework')

    name = models.CharField(max_length=255, unique=True)
    category = models.CharField(max_length=100, choices=SkillCategoryChoice.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name