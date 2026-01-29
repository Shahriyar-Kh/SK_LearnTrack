# FILE: courses/views_admin.py
# ============================================================================
# Admin-only API Views for Course Management
# ============================================================================
# Full CRUD for courses, chapters, topics with permission checks
# ============================================================================

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
import json
import copy

from .models import (
    Course, CourseChapter, CourseTopic, TopicAsset, SourceCode,
    TopicQuiz, QuizQuestion, QuizChoice,
    CourseVersion, AuditLog,
    CourseStatus, DifficultyLevel
)
from .serializers import (
    CourseListSerializer, CourseDetailAdminSerializer, CourseWriteSerializer,
    CourseChapterListSerializer, CourseChapterAdminSerializer, CourseChapterWriteSerializer,
    CourseTopicListSerializer, CourseTopicAdminSerializer, CourseTopicWriteSerializer,
    TopicAssetSerializer, SourceCodeSerializer,
    TopicQuizAdminSerializer, TopicQuizWriteSerializer,
    CourseStructureReorderSerializer, CourseVersionSerializer, AuditLogSerializer,
    DuplicateCourseSerializer
)


class IsAdmin(permissions.BasePermission):
    """Only admin users can access"""
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsAdminOrReadOnly(permissions.BasePermission):
    """Admin can do anything, others can only read"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


# ============================================================================
# ADMIN COURSE VIEWSET
# ============================================================================

class AdminCourseViewSet(viewsets.ModelViewSet):
    """
    Admin course management with full CRUD.
    
    Endpoints:
    - POST /api/admin/courses/ - Create new course
    - PUT /api/admin/courses/{id}/ - Update course metadata
    - GET /api/admin/courses/{id}/ - Get course detail
    - DELETE /api/admin/courses/{id}/ - Soft delete (archive)
    - POST /api/admin/courses/{id}/publish/ - Publish course
    - POST /api/admin/courses/{id}/unpublish/ - Unpublish course
    - GET /api/admin/courses/{id}/preview/ - Student-view preview
    - POST /api/admin/courses/{id}/duplicate/ - Clone course
    - GET /api/admin/courses/{id}/version-history/ - Version history
    - GET /api/admin/courses/{id}/audit-log/ - Full audit trail
    """
    
    permission_classes = [IsAdmin]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Admins see all courses regardless of status"""
        return Course.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseWriteSerializer
        return CourseDetailAdminSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to return full serialized data with ID and chapters"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full serialized data including ID and all fields
        output_serializer = CourseDetailAdminSerializer(serializer.instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        """Log course creation"""
        course = serializer.save(created_by=self.request.user)
        AuditLog.objects.create(
            course=course,
            user=self.request.user,
            action='create',
            object_type='Course',
            object_id=course.id,
            reason=self.request.data.get('reason', 'Course created')
        )
    
    def perform_update(self, serializer):
        """Log course updates"""
        course = serializer.save(updated_by=self.request.user)
        # Track what changed
        changes = {}
        for field in serializer.validated_data.keys():
            old_value = getattr(course, field)
            new_value = serializer.validated_data[field]
            if old_value != new_value:
                changes[field] = {'old': str(old_value), 'new': str(new_value)}
        
        if changes:
            AuditLog.objects.create(
                course=course,
                user=self.request.user,
                action='update',
                object_type='Course',
                object_id=course.id,
                changes=changes,
                reason=self.request.data.get('reason', 'Course updated')
            )
    
    @action(detail=True, methods=['post'])
    def publish(self, request, id=None, pk=None):
        """
        Publish a course (DRAFT → PUBLISHED).
        
        Validation:
        - Course must have at least 1 chapter
        - Each chapter must have at least 1 topic
        - Each topic must have content
        """
        course = self.get_object()
        
        # Validation
        if course.status == CourseStatus.PUBLISHED:
            return Response(
                {'error': 'Course already published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        chapters = course.chapters.filter(is_archived=False)
        if not chapters.exists():
            return Response(
                {'error': 'Course must have at least 1 chapter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        for chapter in chapters:
            topics = chapter.topics.filter(is_archived=False)
            if not topics.exists():
                return Response(
                    {'error': f'Chapter "{chapter.title}" has no topics'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            for topic in topics:
                if not topic.content.strip():
                    return Response(
                        {'error': f'Topic "{topic.title}" has no content'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Publish
        with transaction.atomic():
            course.status = CourseStatus.PUBLISHED
            course.published_at = timezone.now()
            course.save()
            
            # Create version snapshot
            snapshot = self._create_course_snapshot(course)
            version_num = course.versions.count() + 1
            CourseVersion.objects.create(
                course=course,
                version_number=version_num,
                snapshot=snapshot,
                change_summary=request.data.get('change_summary', 'Course published'),
                created_by=request.user
            )
            
            # Log
            AuditLog.objects.create(
                course=course,
                user=request.user,
                action='publish',
                object_type='Course',
                object_id=course.id,
                reason=request.data.get('reason', 'Course published')
            )
            
            # Clear cache
            self._invalidate_course_cache(course.id)
        
        serializer = self.get_serializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def unpublish(self, request, id=None, pk=None):
        """Unpublish a course (PUBLISHED → DRAFT)"""
        course = self.get_object()
        
        if course.status != CourseStatus.PUBLISHED:
            return Response(
                {'error': 'Only published courses can be unpublished'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            course.status = CourseStatus.DRAFT
            course.save()
            
            AuditLog.objects.create(
                course=course,
                user=request.user,
                action='unpublish',
                object_type='Course',
                object_id=course.id,
                reason=request.data.get('reason', 'Course unpublished')
            )
            
            self._invalidate_course_cache(course.id)
        
        serializer = self.get_serializer(course)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def preview(self, request, id=None, pk=None):
        """
        Get student-view preview of entire course.
        Includes mock progress, doesn't show draft-only content.
        """
        course = self.get_object()
        
        # Return published course view
        serializer = CourseDetailAdminSerializer(course)
        data = serializer.data
        data['preview_mode'] = True
        data['mock_progress'] = {
            'enrolled': False,
            'progress_percentage': 0,
            'completed_topics': 0,
            'total_topics': sum(
                c.topics.filter(is_archived=False).count()
                for c in course.chapters.filter(is_archived=False)
            )
        }
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, id=None, pk=None):
        """Clone entire course structure"""
        course = self.get_object()
        serializer = DuplicateCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create new course
        new_title = serializer.validated_data.get('title') or f"{course.title} (Copy)"
        new_course = Course.objects.create(
            title=new_title,
            slug=f"{course.slug}-copy-{timezone.now().timestamp()}",
            description=course.description,
            category=course.category,
            difficulty=course.difficulty,
            estimated_hours=course.estimated_hours,
            thumbnail=course.thumbnail,
            tags=copy.deepcopy(course.tags),
            meta_title=course.meta_title,
            meta_description=course.meta_description,
            status=CourseStatus.DRAFT,
            created_by=request.user
        )
        
        # Deep copy chapters and topics
        for chapter in course.chapters.filter(is_archived=False):
            new_chapter = CourseChapter.objects.create(
                course=new_course,
                title=chapter.title,
                slug=chapter.slug,
                description=chapter.description,
                order_index=chapter.order_index
            )
            
            for topic in chapter.topics.filter(is_archived=False):
                new_topic = CourseTopic.objects.create(
                    chapter=new_chapter,
                    title=topic.title,
                    slug=topic.slug,
                    description=topic.description,
                    content=topic.content,
                    estimated_minutes=topic.estimated_minutes,
                    difficulty=topic.difficulty,
                    key_concepts=copy.deepcopy(topic.key_concepts),
                    meta_title=topic.meta_title,
                    meta_description=topic.meta_description,
                    order_index=topic.order_index
                )
                
                # Copy assets
                for asset in topic.assets.all():
                    TopicAsset.objects.create(
                        topic=new_topic,
                        type=asset.type,
                        name=asset.name,
                        file=asset.file,
                        description=asset.description,
                        alt_text=asset.alt_text,
                        order_index=asset.order_index
                    )
                
                # Copy code snippets
                for code in topic.code_snippets.all():
                    SourceCode.objects.create(
                        topic=new_topic,
                        language=code.language,
                        code=code.code,
                        description=code.description,
                        title=code.title,
                        order_index=code.order_index
                    )
                
                # Copy quiz if requested
                if serializer.validated_data.get('include_quiz') and topic.quiz.exists():
                    quiz = topic.quiz.first()
                    new_quiz = TopicQuiz.objects.create(
                        topic=new_topic,
                        title=quiz.title,
                        description=quiz.description,
                        passing_score=quiz.passing_score,
                        is_ai_generated=quiz.is_ai_generated
                    )
                    
                    for question in quiz.questions.all():
                        new_question = QuizQuestion.objects.create(
                            quiz=new_quiz,
                            type=question.type,
                            question_text=question.question_text,
                            explanation=question.explanation,
                            order_index=question.order_index
                        )
                        
                        for choice in question.choices.all():
                            QuizChoice.objects.create(
                                question=new_question,
                                choice_text=choice.choice_text,
                                is_correct=choice.is_correct,
                                order_index=choice.order_index
                            )
        
        # Log
        AuditLog.objects.create(
            course=new_course,
            user=request.user,
            action='duplicate',
            object_type='Course',
            object_id=new_course.id,
            changes={'source_course_id': course.id},
            reason=f'Duplicated from {course.title}'
        )
        
        serializer = self.get_serializer(new_course)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def version_history(self, request, pk=None):
        """Get all versions of this course"""
        course = self.get_object()
        versions = course.versions.all().order_by('-version_number')
        serializer = CourseVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def audit_log(self, request, pk=None):
        """Get audit trail for this course"""
        course = self.get_object()
        logs = course.audit_logs.all().order_by('-created_at')[:100]  # Last 100
        serializer = AuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    # Helper methods
    
    def _create_course_snapshot(self, course):
        """Create full JSON snapshot of course structure"""
        chapters_data = []
        for chapter in course.chapters.filter(is_archived=False):
            topics_data = []
            for topic in chapter.topics.filter(is_archived=False):
                topic_data = {
                    'id': topic.id,
                    'title': topic.title,
                    'slug': topic.slug,
                    'content': topic.content,
                    'estimated_minutes': topic.estimated_minutes,
                    'assets': list(topic.assets.values()),
                    'code_snippets': list(topic.code_snippets.values()),
                }
                topics_data.append(topic_data)
            
            chapters_data.append({
                'id': chapter.id,
                'title': chapter.title,
                'slug': chapter.slug,
                'topics': topics_data
            })
        
        return {
            'course_id': course.id,
            'title': course.title,
            'slug': course.slug,
            'status': course.status,
            'created_at': course.created_at.isoformat(),
            'chapters': chapters_data
        }
    
    def _invalidate_course_cache(self, course_id):
        """Clear related caches when course changes"""
        cache.delete(f'course:{course_id}')
        cache.delete(f'course:{course_id}:structure')
        cache.delete('courses:published_list')


# ============================================================================
# ADMIN CHAPTER VIEWSET
# ============================================================================

class AdminChapterViewSet(viewsets.ModelViewSet):
    """
    Manage chapters within a course.
    
    Nested under: /api/admin/courses/{course_id}/chapters/
    """
    
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseChapterWriteSerializer
        return CourseChapterAdminSerializer
    
    def get_queryset(self):
        # Nested router uses 'course' as lookup, not 'course_id'
        course_id = self.kwargs.get('course') or self.kwargs.get('course_id')
        return CourseChapter.objects.filter(course_id=course_id).order_by('order_index')
    
    def create(self, request, *args, **kwargs):
        """Override create to return full serialized data"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full serialized data including ID
        output_serializer = CourseChapterAdminSerializer(serializer.instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        # Nested router uses 'course' as lookup, not 'course_id'
        course_id = self.kwargs.get('course') or self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        chapter = serializer.save(course=course)
        
        AuditLog.objects.create(
            course=course,
            user=self.request.user,
            action='create',
            object_type='Chapter',
            object_id=chapter.id,
            reason=f'Created chapter "{chapter.title}"'
        )
    
    def perform_update(self, serializer):
        chapter = serializer.save()
        AuditLog.objects.create(
            course=chapter.course,
            user=self.request.user,
            action='update',
            object_type='Chapter',
            object_id=chapter.id,
            reason=f'Updated chapter "{chapter.title}"'
        )
        self._invalidate_cache(chapter.course_id)
    
    def perform_destroy(self, instance):
        """Soft delete - archive chapter"""
        instance.is_archived = True
        instance.save()
        
        AuditLog.objects.create(
            course=instance.course,
            user=self.request.user,
            action='delete',
            object_type='Chapter',
            object_id=instance.id,
            reason=f'Archived chapter "{instance.title}"'
        )
        self._invalidate_cache(instance.course_id)
    
    def _invalidate_cache(self, course_id):
        cache.delete(f'course:{course_id}:structure')


# ============================================================================
# ADMIN TOPIC VIEWSET
# ============================================================================

class AdminTopicViewSet(viewsets.ModelViewSet):
    """
    Manage topics within a chapter.
    
    Nested under: /api/admin/courses/{course_id}/chapters/{chapter_id}/topics/
    """
    
    permission_classes = [IsAdmin]
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CourseTopicWriteSerializer
        return CourseTopicAdminSerializer
    
    def get_queryset(self):
        # Nested router uses 'chapter' as lookup, not 'chapter_id'
        chapter_id = self.kwargs.get('chapter') or self.kwargs.get('chapter_id')
        return CourseTopic.objects.filter(chapter_id=chapter_id).order_by('order_index')
    
    def create(self, request, *args, **kwargs):
        """Override create to return full serialized data with ID"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return full serialized data including ID and all fields
        output_serializer = CourseTopicAdminSerializer(serializer.instance)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        # Nested router uses 'chapter' as lookup, not 'chapter_id'
        chapter_id = self.kwargs.get('chapter') or self.kwargs.get('chapter_id')
        chapter = get_object_or_404(CourseChapter, id=chapter_id)
        topic = serializer.save(chapter=chapter)
        
        AuditLog.objects.create(
            course=chapter.course,
            user=self.request.user,
            action='create',
            object_type='Topic',
            object_id=topic.id,
            reason=f'Created topic "{topic.title}"'
        )
    
    def perform_update(self, serializer):
        topic = serializer.save()
        AuditLog.objects.create(
            course=topic.chapter.course,
            user=self.request.user,
            action='update',
            object_type='Topic',
            object_id=topic.id,
            reason=f'Updated topic "{topic.title}"'
        )
        self._invalidate_cache(topic.chapter.course_id)
    
    def perform_destroy(self, instance):
        """Soft delete - archive topic"""
        instance.is_archived = True
        instance.save()
        
        AuditLog.objects.create(
            course=instance.chapter.course,
            user=self.request.user,
            action='delete',
            object_type='Topic',
            object_id=instance.id,
            reason=f'Archived topic "{instance.title}"'
        )
        self._invalidate_cache(instance.chapter.course_id)
    
    def _invalidate_cache(self, course_id):
        cache.delete(f'course:{course_id}:structure')


# ============================================================================
# STRUCTURE REORDERING
# ============================================================================

class ReorderStructureViewSet(viewsets.ViewSet):
    """Handle drag-drop reordering of chapters and topics"""
    
    permission_classes = [IsAdmin]
    
    @action(detail=False, methods=['post'], url_path='reorder')
    def reorder(self, request):
        """
        POST /api/admin/courses/{course_id}/structure/reorder/
        
        Body: {
            "chapters": [
                {
                    "id": 1,
                    "order_index": 0,
                    "topics": [
                        {"id": 5, "order_index": 0},
                        {"id": 6, "order_index": 1}
                    ]
                }
            ]
        }
        """
        serializer = CourseStructureReorderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        
        with transaction.atomic():
            for chapter_data in serializer.validated_data['chapters']:
                chapter = get_object_or_404(
                    CourseChapter,
                    id=chapter_data['id'],
                    course=course
                )
                chapter.order_index = chapter_data['order_index']
                chapter.save()
                
                for topic_data in chapter_data.get('topics', []):
                    topic = get_object_or_404(
                        CourseTopic,
                        id=topic_data['id'],
                        chapter=chapter
                    )
                    topic.order_index = topic_data['order_index']
                    topic.save()
            
            AuditLog.objects.create(
                course=course,
                user=self.request.user,
                action='update',
                object_type='Course',
                object_id=course.id,
                reason='Reordered course structure'
            )
            
            cache.delete(f'course:{course_id}:structure')
        
        return Response({'status': 'Structure reordered'}, status=status.HTTP_200_OK)

