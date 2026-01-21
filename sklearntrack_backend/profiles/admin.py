# FILE: profiles/admin.py
# ============================================================================

from django.contrib import admin
from .models import Profile, NotificationSettings, ProfileActivityLog


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'total_study_days',
        'current_streak',
        'total_notes',
        'has_avatar',
        'created_at'
    ]
    list_filter = ['created_at', 'timezone']
    search_fields = ['user__email', 'user__full_name', 'bio']
    readonly_fields = [
        'total_study_days',
        'current_streak',
        'longest_streak',
        'total_notes',
        'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Personal Info', {
            'fields': ('bio', 'avatar')
        }),
        ('Learning Preferences', {
            'fields': (
                'learning_goal',
                'preferred_study_hours',
                'timezone',
                'skill_interests'
            )
        }),
        ('Statistics', {
            'fields': (
                'total_study_days',
                'current_streak',
                'longest_streak',
                'total_notes'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def has_avatar(self, obj):
        return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'Avatar'


@admin.register(NotificationSettings)
class NotificationSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'email_notifications',
        'weekly_summary',
        'course_reminders',
        'achievement_alerts',
        'updated_at'
    ]
    list_filter = [
        'email_notifications',
        'weekly_summary',
        'course_reminders',
        'achievement_alerts'
    ]
    search_fields = ['profile__user__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('profile',)
        }),
        ('Email Notifications', {
            'fields': (
                'email_notifications',
                'weekly_summary',
                'course_reminders',
                'achievement_alerts',
                'community_updates'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        return obj.profile.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'profile__user__email'


@admin.register(ProfileActivityLog)
class ProfileActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'user_email',
        'activity_type',
        'ip_address',
        'created_at'
    ]
    list_filter = ['activity_type', 'created_at']
    search_fields = [
        'profile__user__email',
        'description',
        'ip_address'
    ]
    readonly_fields = [
        'profile',
        'activity_type',
        'description',
        'ip_address',
        'user_agent',
        'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        return obj.profile.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'profile__user__email'
    
    def has_add_permission(self, request):
        # Activity logs are created automatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Activity logs should not be edited
        return False