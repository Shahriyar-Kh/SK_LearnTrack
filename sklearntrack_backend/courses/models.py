# FILE: courses/models.py
# ============================================================================

from django.db import models
from accounts.models import User

class Course(models.Model):
    """Admin-created courses (W3Schools style)"""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    estimated_duration = models.IntegerField(help_text='Duration in hours')
    tags = models.JSONField(default=list)
    
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Chapter(models.Model):
    """Course chapters"""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chapters'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Topic(models.Model):
    """Chapter topics"""
    
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Subtopic(models.Model):
    """Topic subtopics with content"""
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='subtopics')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    # Content
    explanation = models.TextField()
    code_examples = models.JSONField(default=list)  # List of code snippets
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'subtopics'
        ordering = ['order']
    
    def __str__(self):
        return self.title


class Exercise(models.Model):
    """Practice exercises for subtopics"""
    
    EXERCISE_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice'),
        ('coding', 'Coding Challenge'),
        ('true_false', 'True/False'),
    ]
    
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE, related_name='exercises')
    title = models.CharField(max_length=255)
    question = models.TextField()
    exercise_type = models.CharField(max_length=20, choices=EXERCISE_TYPE_CHOICES)
    options = models.JSONField(default=list)  # For MCQ
    correct_answer = models.TextField()
    explanation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'exercises'
    
    def __str__(self):
        return self.title


class Enrollment(models.Model):
    """User course enrollments"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    last_accessed_subtopic = models.ForeignKey(Subtopic, on_delete=models.SET_NULL, null=True, blank=True)
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'enrollments'
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}"


class SubtopicProgress(models.Model):
    """Track user progress on subtopics"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    bookmarked = models.BooleanField(default=False)
    time_spent = models.IntegerField(default=0)  # in seconds
    
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'subtopic_progress'
        unique_together = ['user', 'subtopic']


class PersonalCourse(models.Model):
    """User-created courses for external learning"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personal_courses')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=255, help_text='Website, book, etc.')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'personal_courses'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"


class PersonalChapter(models.Model):
    """Chapters in personal courses"""
    
    personal_course = models.ForeignKey(PersonalCourse, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'personal_chapters'
        ordering = ['order']


class PersonalTopic(models.Model):
    """Topics in personal course chapters"""
    
    chapter = models.ForeignKey(PersonalChapter, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    order = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'personal_topics'
        ordering = ['order']
