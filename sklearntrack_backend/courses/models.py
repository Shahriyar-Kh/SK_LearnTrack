# FILE: courses/models.py
# ============================================================================
# Advanced Course Management System - Models
# ============================================================================
# Enterprise-grade course structure with versioning, auditing, and draft workflow
# ============================================================================

from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
import json
from datetime import datetime


class CourseStatus(models.TextChoices):
    """Course publication status workflow"""
    DRAFT = 'draft', 'Draft'
    READY = 'ready', 'Ready for Publishing'
    PUBLISHED = 'published', 'Published'
    ARCHIVED = 'archived', 'Archived'


class DifficultyLevel(models.TextChoices):
    """Course difficulty"""
    BEGINNER = 'beginner', 'Beginner'
    INTERMEDIATE = 'intermediate', 'Intermediate'
    ADVANCED = 'advanced', 'Advanced'


class TopicStatus(models.TextChoices):
    """Topic completion status"""
    NOT_STARTED = 'not_started', 'Not Started'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'


class QuestionType(models.TextChoices):
    """Quiz question types"""
    MULTIPLE_CHOICE = 'multiple_choice', 'Multiple Choice'
    TRUE_FALSE = 'true_false', 'True/False'
    SHORT_ANSWER = 'short_answer', 'Short Answer'


class AssetType(models.TextChoices):
    """Content asset types"""
    IMAGE = 'image', 'Image'
    CODE = 'code', 'Source Code'
    DIAGRAM = 'diagram', 'Diagram'
    PDF = 'pdf', 'PDF Document'
    VIDEO = 'video', 'Video Link'


# ============================================================================
# CORE COURSE MODELS
# ============================================================================

class Course(models.Model):
    """
    Master course container.
    
    Features:
    - Draft-first workflow: starts as DRAFT, explicitly published to PUBLISHED
    - SEO optimized with custom slugs and metadata
    - Versioning: full snapshot taken on publish
    - Soft deletes: archived courses retained for audit trail
    - Admin auditing: tracks who created/modified
    """
    
    # Basic info
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, max_length=255, db_index=True)
    description = models.TextField(help_text='Course overview for listing page')
    category = models.CharField(
        max_length=100, 
        db_index=True,
        default='other',
        help_text='Course category for filtering'
    )
    
    # Media
    thumbnail = models.ImageField(
        upload_to='courses/thumbnails/%Y/%m/',
        null=True,
        blank=True,
        help_text='Course card image (optimal: 400x300px)'
    )
    
    # Content metadata
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )
    estimated_hours = models.IntegerField(
        default=10,
        help_text='Estimated time to complete (calculated from topics)'
    )
    tags = models.JSONField(
        default=list,
        help_text='Array of topic tags for search'
    )
    
    # SEO metadata
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text='SEO title for search engines (< 60 chars)'
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text='SEO meta description (< 160 chars)'
    )
    
    # Status & workflow
    status = models.CharField(
        max_length=20,
        choices=CourseStatus.choices,
        default=CourseStatus.DRAFT,
        db_index=True
    )
    
    # Auditing
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Don't allow deleting user with courses
        related_name='courses_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses_updated'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)
    
    class Meta:
        db_table = 'courses'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category']),
        ]
        ordering = ['-published_at', '-created_at']
        permissions = [
            ('can_publish_course', 'Can publish courses to production'),
            ('can_view_audit_log', 'Can view course audit logs'),
            ('can_use_ai_tools', 'Can use AI-assisted content generation'),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from title if not provided"""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    @property
    def is_published(self):
        """Convenience property"""
        return self.status == CourseStatus.PUBLISHED
    
    def get_student_view_data(self):
        """Serializable data for students (caching friendly)"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'difficulty': self.difficulty,
            'estimated_hours': self.estimated_hours,
            'thumbnail_url': self.thumbnail.url if self.thumbnail else None,
            'tags': self.tags,
            'chapter_count': self.chapters.count(),
            'topic_count': sum(ch.topics.count() for ch in self.chapters.all()),
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }


