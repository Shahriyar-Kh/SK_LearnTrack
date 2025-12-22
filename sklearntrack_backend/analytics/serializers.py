# FILE: analytics/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import StudySession, ActivityLog, Notification


class StudySessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudySession
        fields = ['id', 'course', 'date', 'duration', 'notes_count', 'topics_completed']


class ActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ['id', 'action', 'details', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'read', 'created_at']

