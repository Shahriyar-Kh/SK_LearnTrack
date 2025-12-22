# FILE: analytics/models.py
# ============================================================================

from django.db import models
from accounts.models import User
from courses.models import Course

class StudySession(models.Model):
    """Track daily study sessions"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_sessions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    date = models.DateField()
    duration = models.IntegerField(default=0)  # in minutes
    notes_count = models.IntegerField(default=0)
    topics_completed = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'study_sessions'
        ordering = ['-date']
        unique_together = ['user', 'course', 'date']


class ActivityLog(models.Model):
    """Log user activities"""
    
    ACTION_CHOICES = [
        ('course_enrolled', 'Course Enrolled'),
        ('topic_completed', 'Topic Completed'),
        ('note_created', 'Note Created'),
        ('exercise_completed', 'Exercise Completed'),
        ('roadmap_created', 'Roadmap Created'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_logs')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'activity_logs'
        ordering = ['-created_at']


class Notification(models.Model):
    """User notifications"""
    
    NOTIFICATION_TYPES = [
        ('course_reminder', 'Course Reminder'),
        ('roadmap_deadline', 'Roadmap Deadline'),
        ('achievement', 'Achievement'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