class CourseChapter(models.Model):
    """
    Chapters organize topics within a course.
    
    Features:
    - Ordered: explicit order_index for drag-drop reordering
    - Soft deletable: marked as archived
    """
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters'
    )
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, help_text='Chapter overview')
    order_index = models.IntegerField(default=0, db_index=True)
    
    is_archived = models.BooleanField(default=False, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_chapters'
        unique_together = [['course', 'slug']]
        indexes = [
            models.Index(fields=['course', 'order_index']),
            models.Index(fields=['is_archived']),
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class CourseTopic(models.Model):
    """
    Individual topics (lessons) within a chapter.
    
    Features:
    - Rich markdown content
    - Ordered within chapter
    - SEO-friendly URLs
    - Estimated duration
    - Can have quiz, code examples, assets
    """
    
    chapter = models.ForeignKey(
        CourseChapter,
        on_delete=models.CASCADE,
        related_name='topics'
    )
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=255)
    description = models.TextField(blank=True, help_text='Brief topic summary')
    
    # Main content
    content = models.TextField(
        help_text='Markdown content with code blocks, images via ![](asset_id)'
    )
    estimated_minutes = models.IntegerField(
        default=15,
        help_text='Estimated time for student to complete'
    )
    
    # Ordering
    order_index = models.IntegerField(default=0, db_index=True)
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Metadata
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.BEGINNER
    )
    key_concepts = models.JSONField(
        default=list,
        help_text='Array of main concepts covered'
    )
    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        help_text='Topics that should be completed first'
    )
    
    # Status
    is_archived = models.BooleanField(default=False, db_index=True)
    is_ai_generated = models.BooleanField(
        default=False,
        help_text='True if created/substantially modified by AI'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_topics'
        unique_together = [['chapter', 'slug']]
        indexes = [
            models.Index(fields=['chapter', 'order_index']),
            models.Index(fields=['is_archived']),
            models.Index(fields=['is_ai_generated']),
        ]
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.chapter} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_student_view_data(self):
        """Data for student topic viewing"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'content': self.content,  # In production, render markdown to HTML
            'estimated_minutes': self.estimated_minutes,
            'difficulty': self.difficulty,
            'key_concepts': self.key_concepts,
            'assets': list(self.assets.values('id', 'type', 'name', 'file', 'url')),
            'code_examples': list(self.code_snippets.values('id', 'language', 'code', 'description')),
            'has_quiz': self.quiz.exists() if hasattr(self, 'quiz') else False,
        }


# ============================================================================
# CONTENT ASSETS
# ============================================================================

class TopicAsset(models.Model):
    """
    Images, diagrams, code, PDFs embedded in topics.
    
    Features:
    - Multiple asset types
    - Auto-generate preview for images
    - Track asset size for storage monitoring
    """
    
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name='assets'
    )
    
    type = models.CharField(
        max_length=20,
        choices=AssetType.choices,
        db_index=True
    )
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='topics/assets/%Y/%m/')
    
    # Metadata
    description = models.TextField(blank=True)
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        help_text='Alt text for images (SEO + accessibility)'
    )
    
    # Storage tracking
    file_size = models.BigIntegerField(null=True, blank=True)
    
    order_index = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'topic_assets'
        ordering = ['order_index']
        indexes = [
            models.Index(fields=['type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        """Store file size for quota tracking"""
        if self.file:
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def url(self):
        """Return file URL"""
        return self.file.url if self.file else None


class SourceCode(models.Model):
    """
    Code examples/snippets embedded in topics.
    
    Features:
    - Multiple languages with syntax highlighting
    - Can be entire code file or snippet
    - Versioning for different implementations
    """
    
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name='code_snippets'
    )
    
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('sql', 'SQL'),
        ('java', 'Java'),
        ('cpp', 'C++'),
        ('bash', 'Bash'),
        ('other', 'Other'),
    ]
    
    language = models.CharField(
        max_length=50,
        choices=LANGUAGE_CHOICES,
        db_index=True
    )
    code = models.TextField()
    description = models.TextField(blank=True, help_text='Explanation of what this code does')
    title = models.CharField(max_length=255, blank=True)
    
    # Execution support (future)
    is_executable = models.BooleanField(
        default=False,
        help_text='Can this code be executed by students?'
    )
    
    order_index = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'source_code'
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.title} ({self.language})"


# ============================================================================
# QUIZ & ASSESSMENT
# ============================================================================

class TopicQuiz(models.Model):
    """
    Practice quiz for a topic (not graded, for learning).
    
    Features:
    - Multiple questions with multiple choice, true/false, etc.
    - Immediate feedback with explanations
    - Optional: track student attempts
    """
    
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name='quiz',  # Allows topic.quiz.exists()
    )
    
    title = models.CharField(max_length=255, default="Practice Quiz")
    description = models.TextField(blank=True)
    
    # Scoring
    passing_score = models.FloatField(
        default=0.7,
        help_text='Percentage required to pass (0.0-1.0)'
    )
    
    # Control
    is_ai_generated = models.BooleanField(default=False)
    shuffle_questions = models.BooleanField(default=True)
    show_feedback_immediately = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topic_quizzes'
        unique_together = [['topic']]  # One quiz per topic
    
    def __str__(self):
        return f"Quiz: {self.topic.title}"
    
    @property
    def question_count(self):
        return self.questions.count()
    
    def get_student_data(self):
        """Serializable quiz data (without correct answers)"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'question_count': self.question_count,
            'passing_score': self.passing_score,
            'questions': [q.get_student_data() for q in self.questions.all()],
        }


