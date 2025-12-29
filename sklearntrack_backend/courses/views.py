# FILE: courses/views.py
# ============================================================================

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import (
    Course, Chapter, Topic, Subtopic, Exercise,
    Enrollment, SubtopicProgress, PersonalCourse
)
from .serializers import (
    CourseListSerializer, CourseDetailSerializer,
    EnrollmentSerializer, SubtopicProgressSerializer,
    PersonalCourseSerializer, ExerciseSerializer
)


class CourseViewSet(viewsets.ModelViewSet):
    """Course management"""
    
    queryset = Course.objects.filter(is_published=True)
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'  # ← ADD THIS LINE
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll in a course"""
        course = self.get_object()
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Get course progress"""
        course = self.get_object()
        enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='enrollments')
    def enrollments(self, request):
        """
        Get user's course enrollments
        URL: /api/courses/enrollments/
        """
        try:
            # Import your Enrollment model (adjust path as needed)
            from .models import Enrollment
            
            # Get user's enrollments
            enrollments = Enrollment.objects.filter(
                user=request.user
            ).select_related('course').order_by('-enrolled_at')
            
            # Build response data
            data = []
            for enrollment in enrollments:
                course_data = {
                    'id': enrollment.id,
                    'course': {
                        'id': enrollment.course.id,
                        'title': enrollment.course.title,
                        'slug': enrollment.course.slug,
                        'description': enrollment.course.description if hasattr(enrollment.course, 'description') else '',
                        'difficulty': enrollment.course.difficulty if hasattr(enrollment.course, 'difficulty') else None,
                    },
                    'enrolled_at': enrollment.enrolled_at,
                    'progress': getattr(enrollment, 'progress', 0),
                    'completed': getattr(enrollment, 'completed', False),
                    'last_accessed': getattr(enrollment, 'last_accessed', None),
                }
                data.append(course_data)
            
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    """User enrollments"""
    
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Enrollment.objects.filter(user=self.request.user)


class SubtopicViewSet(viewsets.GenericViewSet):
    """Subtopic progress tracking"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark subtopic as completed"""
        subtopic = get_object_or_404(Subtopic, pk=pk)
        progress, created = SubtopicProgress.objects.get_or_create(
            user=request.user,
            subtopic=subtopic
        )
        progress.completed = True
        progress.save()
        
        return Response({'status': 'completed'})
    
    @action(detail=True, methods=['post'])
    def bookmark(self, request, pk=None):
        """Toggle bookmark on subtopic"""
        subtopic = get_object_or_404(Subtopic, pk=pk)
        progress, created = SubtopicProgress.objects.get_or_create(
            user=request.user,
            subtopic=subtopic
        )
        progress.bookmarked = not progress.bookmarked
        progress.save()
        
        return Response({'bookmarked': progress.bookmarked})


class PersonalCourseViewSet(viewsets.ModelViewSet):
    """Personal course management"""
    
    serializer_class = PersonalCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return PersonalCourse.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
