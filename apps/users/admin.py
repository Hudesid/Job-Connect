from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AdminPasswordChangeForm
from .models import User, Token, JobSeeker, Company
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'user_type')


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    list_display = ('id', 'username', 'email', 'is_active', 'is_verify_email')
    list_filter = ('date_joined', 'updated_at', 'is_active', 'is_verify_email')
    search_fields = ('username', 'email', 'id')
    ordering = ('email', 'username')
    readonly_fields = ('last_login', 'date_joined', 'id')
    fieldsets = (
        ('Personal Info', {
        'fields': ('id', 'username', 'email', 'is_active', 'is_verify_email', 'user_type')
        }),
        ('Permission', {
            'fields': ('is_staff', 'is_superuser')
        }),
        ('Change Password', {
            'fields': ('password',),
            'classes': ('collapse',)
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_active', 'is_staff', 'is_superuser', 'is_verify_email')

        }))


admin.site.register(User, CustomUserAdmin)


@admin.register(Token)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'expires_at', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('id', 'token')


@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone_number', 'location', 'experience_years')
    list_filter = ('location', 'experience_years', 'skills', 'education_level')
    search_fields = ('first_name', 'last_name', 'phone_number', 'date_of_birth')


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'industry', 'location', 'founded_year', 'employees_count', 'is_active')
    list_filter = ('location', 'industry', 'founded_year', 'employees_count', 'is_active', 'created_at', 'updated_at')
    search_fields = ('id', 'name', 'industry')