class QuizQuestion(models.Model):
    """
    Individual quiz question.
    """
    
    quiz = models.ForeignKey(
        TopicQuiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE
    )
    
    question_text = models.TextField()
    explanation = models.TextField(
        blank=True,
        help_text='Shown to student after answering'
    )
    
    order_index = models.IntegerField(default=0)
    difficulty_multiplier = models.FloatField(
        default=1.0,
        help_text='Weight for scoring'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'quiz_questions'
        ordering = ['order_index']
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}..."
    
    def get_student_data(self):
        """Question data without revealing correct answers"""
        return {
            'id': self.id,
            'type': self.type,
            'question_text': self.question_text,
            'choices': [c.get_student_data() for c in self.choices.all()],
        }


class QuizChoice(models.Model):
    """
    Answer option for a question.
    """
    
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    
    choice_text = models.TextField()
    is_correct = models.BooleanField(default=False, db_index=True)
    order_index = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'quiz_choices'
        ordering = ['order_index']
    
    def __str__(self):
        return f"{self.choice_text[:30]}... {'✓' if self.is_correct else '✗'}"
    
    def get_student_data(self):
        """Choice data without correct answer"""
        return {
            'id': self.id,
            'choice_text': self.choice_text,
        }


# ============================================================================
# ENROLLMENT & PROGRESS TRACKING
# ============================================================================

class CourseEnrollment(models.Model):
    """
    Student enrollment in a course.
    
    Features:
    - Tracks enrollment date, start/completion dates
    - Overall progress percentage
    - Status: active, completed, dropped, paused
    """
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('paused', 'Paused'),
    ]
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    # Progress tracking
    progress_percentage = models.FloatField(
        default=0.0,
        help_text='Percentage of topics completed'
    )
    completed_topics_count = models.IntegerField(default=0)
    
    # Timestamps
    enrolled_at = models.DateTimeField(auto_now_add=True, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_enrollments'
        unique_together = [['student', 'course']]
        indexes = [
            models.Index(fields=['student', 'status']),
            models.Index(fields=['course', 'status']),
        ]
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class TopicProgress(models.Model):
    """
    Student's progress on individual topics.
    
    Features:
    - Tracks completion status
    - Time spent
    - Quiz attempts
    - Notes
    """
    
    enrollment = models.ForeignKey(
        CourseEnrollment,
        on_delete=models.CASCADE,
        related_name='topic_progress'
    )
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name='student_progress'
    )
    
    status = models.CharField(
        max_length=20,
        choices=TopicStatus.choices,
        default=TopicStatus.NOT_STARTED,
        db_index=True
    )
    
    # Engagement metrics
    time_spent_minutes = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topic_progress'
        unique_together = [['enrollment', 'topic']]
        indexes = [
            models.Index(fields=['enrollment', 'status']),
            models.Index(fields=['topic']),
        ]
    
    def __str__(self):
        return f"{self.enrollment.student} - {self.topic.title}: {self.get_status_display()}"


