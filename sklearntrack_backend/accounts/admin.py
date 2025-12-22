# FILE: accounts/admin.py
# ============================================================================

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile, LoginActivity


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'education_level', 'is_active', 'email_verified']
    search_fields = ['email', 'username', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'country', 'education_level', 'field_of_study')}),
        ('Learning', {'fields': ('learning_goal', 'preferred_study_hours', 'timezone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Status', {'fields': ('email_verified', 'terms_accepted')}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_study_days', 'current_streak', 'longest_streak']
    search_fields = ['user__email', 'user__username']


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'login_at', 'location']
    list_filter = ['login_at']
    search_fields = ['user__email', 'ip_address']
