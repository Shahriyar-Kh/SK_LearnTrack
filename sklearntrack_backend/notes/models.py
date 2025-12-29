# FILE: notes/models.py
# ============================================================================
# Hierarchical Notes Module: Note → Chapter → Topic
# ============================================================================

from django.db import models
from accounts.models import User
from courses.models import Course, Topic as CourseTopic, Subtopic
from django.utils.text import slugify


class Note(models.Model):
    """Main Note container with chapters"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=550, blank=True)
    
    # Organization
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Course relationships
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    course_topic = models.ForeignKey(CourseTopic, on_delete=models.SET_NULL, null=True, blank=True)
    course_subtopic = models.ForeignKey(Subtopic, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    session_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'status']),
        ]
        # Ensure unique note titles per user
        constraints = [
            models.UniqueConstraint(fields=['user', 'title'], name='unique_user_note_title')
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:500]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class Chapter(models.Model):
    """Chapter within a Note"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'note_chapters'
        ordering = ['order', 'created_at']
        unique_together = ['note', 'order']
    
    def __str__(self):
        return f"{self.note.title} - {self.title}"


class TopicExplanation(models.Model):
    """Rich text explanation for a topic"""
    
    content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topic_explanations'
    
    def __str__(self):
        return f"Explanation: {self.content[:50]}..."


class TopicCodeSnippet(models.Model):
    """Code snippet for a topic"""
    
    LANGUAGES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('typescript', 'TypeScript'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('c', 'C'),
        ('csharp', 'C#'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('php', 'PHP'),
        ('ruby', 'Ruby'),
        ('swift', 'Swift'),
        ('kotlin', 'Kotlin'),
        ('sql', 'SQL'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('bash', 'Bash'),
        ('other', 'Other'),
    ]
    
    language = models.CharField(max_length=50, choices=LANGUAGES, default='python')
    code = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topic_code_snippets'
    
    def __str__(self):
        return f"{self.language}: {self.code[:30]}..."


class TopicSource(models.Model):
    """Source/reference link for a topic"""
    
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'topic_sources'
    
    def __str__(self):
        return self.title


class ChapterTopic(models.Model):
    """Topic within a Chapter"""
    
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=500)
    order = models.PositiveIntegerField(default=0)
    
    # Related components (optional)
    explanation = models.OneToOneField(
        TopicExplanation, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='topic'
    )
    code_snippet = models.OneToOneField(
        TopicCodeSnippet, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='topic'
    )
    source = models.OneToOneField(
        TopicSource, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='topic'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chapter_topics'
        ordering = ['order', 'created_at']
        unique_together = ['chapter', 'order']
    
    def __str__(self):
        return f"{self.chapter.title} - {self.name}"
    
    @property
    def has_explanation(self):
        return self.explanation is not None
    
    @property
    def has_code(self):
        return self.code_snippet is not None
    
    @property
    def has_source(self):
        return self.source is not None


# Keep existing models for backward compatibility
class NoteVersion(models.Model):
    """Version control for notes"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    snapshot = models.JSONField(default=dict)  # Full snapshot of note structure
    changes_summary = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'note_versions'
        ordering = ['-version_number']
        unique_together = ['note', 'version_number']
    
    def __str__(self):
        return f"{self.note.title} - v{self.version_number}"


class AIGeneratedContent(models.Model):
    """Track AI-generated content"""
    
    AI_ACTIONS = (
        ('generate_explanation', 'Generate Explanation'),
        ('improve_explanation', 'Improve Explanation'),
        ('summarize_explanation', 'Summarize Explanation'),
        ('generate_code', 'Generate Code'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_generations')
    topic = models.ForeignKey(ChapterTopic, on_delete=models.CASCADE, related_name='ai_generations', null=True, blank=True)
    
    action_type = models.CharField(max_length=50, choices=AI_ACTIONS)
    input_content = models.TextField()
    generated_content = models.TextField()
    
    model_used = models.CharField(max_length=100, default='gpt-4')
    tokens_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_generated_content'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.created_at}"


class NoteShare(models.Model):
    """Share notes with specific permissions"""
    
    PERMISSION_CHOICES = (
        ('view', 'Read Only'),
        ('edit', 'Can Edit'),
    )
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notes', null=True, blank=True)
    
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    is_public = models.BooleanField(default=False)
    public_slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'note_shares'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.is_public:
            return f"Public: {self.note.title}"
        return f"{self.note.title} -> {self.shared_with.username if self.shared_with else 'Public'}"