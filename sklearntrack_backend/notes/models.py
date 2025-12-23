# FILE: notes/models.py
# ============================================================================

from django.db import models
from accounts.models import User
from courses.models import Course, Topic, Subtopic
from django.utils.text import slugify
import json


class NoteSource(models.Model):
    """Sources referenced in notes (YouTube, URLs, PDFs, etc.)"""
    
    SOURCE_TYPES = (
        ('youtube', 'YouTube Video'),
        ('url', 'Website/URL'),
        ('pdf', 'PDF Document'),
        ('article', 'Article'),
        ('book', 'Book'),
        ('other', 'Other'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_sources')
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    title = models.CharField(max_length=500)
    url = models.URLField(max_length=1000, blank=True)
    author = models.CharField(max_length=255, blank=True)
    date = models.DateField(null=True, blank=True)
    reference_number = models.IntegerField()  # For IEEE citation [1], [2], etc.
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)  # Store additional info
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'note_sources'
        ordering = ['reference_number']
        unique_together = ['user', 'reference_number']
    
    def __str__(self):
        return f"[{self.reference_number}] {self.title}"


class Note(models.Model):
    """Enhanced notes with rich text, references, and versioning"""
    
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=550, blank=True)
    
    # Rich content stored as JSON (supports structured format)
    content = models.TextField()  # Main content in HTML or JSON
    content_json = models.JSONField(default=dict, blank=True)  # Structured content
    
    # Organization
    tags = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Relationships
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True)
    subtopic = models.ForeignKey(Subtopic, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Sources/References
    sources = models.ManyToManyField(NoteSource, blank=True, related_name='notes')
    
    # Table of Contents
    toc = models.JSONField(default=list, blank=True)  # Auto-generated TOC
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Learning session tracking
    session_date = models.DateField(null=True, blank=True)
    
    class Meta:
        db_table = 'notes'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['session_date']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:500]
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def generate_toc(self):
        """Auto-generate table of contents from content"""
        # Implementation depends on content structure
        # Parse HTML/JSON and extract headings
        pass


class NoteVersion(models.Model):
    """Version control for notes"""
    
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    content = models.TextField()
    content_json = models.JSONField(default=dict, blank=True)
    
    # Change tracking
    changes_summary = models.TextField(blank=True)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'note_versions'
        ordering = ['-version_number']
        unique_together = ['note', 'version_number']
    
    def __str__(self):
        return f"{self.note.title} - v{self.version_number}"


class CodeSnippet(models.Model):
    """Code snippets with syntax highlighting"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_snippets')
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='code_snippets', null=True, blank=True)
    
    title = models.CharField(max_length=255)
    language = models.CharField(max_length=50)  # python, javascript, etc.
    code = models.TextField()
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Organization
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'code_snippets'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class NoteTemplate(models.Model):
    """Templates for different types of notes"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_templates', null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    template_content = models.JSONField(default=dict)
    
    # Whether it's a system template or user-created
    is_system = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'note_templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DailyNoteReport(models.Model):
    """Daily automated learning reports"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField()
    
    # Report data
    notes_created = models.IntegerField(default=0)
    notes_updated = models.IntegerField(default=0)
    topics_covered = models.JSONField(default=list, blank=True)
    time_spent_minutes = models.IntegerField(default=0)
    
    # AI Summary
    ai_summary = models.TextField(blank=True)
    
    # PDF generation
    pdf_file = models.FileField(upload_to='daily_reports/', blank=True, null=True)
    
    # Email status
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'daily_note_reports'
        ordering = ['-report_date']
        unique_together = ['user', 'report_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.report_date}"


class AIGeneratedNote(models.Model):
    """Track AI-generated note content"""
    
    AI_ACTIONS = (
        ('summarize_short', 'Short Summary'),
        ('summarize_medium', 'Medium Summary'),
        ('summarize_detailed', 'Detailed Summary'),
        ('expand', 'Content Expansion'),
        ('rewrite', 'Rewrite for Clarity'),
        ('breakdown', 'Topic Breakdown'),
        ('from_transcript', 'From YouTube Transcript'),
        ('from_text', 'From Raw Text'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_notes')
    note = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True, related_name='ai_generations')
    
    action_type = models.CharField(max_length=50, choices=AI_ACTIONS)
    source_content = models.TextField()  # Original content used
    generated_content = models.TextField()  # AI output
    
    # Tracking
    approved = models.BooleanField(default=False)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    # AI model info
    model_used = models.CharField(max_length=100, blank=True)
    tokens_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_generated_notes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_type_display()} - {self.created_at}"


class YouTubeTranscript(models.Model):
    """Store YouTube video transcripts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='youtube_transcripts')
    video_url = models.URLField(max_length=500)
    video_id = models.CharField(max_length=100)
    video_title = models.CharField(max_length=500, blank=True)
    
    # Transcript data
    transcript = models.TextField()
    timestamps = models.JSONField(default=list, blank=True)  # List of {time, text}
    
    # Processing
    processed = models.BooleanField(default=False)
    notes_generated = models.ForeignKey(Note, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'youtube_transcripts'
        ordering = ['-created_at']
        unique_together = ['user', 'video_id']
    
    def __str__(self):
        return f"{self.video_title or self.video_id}"


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
    
    # Public sharing
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