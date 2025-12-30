# FILE: accounts/models.py - COMPLETE FIX
# ============================================================================

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user"""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'student')
        
        # Auto-generate username from email
        if 'username' not in extra_fields or not extra_fields.get('username'):
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            
            while self.model.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            extra_fields['username'] = username
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('email_verified', True)
        extra_fields.setdefault('terms_accepted', True)
        
        # Set required fields for superuser
        if 'full_name' not in extra_fields:
            extra_fields['full_name'] = 'Admin User'
        if 'country' not in extra_fields:
            extra_fields['country'] = 'USA'
        if 'education_level' not in extra_fields:
            extra_fields['education_level'] = 'postgraduate'
        if 'field_of_study' not in extra_fields:
            extra_fields['field_of_study'] = 'Administration'
        
        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model with email as primary identifier"""
    
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
    
    # Override email to be unique and required
    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True)
    
    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    # Custom fields
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    full_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(
        max_length=50, 
        choices=EDUCATION_LEVEL_CHOICES, 
        blank=True
    )
    field_of_study = models.CharField(max_length=255, blank=True)
    learning_goal = models.TextField(blank=True)
    preferred_study_hours = models.IntegerField(default=2)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Account status
    email_verified = models.BooleanField(default=False)
    terms_accepted = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    
    objects = CustomUserManager()
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        verbose_name = 'user'
        verbose_name_plural = 'users'
    
    def save(self, *args, **kwargs):
        # Normalize email
        if self.email:
            self.email = self.email.lower().strip()
        
        # Auto-generate username if not provided
        if not self.username:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            while User.objects.filter(username=username).exclude(pk=self.pk).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
        
        # Set role to admin if user is staff or superuser
        if self.is_staff or self.is_superuser:
            self.role = 'admin'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    skill_interests = models.JSONField(default=list)
    
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
        verbose_name = 'profile'
        verbose_name_plural = 'profiles'
    
    def __str__(self):
        return f"{self.user.email}'s Profile"


class LoginActivity(models.Model):
    """Track user login activities"""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='login_activities'
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_at = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'login_activities'
        ordering = ['-login_at']
        verbose_name = 'login activity'
        verbose_name_plural = 'login activities'
    
    def __str__(self):
        return f"{self.user.email} - {self.login_at}"