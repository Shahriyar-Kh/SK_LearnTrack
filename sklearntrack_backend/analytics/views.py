# FILE: analytics/views.py
# ============================================================================

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import logging

from .serializers import (
    DashboardOverviewSerializer,
    RecentNoteSerializer,
    QuickActionSerializer,
    TodayTaskSerializer
)

logger = logging.getLogger(__name__)


class DashboardViewSet(viewsets.ViewSet):
    """
    Dashboard API endpoints
    
    GET /api/dashboard/overview/ - Main dashboard data
    GET /api/dashboard/recent-notes/ - Recent notes
    GET /api/dashboard/quick-actions/ - Quick action buttons
    GET /api/dashboard/today-plan/ - Today's planned tasks
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """
        Get dashboard overview with mix of real and dummy data
        Real data: Profile, Notes, Account info
        Dummy data: Courses, Roadmaps (marked for replacement)
        """
        user = request.user
        
        # Get real profile data
        profile = getattr(user, 'profile', None)
        
        # Calculate real statistics
        total_notes = user.notes.count() if hasattr(user, 'notes') else 0
        
        # Calculate topics from notes
        topics_completed = 0
        if hasattr(user, 'notes'):
            from notes.models import ChapterTopic
            topics_completed = ChapterTopic.objects.filter(
                chapter__note__user=user
            ).count()
        
        # Profile completion check
        profile_fields = [
            user.full_name,
            user.country,
            user.education_level,
            user.field_of_study,
        ]
        if profile:
            profile_fields.extend([
                profile.bio,
                profile.learning_goal,
            ])
        
        filled_fields = sum(1 for field in profile_fields if field)
        profile_completed = filled_fields >= 4  # At least 4 fields filled
        
        # Compile dashboard data
        dashboard_data = {
            # User Info (Real)
            'user_name': user.full_name or user.email.split('@')[0],
            'user_email': user.email,
            'user_avatar': profile.avatar.url if profile and profile.avatar else None,
            
            # Profile Stats (Real)
            'profile_completed': profile_completed,
            'email_verified': user.email_verified,
            
            # Study Stats (Real)
            'total_notes': total_notes,
            'total_study_days': profile.total_study_days if profile else 0,
            'current_streak': profile.current_streak if profile else 0,
            'longest_streak': profile.longest_streak if profile else 0,
            
            # Module Stats (Mixed)
            'active_courses': 3,  # DUMMY - Replace when courses module is ready
            'topics_completed': topics_completed,  # Real from notes
            'weekly_study_time': 245,  # DUMMY - Replace with real tracking
            
            # Achievements (DUMMY)
            'total_achievements': 12,  # DUMMY - Replace with real achievement system
            
            # Recent Activity (Real)
            'last_login': user.last_login_at,
            'account_created': user.created_at,
        }
        
        serializer = DashboardOverviewSerializer(
            dashboard_data, 
            context={'request': request}
        )
        
        return Response({
            'success': True,
            'data': serializer.data,
            'dummy_fields': [
                'active_courses',
                'weekly_study_time',
                'total_achievements'
            ]  # Mark dummy fields for future replacement
        })
    
    @action(detail=False, methods=['get'], url_path='recent-notes')
    def recent_notes(self, request):
        """Get user's recent notes (real data)"""
        user = request.user
        
        if not hasattr(user, 'notes'):
            return Response({
                'success': True,
                'data': [],
                'message': 'Notes module not available'
            })
        
        # Get last 5 notes
        recent_notes = user.notes.all().order_by('-updated_at')[:5]
        
        notes_data = []
        for note in recent_notes:
            notes_data.append({
                'id': note.id,
                'title': note.title,
                'created_at': note.created_at,
                'updated_at': note.updated_at,
                'tags': note.tags or [],
                'chapter_count': note.chapters.count(),
                'status': note.status,
            })
        
        serializer = RecentNoteSerializer(notes_data, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='quick-actions')
    def quick_actions(self, request):
        """Get available quick actions for dashboard"""
        user = request.user
        
        # Check which modules are available
        has_notes = hasattr(user, 'notes')
        has_courses = False  # DUMMY - Set to True when courses module is ready
        has_roadmaps = False  # DUMMY - Set to True when roadmaps module is ready
        
        actions = [
            {
                'id': 'new-note',
                'label': 'New Note',
                'icon': 'PlusCircle',
                'route': '/notes?action=new',
                'enabled': has_notes,
                'badge': None
            },
            {
                'id': 'browse-courses',
                'label': 'Browse Courses',
                'icon': 'BookOpen',
                'route': '/courses',
                'enabled': True,  # Always show
                'badge': None
            },
            {
                'id': 'ai-assistant',
                'label': 'AI Assistant',
                'icon': 'Brain',
                'route': '/notes?ai=true',
                'enabled': has_notes,
                'badge': None
            },
            {
                'id': 'code-vault',
                'label': 'Code Vault',
                'icon': 'Code',
                'route': '/notes?view=code',
                'enabled': has_notes,
                'badge': user.notes.count() if has_notes else None
            },
        ]
        
        serializer = QuickActionSerializer(actions, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @action(detail=False, methods=['get', 'post'], url_path='today-plan')
    def today_plan(self, request):
        """
        GET: Get today's planned tasks
        POST: Update task completion status
        
        NOTE: This is DUMMY data for now
        Replace with real task management when roadmaps module is ready
        """
        
        if request.method == 'POST':
            # Update task completion
            task_id = request.data.get('task_id')
            completed = request.data.get('completed', False)
            
            # TODO: Update real task in database when roadmaps module is ready
            logger.info(f"Task {task_id} marked as {'completed' if completed else 'incomplete'}")
            
            return Response({
                'success': True,
                'message': 'Task updated successfully'
            })
        
        # DUMMY tasks for now
        now = timezone.now()
        tasks = [
            {
                'id': 1,
                'task': 'Review latest notes',
                'time': '9:00 AM',
                'completed': True,
                'priority': 'high'
            },
            {
                'id': 2,
                'task': 'Complete ML assignment',
                'time': '11:00 AM',
                'completed': True,
                'priority': 'high'
            },
            {
                'id': 3,
                'task': 'Practice coding problems',
                'time': '2:00 PM',
                'completed': False,
                'priority': 'medium'
            },
            {
                'id': 4,
                'task': 'Update learning roadmap',
                'time': '4:00 PM',
                'completed': False,
                'priority': 'low'
            },
        ]
        
        serializer = TodayTaskSerializer(tasks, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'is_dummy': True,  # Mark as dummy data
            'message': 'Replace with real task data from roadmaps module'
        })