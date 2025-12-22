# FILE: notes/models.py
# ============================================================================

from django.db import models
from accounts.models import User
from courses.models import Course, Topic, Subtopic

class Note(models.Model):
    """User notes with rich text"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    tags = models.JSONField(default=list)
    
    # Optional relationships
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title


class CodeSnippet(models.Model):
    """Code snippets with syntax highlighting"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_snippets')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='code_snippets', null=True, blank=True)
    
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    code = models.TextField()
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'code_snippets'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NoteHistory(models.Model):
    """Track note version history"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='history')
    content = models.TextField()
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'note_history'
        ordering = ['-saved_at']

