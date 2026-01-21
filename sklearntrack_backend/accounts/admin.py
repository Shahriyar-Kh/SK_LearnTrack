# FILE: accounts/admin.py - CLEANED VERSION
# ============================================================================


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoginActivity, PasswordReset, EmailVerification


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'role', 'is_active', 'has_profile', 'created_at']
    list_filter = ['role', 'education_level', 'is_active', 'email_verified']
    search_fields = ['email', 'username', 'full_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'country', 'education_level', 'field_of_study')}),
        ('Learning', {'fields': ('learning_goal', 'preferred_study_hours', 'timezone')}),
        ('OAuth', {'fields': ('google_id',)}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Status', {'fields': ('email_verified', 'terms_accepted')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_login_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login_at']
    
    def has_profile(self, obj):
        """Check if user has associated profile"""
        return hasattr(obj, 'profile')
    has_profile.boolean = True
    has_profile.short_description = 'Profile Created'


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'device_type', 'login_at', 'location']
    list_filter = ['login_at', 'device_type']
    search_fields = ['user__email', 'ip_address', 'location']
    readonly_fields = ['user', 'ip_address', 'user_agent', 'login_at', 'location', 'device_type']
    date_hierarchy = 'login_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PasswordReset)
class PasswordResetAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'used']
    list_filter = ['used', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['user', 'token', 'created_at', 'expires_at', 'used']
    date_hierarchy = 'created_at'
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token'
    
    def has_add_permission(self, request):
        return False


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'created_at', 'expires_at', 'verified']
    list_filter = ['verified', 'created_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['user', 'token', 'created_at', 'expires_at', 'verified']
    date_hierarchy = 'created_at'
    
    def token_preview(self, obj):
        return f"{obj.token[:20]}..."
    token_preview.short_description = 'Token'
    
    def has_add_permission(self, request):
        return False