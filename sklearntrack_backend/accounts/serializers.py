# FILE: accounts/serializers.py
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile, LoginActivity

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'password', 'password_confirm',
            'full_name', 'country', 'education_level', 'field_of_study',
            'learning_goal', 'preferred_study_hours', 'timezone',
            'terms_accepted'
        ]
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        if not data.get('terms_accepted'):
            raise serializers.ValidationError("You must accept terms and conditions")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create profile
        Profile.objects.get_or_create(user=user)

        
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = Profile
        fields = [
            'avatar', 'bio', 'skill_interests',
            'email_notifications', 'weekly_summary', 'course_reminders',
            'total_study_days', 'current_streak', 'longest_streak'
        ]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'full_name', 'role',
            'country', 'education_level', 'field_of_study',
            'learning_goal', 'preferred_study_hours', 'timezone',
            'email_verified', 'profile', 'created_at'
        ]
        read_only_fields = ['id', 'email_verified', 'created_at']


class LoginActivitySerializer(serializers.ModelSerializer):
    """Serializer for login activities"""
    
    class Meta:
        model = LoginActivity
        fields = ['ip_address', 'user_agent', 'login_at', 'location']
