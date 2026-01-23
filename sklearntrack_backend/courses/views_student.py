# FILE: courses/views_student.py
# ============================================================================
# Student-facing API Views for Learning Experience
# ============================================================================
# Read-only access to published courses, progress tracking, quiz submission
# ============================================================================

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from django.db.models import Q, F, Count, Avg, Sum, Case, When, IntegerField

from .models import (
    Course, CourseChapter, CourseTopic, TopicAsset, SourceCode,
    TopicQuiz, QuizQuestion, QuizChoice,
    CourseEnrollment, TopicProgress, QuizAttempt, StudentNote, TopicBookmark,
    TopicStatus, CourseStatus
)
from .serializers import (
    CourseListSerializer, CourseDetailStudentSerializer,
    CourseTopicListSerializer, CourseTopicDetailSerializer,
    CourseEnrollmentSerializer, TopicProgressSerializer,
    QuizAttemptSerializer, StudentNoteSerializer, TopicBookmarkSerializer,
    TopicQuizSerializer
)


class IsAuthenticated(permissions.IsAuthenticated):
    """Custom auth check"""
    pass


class IsPublished(permissions.BasePermission):
    """Course must be published"""
    def has_object_permission(self, request, view, obj):
        return obj.status == CourseStatus.PUBLISHED


# ============================================================================
# STUDENT COURSE DISCOVERY
# ============================================================================

class StudentCourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Browse published courses.
    
    Endpoints:
    - GET /api/courses/ - List all published courses (cached)
    - GET /api/courses/{id}/ - Course detail with structure
    - GET /api/courses/?category=python&difficulty=beginner&search=basics
    - POST /api/courses/{id}/enroll/ - Enroll in course
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseListSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Only show published courses"""
        queryset = Course.objects.filter(status=CourseStatus.PUBLISHED).order_by('-published_at')
        
        # Filters
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(tags__contains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CourseDetailStudentSerializer
        return CourseListSerializer
    
    def retrieve(self, request, *args, **kwargs):
        """Get course detail with caching"""
        course = self.get_object()
        
        # Try cache first
        cache_key = f'course:{course.id}:student_view'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        serializer = self.get_serializer(course)
        data = serializer.data
        
        # Cache for 24 hours
        cache.set(cache_key, data, 86400)
        return Response(data)
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, id=None, pk=None):
        """
        Enroll student in course.
        
        POST /api/courses/{id}/enroll/
        Response: { id, course, status, enrolled_at, ... }
        """
        course = self.get_object()
        
        # Check permission
        if course.status != CourseStatus.PUBLISHED:
            return Response(
                {'error': 'Cannot enroll in unpublished course'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create enrollment
        enrollment, created = CourseEnrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        # If new enrollment, initialize progress tracking
        if created:
            enrollment.started_at = timezone.now()
            enrollment.save()
            
            # Create topic progress records for all topics
            for chapter in course.chapters.filter(is_archived=False):
                for topic in chapter.topics.filter(is_archived=False):
                    TopicProgress.objects.create(
                        enrollment=enrollment,
                        topic=topic,
                        status=TopicStatus.NOT_STARTED
                    )
        
        serializer = CourseEnrollmentSerializer(enrollment)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, id=None, pk=None):
        """
        Get student's progress in course.
        
        GET /api/courses/{id}/progress/
        Response: { progress_percentage, completed_topics, current_topic, ... }
        """
        course = self.get_object()
        enrollment = get_object_or_404(
            CourseEnrollment,
            student=request.user,
            course=course
        )
        
        # Calculate progress
        total_topics = sum(
            ch.topics.filter(is_archived=False).count()
            for ch in course.chapters.filter(is_archived=False)
        )
        
        completed = enrollment.topic_progress.filter(
            status=TopicStatus.COMPLETED
        ).count()
        
        progress_data = {
            'enrollment_id': enrollment.id,
            'course_id': course.id,
            'status': enrollment.status,
            'total_topics': total_topics,
            'completed_topics': completed,
            'progress_percentage': (completed / total_topics * 100) if total_topics > 0 else 0,
            'enrolled_at': enrollment.enrolled_at,
            'started_at': enrollment.started_at,
            'completed_at': enrollment.completed_at,
            'last_accessed_at': enrollment.last_accessed_at,
            'time_spent_minutes': enrollment.topic_progress.aggregate(
                total=Sum('time_spent_minutes')
            )['total'] or 0,
        }
        
        # Get current (last accessed) topic
        try:
            last_progress = enrollment.topic_progress.filter(
                status__in=[TopicStatus.IN_PROGRESS, TopicStatus.NOT_STARTED]
            ).latest('last_viewed_at')
            progress_data['current_topic_id'] = last_progress.topic.id
            progress_data['current_topic_title'] = last_progress.topic.title
        except TopicProgress.DoesNotExist:
            pass
        
        return Response(progress_data)


# ============================================================================
# TOPIC VIEWER
# ============================================================================

class StudentTopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View individual topics with assets and quizzes.
    
    Endpoints:
    - GET /api/courses/{course_id}/topics/{topic_id}/ - Topic detail
    - GET /api/courses/{course_id}/topics/{topic_id}/next/ - Next topic
    - GET /api/courses/{course_id}/topics/{topic_id}/previous/ - Previous topic
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CourseTopicDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        """Only show topics from published courses"""
        course_id = self.kwargs.get('course_id')
        return CourseTopic.objects.filter(
            chapter__course_id=course_id,
            chapter__course__status=CourseStatus.PUBLISHED,
            is_archived=False
        ).order_by('chapter__order_index', 'order_index')
    
    def retrieve(self, request, *args, **kwargs):
        """View topic and track engagement"""
        topic = self.get_object()
        course_id = self.kwargs.get('course_id')
        course = get_object_or_404(Course, id=course_id, status=CourseStatus.PUBLISHED)
        
        # Get enrollment
        enrollment = get_object_or_404(
            CourseEnrollment,
            student=request.user,
            course=course
        )
        
        # Update progress tracking
        progress, _ = TopicProgress.objects.get_or_create(
            enrollment=enrollment,
            topic=topic
        )
        progress.view_count += 1
        progress.last_viewed_at = timezone.now()
        if progress.status == TopicStatus.NOT_STARTED:
            progress.status = TopicStatus.IN_PROGRESS
            progress.started_at = timezone.now()
        progress.save()
        
        # Get topic data
        serializer = self.get_serializer(topic)
        data = serializer.data
        
        # Add progress info
        data['student_progress'] = {
            'status': progress.status,
            'time_spent_minutes': progress.time_spent_minutes,
            'view_count': progress.view_count,
            'started_at': progress.started_at,
            'completed_at': progress.completed_at,
        }
        
        # Add previous/next topic URLs
        prev_topic = self._get_previous_topic(topic)
        next_topic = self._get_next_topic(topic)
        
        data['navigation'] = {
            'previous_topic_id': prev_topic.id if prev_topic else None,
            'next_topic_id': next_topic.id if next_topic else None,
        }
        
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def next(self, request, id=None, course_id=None, pk=None):
        """Get next topic"""
        topic = self.get_object()
        next_topic = self._get_next_topic(topic)
        
        if not next_topic:
            return Response(
                {'error': 'No next topic'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(next_topic)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def previous(self, request, id=None, course_id=None, pk=None):
        """Get previous topic"""
        topic = self.get_object()
        prev_topic = self._get_previous_topic(topic)
        
        if not prev_topic:
            return Response(
                {'error': 'No previous topic'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(prev_topic)
        return Response(serializer.data)
    
    def _get_next_topic(self, current_topic):
        """Get next topic in chapter, or first topic of next chapter"""
        same_chapter = current_topic.chapter.topics.filter(
            order_index__gt=current_topic.order_index,
            is_archived=False
        ).order_by('order_index').first()
        
        if same_chapter:
            return same_chapter
        
        next_chapter = current_topic.chapter.course.chapters.filter(
            order_index__gt=current_topic.chapter.order_index,
            is_archived=False
        ).order_by('order_index').first()
        
        if next_chapter:
            return next_chapter.topics.filter(is_archived=False).order_by('order_index').first()
        
        return None
    
    def _get_previous_topic(self, current_topic):
        """Get previous topic in chapter, or last topic of previous chapter"""
        same_chapter = current_topic.chapter.topics.filter(
            order_index__lt=current_topic.order_index,
            is_archived=False
        ).order_by('-order_index').first()
        
        if same_chapter:
            return same_chapter
        
        prev_chapter = current_topic.chapter.course.chapters.filter(
            order_index__lt=current_topic.chapter.order_index,
            is_archived=False
        ).order_by('-order_index').first()
        
        if prev_chapter:
            return prev_chapter.topics.filter(is_archived=False).order_by('-order_index').first()
        
        return None


# ============================================================================
# QUIZ SUBMISSION & GRADING
# ============================================================================

class QuizAttemptViewSet(viewsets.ViewSet):
    """
    Submit quiz answers and get instant feedback.
    
    Endpoints:
    - POST /api/courses/{course_id}/topics/{topic_id}/quiz-attempt/ - Submit answers
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='quiz-attempt')
    def submit_quiz(self, request, course_id=None, topic_id=None):
        """
        Submit quiz answers for instant grading.
        
        POST /api/courses/{course_id}/topics/{topic_id}/quiz-attempt/
        Body: {
            "answers": {
                "question_id": "choice_id",
                ...
            }
        }
        
        Response: {
            "score": 0.8,
            "passed": true,
            "message": "Great job!",
            "results": [
                {
                    "question_id": 1,
                    "question_text": "...",
                    "student_choice_id": 2,
                    "correct_choice_id": 2,
                    "is_correct": true,
                    "explanation": "..."
                }
            ]
        }
        """
        course = get_object_or_404(Course, id=course_id, status=CourseStatus.PUBLISHED)
        topic = get_object_or_404(CourseTopic, id=topic_id, chapter__course=course)
        
        # Get quiz
        quiz = topic.quiz.first()
        if not quiz:
            return Response(
                {'error': 'No quiz for this topic'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get enrollment
        enrollment = get_object_or_404(
            CourseEnrollment,
            student=request.user,
            course=course
        )
        
        # Validate answers
        answers = request.data.get('answers', {})
        if not answers:
            return Response(
                {'error': 'No answers provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Grade quiz
        results = []
        correct_count = 0
        total_count = 0
        
        for question_id_str, choice_id_str in answers.items():
            try:
                question_id = int(question_id_str)
                choice_id = int(choice_id_str)
            except ValueError:
                continue
            
            question = get_object_or_404(QuizQuestion, id=question_id, quiz=quiz)
            chosen_choice = get_object_or_404(QuizChoice, id=choice_id)
            correct_choice = question.choices.filter(is_correct=True).first()
            
            is_correct = chosen_choice.is_correct
            if is_correct:
                correct_count += 1
            
            total_count += 1
            
            results.append({
                'question_id': question.id,
                'question_text': question.question_text,
                'student_choice_id': choice_id,
                'student_choice_text': chosen_choice.choice_text,
                'correct_choice_id': correct_choice.id if correct_choice else None,
                'correct_choice_text': correct_choice.choice_text if correct_choice else None,
                'is_correct': is_correct,
                'explanation': question.explanation,
            })
        
        # Calculate score
        score = (correct_count / total_count) if total_count > 0 else 0
        passed = score >= quiz.passing_score
        
        # Save attempt
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            score=score,
            passed=passed,
            answers=answers,
            time_spent_minutes=int((timezone.now() - timezone.now()).total_seconds() / 60)
        )
        
        # Update topic progress if passed
        if passed:
            topic_progress = TopicProgress.objects.get(
                enrollment=enrollment,
                topic=topic
            )
            topic_progress.status = TopicStatus.COMPLETED
            topic_progress.completed_at = timezone.now()
            topic_progress.save()
            
            # Update enrollment progress percentage
            enrollment.completed_topics_count = enrollment.topic_progress.filter(
                status=TopicStatus.COMPLETED
            ).count()
            total_topics = sum(
                ch.topics.filter(is_archived=False).count()
                for ch in course.chapters.filter(is_archived=False)
            )
            enrollment.progress_percentage = (
                enrollment.completed_topics_count / total_topics * 100
            ) if total_topics > 0 else 0
            enrollment.save()
        
        return Response({
            'attempt_id': attempt.id,
            'score': score,
            'percentage': int(score * 100),
            'passed': passed,
            'message': 'Great job!' if passed else 'Keep practicing!',
            'correct_count': correct_count,
            'total_count': total_count,
            'passing_score': int(quiz.passing_score * 100),
            'results': results,
        }, status=status.HTTP_201_CREATED)


# ============================================================================
# STUDENT NOTES & BOOKMARKS
# ============================================================================

class StudentNoteViewSet(viewsets.ModelViewSet):
    """
    Student personal notes for topics.
    
    Endpoints:
    - GET /api/courses/{course_id}/topics/{topic_id}/notes/ - My notes
    - POST /api/courses/{course_id}/topics/{topic_id}/notes/ - Create note
    - PUT /api/courses/{course_id}/topics/{topic_id}/notes/{id}/ - Update note
    - DELETE /api/courses/{course_id}/topics/{topic_id}/notes/{id}/ - Delete note
    """
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentNoteSerializer
    
    def get_queryset(self):
        topic_id = self.kwargs.get('topic_id')
        return StudentNote.objects.filter(
            student=self.request.user,
            topic_id=topic_id
        )
    
    def perform_create(self, serializer):
        topic_id = self.kwargs.get('topic_id')
        topic = get_object_or_404(CourseTopic, id=topic_id)
        serializer.save(student=self.request.user, topic=topic)
    
    def perform_update(self, serializer):
        serializer.save()


class TopicBookmarkViewSet(viewsets.ViewSet):
    """
    Bookmark topics for later review.
    
    Endpoints:
    - POST /api/courses/{course_id}/topics/{topic_id}/bookmark/ - Bookmark topic
    - DELETE /api/courses/{course_id}/topics/{topic_id}/bookmark/ - Remove bookmark
    - GET /api/me/bookmarks/ - Get all bookmarks
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'], url_path='bookmark')
    def bookmark_topic(self, request, course_id=None, topic_id=None):
        """Bookmark a topic"""
        topic = get_object_or_404(
            CourseTopic,
            id=topic_id,
            chapter__course_id=course_id
        )
        
        bookmark, created = TopicBookmark.objects.get_or_create(
            student=request.user,
            topic=topic
        )
        
        return Response(
            {'bookmarked': created, 'topic_id': topic.id},
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['delete'], url_path='bookmark')
    def remove_bookmark(self, request, course_id=None, topic_id=None):
        """Remove bookmark"""
        bookmark = get_object_or_404(
            TopicBookmark,
            student=request.user,
            topic_id=topic_id
        )
        bookmark.delete()
        
        return Response({'removed': True}, status=status.HTTP_204_NO_CONTENT)


# ============================================================================
# STUDENT DASHBOARD
# ============================================================================

class StudentDashboardViewSet(viewsets.ViewSet):
    """
    Student dashboard with enrollments, progress, and recommendations.
    
    Endpoints:
    - GET /api/me/dashboard/ - Dashboard overview
    - GET /api/me/resume/ - Last accessed course/topic
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """Get student dashboard"""
        enrollments = CourseEnrollment.objects.filter(
            student=request.user
        ).select_related('course').order_by('-last_accessed_at')
        
        dashboard_data = {
            'total_enrollments': enrollments.count(),
            'active_courses': enrollments.filter(status='active').count(),
            'completed_courses': enrollments.filter(status='completed').count(),
            'total_time_minutes': sum(
                sum(
                    tp.time_spent_minutes
                    for tp in e.topic_progress.all()
                )
                for e in enrollments
            ),
            'enrollments': CourseEnrollmentSerializer(
                enrollments[:5],  # Last 5
                many=True
            ).data,
            'statistics': {
                'avg_completion': enrollments.aggregate(
                    avg=Avg('progress_percentage')
                )['avg'] or 0,
                'total_topics_completed': sum(
                    e.completed_topics_count
                    for e in enrollments
                ),
            }
        }
        
        return Response(dashboard_data)
    
    @action(detail=False, methods=['get'], url_path='resume')
    def resume(self, request):
        """Get last accessed topic across all courses"""
        last_progress = TopicProgress.objects.filter(
            enrollment__student=request.user,
            status__in=[TopicStatus.IN_PROGRESS, TopicStatus.NOT_STARTED]
        ).select_related('topic', 'enrollment__course').latest(
            'last_viewed_at', default=None
        )
        
        if not last_progress:
            return Response(
                {'message': 'No courses started yet'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'course_id': last_progress.enrollment.course.id,
            'course_title': last_progress.enrollment.course.title,
            'topic_id': last_progress.topic.id,
            'topic_title': last_progress.topic.title,
            'last_accessed_at': last_progress.last_viewed_at,
            'url': f"/courses/{last_progress.enrollment.course.slug}/topics/{last_progress.topic.slug}/",
        })

