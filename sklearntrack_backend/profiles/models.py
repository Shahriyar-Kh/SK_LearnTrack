# FILE: profiles/models.py
# ============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from PIL import Image
import os

User = get_user_model()


def validate_image_size(image):
    """Validate image file size (max 5MB)"""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError('Image file size cannot exceed 5MB')


def validate_skill_interests(value):
    """Validate skill interests list"""
    if not isinstance(value, list):
        raise ValidationError('Skill interests must be a list')
    if len(value) > 30:
        raise ValidationError('Cannot have more than 30 skill interests')
    for skill in value:
        if not isinstance(skill, str):
            raise ValidationError('Each skill must be a string')
        if len(skill) > 50:
            raise ValidationError('Skill name cannot exceed 50 characters')


class Profile(models.Model):
    """Extended user profile with learning preferences and settings"""
    
    EDUCATION_LEVELS = [
        ('high_school', 'High School'),
        ('undergraduate', 'Undergraduate'),
        ('graduate', 'Graduate'),
        ('postgraduate', 'Postgraduate'),
        ('professional', 'Professional'),
    ]
    
    TIMEZONES = [
        ('America/New_York', 'Eastern Time (ET)'),
        ('America/Chicago', 'Central Time (CT)'),
        ('America/Denver', 'Mountain Time (MT)'),
        ('America/Los_Angeles', 'Pacific Time (PT)'),
        ('UTC', 'UTC'),
        ('Europe/London', 'London (GMT)'),
        ('Europe/Paris', 'Central European Time'),
        ('Asia/Dubai', 'Dubai (GST)'),
        ('Asia/Karachi', 'Pakistan (PKT)'),
        ('Asia/Kolkata', 'India (IST)'),
        ('Asia/Shanghai', 'China (CST)'),
        ('Asia/Tokyo', 'Japan (JST)'),
        ('Australia/Sydney', 'Sydney (AEDT)'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    # Personal Information
    bio = models.TextField(
        blank=True,
        max_length=2000,
        help_text='Brief biography (max 2000 characters)'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        validators=[validate_image_size],
        help_text='Profile picture (max 5MB, jpg/png/webp)'
    )
    
    # Learning Preferences
    learning_goal = models.TextField(
        blank=True,
        max_length=1000,
        help_text='What you want to achieve'
    )
    preferred_study_hours = models.IntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text='Preferred daily study hours (1-12)'
    )
    timezone = models.CharField(
        max_length=50,
        default='UTC',
        choices=TIMEZONES
    )
    skill_interests = models.JSONField(
        default=list,
        blank=True,
        validators=[validate_skill_interests],
        help_text='List of skills you are interested in'
    )
    
    # Statistics (managed by system)
    total_study_days = models.IntegerField(default=0, editable=False)
    current_streak = models.IntegerField(default=0, editable=False)
    longest_streak = models.IntegerField(default=0, editable=False)
    total_notes = models.IntegerField(default=0, editable=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'profiles'
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email}'s Profile"
    
    def save(self, *args, **kwargs):
        # Resize avatar if provided
        super().save(*args, **kwargs)
        
        if self.avatar:
            img_path = self.avatar.path
            try:
                img = Image.open(img_path)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Resize to 512x512
                if img.height > 512 or img.width > 512:
                    output_size = (512, 512)
                    img.thumbnail(output_size, Image.Resampling.LANCZOS)
                    img.save(img_path, quality=90, optimize=True)
            except Exception as e:
                # Log error but don't fail the save
                print(f"Error resizing avatar: {e}")
    
    def get_avatar_url(self):
        """Get avatar URL (works for both local and cloud storage)"""
        if self.avatar:
            return self.avatar.url
        return None
    
    def add_skill_interest(self, skill):
        """Add a skill to interests"""
        if skill not in self.skill_interests:
            self.skill_interests.append(skill)
            self.save()
    
    def remove_skill_interest(self, skill):
        """Remove a skill from interests"""
        if skill in self.skill_interests:
            self.skill_interests.remove(skill)
            self.save()
    
    def update_statistics(self):
        """Update profile statistics from related models"""
        # Update total notes count
        if hasattr(self.user, 'notes'):
            self.total_notes = self.user.notes.count()
        
        # Update study days and streaks (implement based on your study tracking)
        # This is a placeholder - implement based on your actual study tracking model
        self.save(update_fields=['total_notes', 'total_study_days', 'current_streak', 'longest_streak'])


class NotificationSettings(models.Model):
    """User notification preferences"""
    
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='notification_settings',
        primary_key=True
    )
    
    # Email Notifications
    email_notifications = models.BooleanField(
        default=True,
        help_text='Receive email notifications for important updates'
    )
    weekly_summary = models.BooleanField(
        default=True,
        help_text='Receive weekly summary of learning progress'
    )
    course_reminders = models.BooleanField(
        default=True,
        help_text='Receive reminders about active courses'
    )
    
    # Future notification types can be added here
    achievement_alerts = models.BooleanField(default=True)
    community_updates = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_settings'
        verbose_name = 'Notification Settings'
        verbose_name_plural = 'Notification Settings'
    
    def __str__(self):
        return f"Notifications for {self.profile.user.email}"


class ProfileActivityLog(models.Model):
    """Track profile changes for security and audit purposes"""
    
    ACTIVITY_TYPES = [
        ('profile_updated', 'Profile Updated'),
        ('avatar_changed', 'Avatar Changed'),
        ('password_changed', 'Password Changed'),
        ('preferences_updated', 'Preferences Updated'),
        ('notifications_updated', 'Notifications Updated'),
    ]
    
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='activity_logs'
    )
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'profile_activity_logs'
        ordering = ['-created_at']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        return f"{self.profile.user.email} - {self.activity_type} - {self.created_at}"