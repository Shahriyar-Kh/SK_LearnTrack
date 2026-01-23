# FILE: courses/serializers.py
# ============================================================================
# DRF Serializers for Course Management System
# ============================================================================
# Hierarchical serializers supporting admin creation & student viewing
# ============================================================================

from rest_framework import serializers
from django.utils.text import slugify
from django.utils import timezone
from .models import (
    Course, CourseChapter, CourseTopic, TopicAsset, SourceCode,
    TopicQuiz, QuizQuestion, QuizChoice,
    CourseEnrollment, TopicProgress, QuizAttempt, StudentNote, TopicBookmark,
    CourseVersion, AuditLog,
    CourseStatus, DifficultyLevel, TopicStatus, AssetType, QuestionType
)


# ============================================================================
# QUIZ & ASSESSMENT SERIALIZERS
# ============================================================================

class QuizChoiceSerializer(serializers.ModelSerializer):
    """Quiz choice - hides correct answer from students"""
    
    class Meta:
        model = QuizChoice
        fields = ['id', 'choice_text', 'order_index']


class QuizChoiceAdminSerializer(serializers.ModelSerializer):
    """Admin view - includes correct answer"""
    
    class Meta:
        model = QuizChoice
        fields = ['id', 'choice_text', 'is_correct', 'order_index']


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Quiz question - student view (no answers)"""
    choices = QuizChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'type', 'question_text', 'choices', 'order_index']


class QuizQuestionAdminSerializer(serializers.ModelSerializer):
    """Admin view - full data"""
    choices = QuizChoiceAdminSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'type', 'question_text', 'explanation', 'choices', 
                  'order_index', 'difficulty_multiplier']


class TopicQuizSerializer(serializers.ModelSerializer):
    """Quiz for students - questions without answers"""
    questions = QuizQuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TopicQuiz
        fields = ['id', 'title', 'description', 'question_count', 'passing_score', 
                  'show_feedback_immediately', 'questions']
    
    def get_question_count(self, obj):
        return obj.questions.count()


class TopicQuizAdminSerializer(serializers.ModelSerializer):
    """Quiz for admins - full details"""
    questions = QuizQuestionAdminSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TopicQuiz
        fields = ['id', 'title', 'description', 'question_count', 'passing_score',
                  'shuffle_questions', 'show_feedback_immediately', 
                  'is_ai_generated', 'questions', 'created_at', 'updated_at']
    
    def get_question_count(self, obj):
        return obj.questions.count()


class TopicQuizWriteSerializer(serializers.ModelSerializer):
    """Writable quiz serializer for creation/update"""
    questions = QuizQuestionAdminSerializer(many=True, required=False)
    
    class Meta:
        model = TopicQuiz
        fields = ['title', 'description', 'passing_score', 'shuffle_questions',
                  'show_feedback_immediately', 'is_ai_generated', 'questions']
    
    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = TopicQuiz.objects.create(**validated_data)
        
        # Bulk create questions
        for q_data in questions_data:
            choices_data = q_data.pop('choices', [])
            question = QuizQuestion.objects.create(quiz=quiz, **q_data)
            for c_data in choices_data:
                QuizChoice.objects.create(question=question, **c_data)
        
        return quiz


# ============================================================================
# ASSET & CODE SERIALIZERS
# ============================================================================

class TopicAssetSerializer(serializers.ModelSerializer):
    """Topic assets (images, diagrams, PDFs)"""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = TopicAsset
        fields = ['id', 'type', 'name', 'description', 'alt_text', 'url', 
                  'order_index', 'created_at']
    
    def get_url(self, obj):
        """Generate full URL for asset"""
        if obj and obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class SourceCodeSerializer(serializers.ModelSerializer):
    """Code examples/snippets"""
    
    class Meta:
        model = SourceCode
        fields = ['id', 'language', 'code', 'description', 'title', 
                  'is_executable', 'order_index', 'created_at']


# ============================================================================
# TOPIC SERIALIZERS
# ============================================================================

class CourseTopicListSerializer(serializers.ModelSerializer):
    """Minimal topic data for lists"""
    
    class Meta:
        model = CourseTopic
        fields = ['id', 'title', 'slug', 'order_index', 'estimated_minutes', 
                  'difficulty', 'is_archived']


class CourseTopicDetailSerializer(serializers.ModelSerializer):
    """Full topic detail for student viewing"""
    assets = TopicAssetSerializer(many=True, read_only=True)
    code_snippets = SourceCodeSerializer(many=True, read_only=True)
    quiz = TopicQuizSerializer(required=False, read_only=True)
    
    class Meta:
        model = CourseTopic
        fields = ['id', 'title', 'slug', 'description', 'content', 
                  'estimated_minutes', 'difficulty', 'key_concepts',
                  'assets', 'code_snippets', 'quiz', 'created_at']


class CourseTopicAdminSerializer(serializers.ModelSerializer):
    """Admin topic serializer - full data for editing"""
    assets = TopicAssetSerializer(many=True, read_only=True)
    code_snippets = SourceCodeSerializer(many=True, read_only=True)
    quiz = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseTopic
        fields = ['id', 'title', 'slug', 'description', 'content',
                  'estimated_minutes', 'difficulty', 'key_concepts',
                  'meta_title', 'meta_description', 'is_archived',
                  'is_ai_generated', 'order_index', 'assets',
                  'code_snippets', 'quiz', 'created_at', 'updated_at']
    
    def get_quiz(self, obj):
        """Get quiz for this topic if it exists"""
        try:
            quiz_instance = obj.quiz.first()  # Get first quiz from manager
            if quiz_instance:
                return TopicQuizAdminSerializer(quiz_instance).data
            return None
        except:
            return None


class CourseTopicWriteSerializer(serializers.ModelSerializer):
    """Writable topic serializer"""
    
    class Meta:
        model = CourseTopic
        fields = ['title', 'description', 'content', 'estimated_minutes',
                  'difficulty', 'key_concepts', 'meta_title', 'meta_description',
                  'order_index']
    
    def create(self, validated_data):
        # Auto-generate slug
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        return super().create(validated_data)


# ============================================================================
# CHAPTER SERIALIZERS
# ============================================================================

class CourseChapterListSerializer(serializers.ModelSerializer):
    """Minimal chapter data for lists"""
    
    class Meta:
        model = CourseChapter
        fields = ['id', 'title', 'slug', 'order_index', 'is_archived']


class CourseChapterDetailSerializer(serializers.ModelSerializer):
    """Chapter with nested topics"""
    topics = CourseTopicListSerializer(many=True, read_only=True)
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseChapter
        fields = ['id', 'title', 'slug', 'description', 'order_index',
                  'is_archived', 'topic_count', 'topics', 'created_at']
    
    def get_topic_count(self, obj):
        return obj.topics.count()


class CourseChapterAdminSerializer(serializers.ModelSerializer):
    """Admin chapter - full detail"""
    topics = CourseTopicAdminSerializer(many=True, read_only=True)
    
    class Meta:
        model = CourseChapter
        fields = ['id', 'title', 'slug', 'description', 'order_index',
                  'is_archived', 'topics', 'created_at', 'updated_at']


class CourseChapterWriteSerializer(serializers.ModelSerializer):
    """Writable chapter serializer"""
    
    class Meta:
        model = CourseChapter
        fields = ['title', 'description', 'order_index']
    
    def create(self, validated_data):
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        return super().create(validated_data)


# ============================================================================
# COURSE SERIALIZERS
# ============================================================================

class CourseListSerializer(serializers.ModelSerializer):
    """Course list view - minimal data"""
    chapter_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'category', 'difficulty',
                  'estimated_hours', 'thumbnail', 'chapter_count', 'status',
                  'published_at', 'created_at']
    
    def get_chapter_count(self, obj):
        return obj.chapters.filter(is_archived=False).count()


class CourseDetailStudentSerializer(serializers.ModelSerializer):
    """Course detail for students - published data only"""
    chapters = CourseChapterDetailSerializer(many=True, read_only=True)
    chapter_count = serializers.SerializerMethodField()
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'category', 'difficulty',
                  'estimated_hours', 'thumbnail', 'tags', 'meta_title',
                  'meta_description', 'chapter_count', 'topic_count',
                  'chapters', 'published_at']
    
    def get_chapter_count(self, obj):
        return obj.chapters.filter(is_archived=False).count()
    
    def get_topic_count(self, obj):
        total = 0
        for chapter in obj.chapters.filter(is_archived=False):
            total += chapter.topics.filter(is_archived=False).count()
        return total


class CourseDetailAdminSerializer(serializers.ModelSerializer):
    """Course detail for admins - full data"""
    chapters = CourseChapterAdminSerializer(many=True, read_only=True)
    versions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'category', 'difficulty',
                  'estimated_hours', 'thumbnail', 'tags', 'meta_title',
                  'meta_description', 'status', 'created_by', 'updated_by',
                  'chapters', 'versions_count', 'created_at', 'updated_at',
                  'published_at']
    
    def get_versions_count(self, obj):
        return obj.versions.count()


class CourseWriteSerializer(serializers.ModelSerializer):
    """Writable course serializer"""
    
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'difficulty', 'estimated_hours',
                  'thumbnail', 'tags', 'meta_title', 'meta_description']
    
    def create(self, validated_data):
        # Auto-generate slug
        if 'slug' not in validated_data:
            validated_data['slug'] = slugify(validated_data['title'])
        # Set creating user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class CourseStructureReorderSerializer(serializers.Serializer):
    """Handle drag-drop reordering"""
    chapters = serializers.ListField(
        child=serializers.DictField(
            child=serializers.JSONField(),
            help_text='{ id: int, order_index: int, topics: [{id, order_index}] }'
        )
    )


# ============================================================================
# PROGRESS & ENROLLMENT SERIALIZERS
# ============================================================================

class TopicProgressSerializer(serializers.ModelSerializer):
    """Student's progress on a topic"""
    
    class Meta:
        model = TopicProgress
        fields = ['id', 'topic', 'status', 'time_spent_minutes', 'view_count',
                  'started_at', 'completed_at', 'last_viewed_at']