class QuizAttempt(models.Model):
    """
    Student's attempt at a quiz.
    
    Features:
    - Tracks answers and score
    - Timestamps for analytics
    - Question-level performance
    """
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        TopicQuiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # Scoring
    score = models.FloatField(
        help_text='Percentage scored (0.0-1.0)'
    )
    passed = models.BooleanField(db_index=True)
    
    # Answers (JSON for flexibility)
    answers = models.JSONField(
        default=dict,
        help_text='{ question_id: choice_id }'
    )
    
    # Time tracking
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(auto_now=True)
    time_spent_minutes = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'quiz_attempts'
        indexes = [
            models.Index(fields=['student', 'quiz']),
            models.Index(fields=['passed']),
        ]
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.student} - {self.quiz.topic}: {self.score*100:.1f}%"


class StudentNote(models.Model):
    """
    Student's personal notes for a topic.
    
    Features:
    - Markdown format
    - Auto-saves
    - Can be shared (future)
    """
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student_notes'
    )
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name='student_notes'
    )
    
    content = models.TextField(help_text='Markdown format')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_notes'
        unique_together = [['student', 'topic']]
    
    def __str__(self):
        return f"Note: {self.student} on {self.topic}"


class TopicBookmark(models.Model):
    """
    Student's bookmarked topics (for later review).
    
    Features:
    - Quick access to important topics
    - Timestamped for sorting
    """
    
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_topics'
    )
    topic = models.ForeignKey(
        CourseTopic,
        on_delete=models.CASCADE,
        related_name='bookmarked_by'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'topic_bookmarks'
        unique_together = [['student', 'topic']]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} bookmarked {self.topic}"


# ============================================================================
# VERSIONING & AUDITING
# ============================================================================

class CourseVersion(models.Model):
    """
    Snapshot of entire course structure at publication time.
    
    Features:
    - Full course JSON stored for rollback
    - Metadata about what changed
    - Comparison with previous version
    """
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    
    version_number = models.IntegerField()
    snapshot = models.JSONField(
        help_text='Complete course structure snapshot'
    )
    change_summary = models.TextField(
        blank=True,
        help_text='What changed in this version'
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'course_versions'
        unique_together = [['course', 'version_number']]
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.course} v{self.version_number}"


class AuditLog(models.Model):
    """
    Complete audit trail of all changes to courses.
    
    Features:
    - Tracks who, what, when, and why
    - Used for compliance and debugging
    - Can identify problematic changes
    """
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted/Archived'),
        ('publish', 'Published'),
        ('unpublish', 'Unpublished'),
        ('duplicate', 'Duplicated'),
        ('ai_generate', 'AI Generated'),
    ]
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='audit_logs'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='course_audit_logs'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, db_index=True)
    object_type = models.CharField(
        max_length=50,
        help_text='Course, Chapter, Topic, etc.'
    )
    object_id = models.IntegerField(help_text='ID of affected object')
    
    changes = models.JSONField(
        default=dict,
        help_text='{ "field": {"old": value, "new": value} }'
    )
    reason = models.TextField(blank=True, help_text='Why this change was made')
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['course', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} {self.action} {self.object_type}({self.object_id})"
