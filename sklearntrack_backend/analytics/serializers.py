# FILE: analytics/serializers.py
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class DashboardOverviewSerializer(serializers.Serializer):
    """Dashboard overview data with real + placeholder values"""
    
    # User Info (Real)
    user_name = serializers.CharField()
    user_email = serializers.CharField()
    user_avatar = serializers.SerializerMethodField()
    
    # Profile Stats (Real)
    profile_completed = serializers.BooleanField()
    email_verified = serializers.BooleanField()
    
    # Study Stats (Real where available)
    total_notes = serializers.IntegerField()
    total_study_days = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    
    # Module Stats (Mixed: Real + Dummy)
    active_courses = serializers.IntegerField()  # DUMMY for now
    topics_completed = serializers.IntegerField()  # Real from notes
    weekly_study_time = serializers.IntegerField()  # DUMMY for now
    
    # Achievements (DUMMY for now)
    total_achievements = serializers.IntegerField()
    
    # Recent Activity (Real)
    last_login = serializers.DateTimeField(allow_null=True)
    account_created = serializers.DateTimeField()
    
    def get_user_avatar(self, obj):
        """Get user avatar URL"""
        request = self.context.get('request')
        avatar = obj.get('user_avatar')
        
        if avatar and request:
            return request.build_absolute_uri(avatar)
        return None


class RecentNoteSerializer(serializers.Serializer):
    """Serializer for recent notes in dashboard"""
    id = serializers.IntegerField()
    title = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    tags = serializers.ListField(child=serializers.CharField())
    chapter_count = serializers.IntegerField()
    status = serializers.CharField()
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Add human-readable time difference
        now = timezone.now()
        updated = instance.get('updated_at')
        if updated:
            diff = now - updated
            if diff < timedelta(hours=1):
                data['time_ago'] = f"{diff.seconds // 60} minutes ago"
            elif diff < timedelta(days=1):
                data['time_ago'] = f"{diff.seconds // 3600} hours ago"
            else:
                data['time_ago'] = f"{diff.days} days ago"
        return data


class QuickActionSerializer(serializers.Serializer):
    """Serializer for dashboard quick actions"""
    id = serializers.CharField()
    label = serializers.CharField()
    icon = serializers.CharField()
    route = serializers.CharField()
    enabled = serializers.BooleanField()
    badge = serializers.IntegerField(allow_null=True, required=False)


class TodayTaskSerializer(serializers.Serializer):
    """Serializer for today's planned tasks"""
    id = serializers.IntegerField()
    task = serializers.CharField()
    time = serializers.CharField()
    completed = serializers.BooleanField()
    priority = serializers.CharField()  # low, medium, high