class QuizAttemptSerializer(serializers.ModelSerializer):
    """Quiz attempt results"""
    
    class Meta:
        model = QuizAttempt
        fields = ['id', 'quiz', 'score', 'passed', 'time_spent_minutes',
                  'started_at', 'completed_at']


class StudentNoteSerializer(serializers.ModelSerializer):
    """Student's personal notes"""
    
    class Meta:
        model = StudentNote
        fields = ['id', 'topic', 'content', 'created_at', 'updated_at']


class TopicBookmarkSerializer(serializers.ModelSerializer):
    """Topic bookmarks"""
    topic = CourseTopicListSerializer(read_only=True)
    
    class Meta:
        model = TopicBookmark
        fields = ['id', 'topic', 'created_at']


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    """Student enrollment in course"""
    course = CourseListSerializer(read_only=True)
    topic_progress = TopicProgressSerializer(many=True, read_only=True)
    
    class Meta:
        model = CourseEnrollment
        fields = ['id', 'course', 'status', 'progress_percentage',
                  'completed_topics_count', 'enrolled_at', 'started_at',
                  'completed_at', 'last_accessed_at', 'topic_progress']


# ============================================================================
# VERSION & AUDIT SERIALIZERS
# ============================================================================

class CourseVersionSerializer(serializers.ModelSerializer):
    """Course version history"""
    created_by = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = CourseVersion
        fields = ['id', 'version_number', 'change_summary', 'created_by', 'created_at']


class AuditLogSerializer(serializers.ModelSerializer):
    """Audit log entry"""
    user = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = ['id', 'action', 'object_type', 'object_id', 'changes',
                  'reason', 'user', 'created_at']


# ============================================================================
# BULK OPERATIONS SERIALIZERS
# ============================================================================

class DuplicateCourseSerializer(serializers.Serializer):
    """Duplicate a course"""
    title = serializers.CharField(max_length=255, required=False)
    include_quiz = serializers.BooleanField(default=True)
    
    def create(self, validated_data):
        """Implemented in viewset"""
        pass


class ExportCourseSerializer(serializers.Serializer):
    """Export course to JSON/Markdown"""
    format = serializers.ChoiceField(choices=['json', 'markdown'])


class ImportCourseSerializer(serializers.Serializer):
    """Import course from JSON"""
    file = serializers.FileField()
    title = serializers.CharField(max_length=255, required=False)

