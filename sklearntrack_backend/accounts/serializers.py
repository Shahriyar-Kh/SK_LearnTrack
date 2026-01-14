# FILE: accounts/serializers.py - FIXED VERSION
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile, LoginActivity
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm',
            'full_name', 'country', 'education_level', 'field_of_study',
            'learning_goal', 'preferred_study_hours', 'timezone',
            'terms_accepted'
        ]
        extra_kwargs = {
            'terms_accepted': {'required': True},
            'email': {'required': True},
            'full_name': {'required': True},
            'country': {'required': True},
            'education_level': {'required': True},
            'field_of_study': {'required': True},
        }
    
    def validate_email(self, value):
        """Validate email is unique"""
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password strength using Django validators"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        """Validate registration data"""
        errors = {}
        
        # Check password match
        if data.get('password') != data.get('password_confirm'):
            errors['password_confirm'] = ["Passwords do not match."]
        
        # Check terms accepted
        if not data.get('terms_accepted'):
            errors['terms_accepted'] = ["You must accept the terms and conditions."]
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data
    
    def create(self, validated_data):
        """Create new user with 'student' role by default"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        # Ensure role is set to 'student' for regular registration
        validated_data['role'] = 'student'
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        logger.info(f"User created successfully: {user.email} with role: {user.role}")
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = Profile
        fields = [
            'avatar', 'bio', 'skill_interests',
            'email_notifications', 'weekly_summary', 'course_reminders',
            'total_study_days', 'current_streak', 'longest_streak', 'total_notes'
        ]
        read_only_fields = ['total_study_days', 'current_streak', 'longest_streak', 'total_notes']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details with role"""
    
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'full_name', 'role',
            'country', 'education_level', 'field_of_study',
            'learning_goal', 'preferred_study_hours', 'timezone',
            'email_verified', 'is_staff', 'is_superuser',
            'profile', 'created_at'
        ]
        read_only_fields = [
            'id', 'email_verified', 'created_at', 'username', 
            'role', 'is_staff', 'is_superuser'
        ]


class LoginActivitySerializer(serializers.ModelSerializer):
    """Serializer for login activities"""
    
    class Meta:
        model = LoginActivity
        fields = ['ip_address', 'user_agent', 'login_at', 'location']


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT serializer that accepts email and adds user data + role-based redirect"""
    
    username_field = 'email'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields.pop('username')
        self.fields['email'] = serializers.EmailField(required=True)
    
    @classmethod
    def get_token(cls, user):
        """Override to add custom claims to token"""
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['is_staff'] = user.is_staff
        token['is_superuser'] = user.is_superuser
        
        return token
    
    def validate(self, attrs):
        """Validate and authenticate user with email"""
        email = attrs.get('email', '').lower().strip()
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError({
                'detail': 'Email and password are required.'
            })
        
        # Authenticate using email
        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )
        
        if not user:
            raise serializers.ValidationError({
                'detail': 'Invalid email or password.'
            })
        
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'User account is disabled.'
            })
        
        # Update last login
        from django.utils import timezone
        user.last_login_at = timezone.now()
        user.save(update_fields=['last_login_at'])
        
        # Get tokens using parent class method
        refresh = self.get_token(user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data,
            'redirect': self.get_redirect_url(user)
        }
        
        logger.info(f"User logged in: {user.email} with role: {user.role}")
        
        return data
    
    def get_redirect_url(self, user):
        """Determine redirect URL based on user role"""
        if user.role == 'admin' or user.is_staff or user.is_superuser:
            return '/admin-dashboard'
        # All non-admin users (including 'student' role) go to user dashboard
        return '/dashboard'


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth authentication"""
    credential = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True)


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        try:
            validate_password(data['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })
        return data


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile after OAuth"""
    
    class Meta:
        model = User
        fields = [
            'full_name', 'country', 'education_level', 
            'field_of_study', 'learning_goal', 'preferred_study_hours'
        ]
    
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        return instance