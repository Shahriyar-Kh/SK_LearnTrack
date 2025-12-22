# FILE: accounts/models.py
# ============================================================================

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom User model with extended fields"""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin'),
    ]
    
    EDUCATION_LEVEL_CHOICES = [
        ('high_school', 'High School'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
        ('professional', 'Professional'),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Additional registration fields
    full_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES)
    field_of_study = models.CharField(max_length=255)
    learning_goal = models.TextField(blank=True)
    preferred_study_hours = models.IntegerField(default=2)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Account status
    email_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    terms_accepted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    skill_interests = models.JSONField(default=list)  # List of skills
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    weekly_summary = models.BooleanField(default=True)
    course_reminders = models.BooleanField(default=True)
    
    # Statistics
    total_study_days = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class LoginActivity(models.Model):
    """Track user login activities"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_activities')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'login_activities'
        ordering = ['-login_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.login_at}"
