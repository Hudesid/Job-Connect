from django.contrib import admin
from .models import Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'category')
    search_fields = ('id', 'name', 'category')
