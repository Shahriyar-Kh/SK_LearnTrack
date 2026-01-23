# FILE: roadmaps/models.py
# ============================================================================

from django.db import models
from django.conf import settings
from courses.models import Course, CourseTopic
from notes.models import Note

class Roadmap(models.Model):
    """User learning roadmaps"""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='roadmaps')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'roadmaps'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class Milestone(models.Model):
    """Roadmap milestones"""
    
    roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'milestones'
        ordering = ['order']


class RoadmapTask(models.Model):
    """Tasks within milestones"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    milestone = models.ForeignKey(Milestone, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    completed = models.BooleanField(default=False)
    
    # Optional links
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(CourseTopic, on_delete=models.SET_NULL, null=True, blank=True)
    note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True)
    
    due_date = models.DateField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'roadmap_tasks'
        ordering = ['due_date', '-priority']
