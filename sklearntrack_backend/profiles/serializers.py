# FILE: profiles/serializers.py
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile, NotificationSettings, ProfileActivityLog

User = get_user_model()


class NotificationSettingsSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences"""
    
    class Meta:
        model = NotificationSettings
        fields = [
            'email_notifications',
            'weekly_summary',
            'course_reminders',
            'achievement_alerts',
            'community_updates',
        ]
    
    def update(self, instance, validated_data):
        """Update notification settings and log activity"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Log activity
        ProfileActivityLog.objects.create(
            profile=instance.profile,
            activity_type='notifications_updated',
            description='Notification settings updated'
        )
        
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    """Main profile serializer with nested notification settings"""
    
    # User fields (read-only)
    email = serializers.EmailField(source='user.email', read_only=True)
    fullName = serializers.CharField(source='user.full_name', max_length=200)
    country = serializers.CharField(source='user.country', max_length=100)
    educationLevel = serializers.ChoiceField(
        source='user.education_level',
        choices=Profile.EDUCATION_LEVELS,
        required=False
    )
    fieldOfStudy = serializers.CharField(
        source='user.field_of_study',
        max_length=255,
        required=False
    )
    
    # Profile fields (match React state keys exactly)
    avatar = serializers.SerializerMethodField()
    learningGoal = serializers.CharField(
        source='learning_goal',
        max_length=1000,
        required=False,
        allow_blank=True
    )
    preferredStudyHours = serializers.IntegerField(
        source='preferred_study_hours',
        min_value=1,
        max_value=12
    )
    skillInterests = serializers.ListField(
        source='skill_interests',
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    
    # Statistics (read-only)
    totalStudyDays = serializers.IntegerField(source='total_study_days', read_only=True)
    currentStreak = serializers.IntegerField(source='current_streak', read_only=True)
    longestStreak = serializers.IntegerField(source='longest_streak', read_only=True)
    totalNotes = serializers.IntegerField(source='total_notes', read_only=True)
    
    # Nested notification settings
    notifications = NotificationSettingsSerializer(
        source='notification_settings',
        read_only=True
    )
    
    # Metadata
    emailVerified = serializers.BooleanField(source='user.email_verified', read_only=True)
    accountCreated = serializers.DateTimeField(source='user.created_at', read_only=True)
    lastLogin = serializers.DateTimeField(source='user.last_login_at', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            # User fields
            'email',
            'fullName',
            'country',
            'educationLevel',
            'fieldOfStudy',
            
            # Profile fields
            'bio',
            'avatar',
            'learningGoal',
            'preferredStudyHours',
            'timezone',
            'skillInterests',
            
            # Statistics
            'totalStudyDays',
            'currentStreak',
            'longestStreak',
            'totalNotes',
            
            # Settings
            'notifications',
            
            # Metadata
            'emailVerified',
            'accountCreated',
            'lastLogin',
        ]
    
    def get_avatar(self, obj):
        """Get avatar URL or None"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    
    def validate_fullName(self, value):
        """Validate full name length"""
        if len(value) < 2:
            raise serializers.ValidationError('Full name must be at least 2 characters')
        if len(value) > 200:
            raise serializers.ValidationError('Full name cannot exceed 200 characters')
        return value.strip()
    
    def validate_bio(self, value):
        """Validate bio length"""
        if len(value) > 2000:
            raise serializers.ValidationError('Bio cannot exceed 2000 characters')
        return value.strip()
    
    def validate_skillInterests(self, value):
        """Validate skill interests"""
        if len(value) > 30:
            raise serializers.ValidationError('Cannot have more than 30 skill interests')
        
        # Remove duplicates and validate each skill
        unique_skills = []
        for skill in value:
            skill = skill.strip()
            if skill and skill not in unique_skills:
                if len(skill) > 50:
                    raise serializers.ValidationError('Skill name cannot exceed 50 characters')
                unique_skills.append(skill)
        
        return unique_skills
    
    def update(self, instance, validated_data):
        """Update profile and related user fields"""
        # Extract user data
        user_data = {}
        if 'user' in validated_data:
            user_fields = validated_data.pop('user')
            user_data = {
                'full_name': user_fields.get('full_name'),
                'country': user_fields.get('country'),
                'education_level': user_fields.get('education_level'),
                'field_of_study': user_fields.get('field_of_study'),
            }
        
        # Update user fields
        if user_data:
            for attr, value in user_data.items():
                if value is not None:
                    setattr(instance.user, attr, value)
            instance.user.save()
        
        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Log activity
        ProfileActivityLog.objects.create(
            profile=instance,
            activity_type='profile_updated',
            description='Profile information updated'
        )
        
        return instance


class AvatarUploadSerializer(serializers.Serializer):
    """Serializer for avatar upload"""
    
    avatar = serializers.ImageField(required=True)
    
    def validate_avatar(self, value):
        """Validate avatar image"""
        # Check file size (5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Image file size cannot exceed 5MB')
        
        # Check file extension
        allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
        ext = value.name.split('.')[-1].lower()
        if ext not in allowed_extensions:
            raise serializers.ValidationError(
                f'Unsupported file format. Allowed: {", ".join(allowed_extensions)}'
            )
        
        return value


class PreferencesSerializer(serializers.ModelSerializer):
    """Serializer for study preferences only"""
    
    learningGoal = serializers.CharField(
        source='learning_goal',
        max_length=1000,
        required=False,
        allow_blank=True
    )
    preferredStudyHours = serializers.IntegerField(
        source='preferred_study_hours',
        min_value=1,
        max_value=12
    )
    skillInterests = serializers.ListField(
        source='skill_interests',
        child=serializers.CharField(max_length=50),
        required=False,
        allow_empty=True
    )
    
    class Meta:
        model = Profile
        fields = [
            'learningGoal',
            'preferredStudyHours',
            'timezone',
            'skillInterests',
        ]
    
    def update(self, instance, validated_data):
        """Update preferences and log activity"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Log activity
        ProfileActivityLog.objects.create(
            profile=instance,
            activity_type='preferences_updated',
            description='Study preferences updated'
        )
        
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(required=True, write_only=True)
    
    def validate_old_password(self, value):
        """Validate old password is correct"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect')
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    
    def validate(self, data):
        """Validate passwords match"""
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'Passwords do not match'
            })
        
        # Check new password is different from old
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from current password'
            })
        
        return data


class ActivitySummarySerializer(serializers.Serializer):
    """Serializer for account activity summary"""
    
    totalStudyDays = serializers.IntegerField()
    totalNotes = serializers.IntegerField()
    activeCourses = serializers.IntegerField()
    currentStreak = serializers.IntegerField()
    longestStreak = serializers.IntegerField()
    lastLogin = serializers.DateTimeField()
    accountCreated = serializers.DateTimeField()
    emailVerified = serializers.BooleanField()


class ActivityLogSerializer(serializers.ModelSerializer):
    """Serializer for activity logs"""
    
    activityType = serializers.CharField(source='activity_type')
    ipAddress = serializers.IPAddressField(source='ip_address')
    userAgent = serializers.CharField(source='user_agent')
    createdAt = serializers.DateTimeField(source='created_at')
    
    class Meta:
        model = ProfileActivityLog
        fields = ['activityType', 'description', 'ipAddress', 'userAgent', 'createdAt']