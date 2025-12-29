# FILE: accounts/models.py
# ============================================================================
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom user manager that uses email instead of username"""
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        
        # Set default values
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'student')
        
        # Auto-generate username if not provided
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
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


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
    
    # Override email to be unique and required
    email = models.EmailField(_('email address'), unique=True)
    # Make username optional but unique
    username = models.CharField(max_length=150, unique=True, blank=True)
    
    # Role field with default 'student'
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    
    # Additional registration fields
    full_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100, blank=True)
    education_level = models.CharField(max_length=50, choices=EDUCATION_LEVEL_CHOICES, blank=True)
    field_of_study = models.CharField(max_length=255, blank=True)
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
    
    # Use custom manager
    objects = CustomUserManager()
    
    # Use email for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']  # Required for createsuperuser (email is automatically included)
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        # Normalize email to lowercase
        if self.email:
            self.email = self.email.lower().strip()
        
        # Auto-generate username from email if not provided
        if not self.username:
            base_username = self.email.split('@')[0]
            username = base_username
            counter = 1
            
            # Ensure unique username
            while User.objects.filter(username=username).exclude(pk=self.pk).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            self.username = username
        
        # Set role to 'admin' if user is staff or superuser
        if self.is_staff or self.is_superuser:
            self.role = 'admin'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.email


class Profile(models.Model):
    """Extended profile information for users"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
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