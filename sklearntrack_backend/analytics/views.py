# FILE: analytics/views.py
# ============================================================================

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum, Count
from datetime import datetime, timedelta
from .models import StudySession, ActivityLog, Notification
from .serializers import StudySessionSerializer, ActivityLogSerializer, NotificationSerializer


class AnalyticsViewSet(viewsets.GenericViewSet):
    """Analytics endpoints"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard analytics"""
        user = request.user
        
        # Weekly study time
        week_ago = datetime.now().date() - timedelta(days=7)
        weekly_sessions = StudySession.objects.filter(
            user=user,
            date__gte=week_ago
        )
        
        weekly_stats = weekly_sessions.aggregate(
            total_minutes=Sum('duration'),
            total_topics=Sum('topics_completed'),
            session_count=Count('id')
        )
        
        # Recent activity
        recent_activities = ActivityLog.objects.filter(user=user)[:10]
        
        return Response({
            'weekly_study_time': weekly_stats['total_minutes'] or 0,
            'topics_completed': weekly_stats['total_topics'] or 0,
            'study_sessions': weekly_stats['session_count'] or 0,
            'current_streak': user.profile.current_streak,
            'recent_activities': ActivityLogSerializer(recent_activities, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def study_history(self, request):
        """Get study session history"""
        days = int(request.query_params.get('days', 30))
        start_date = datetime.now().date() - timedelta(days=days)
        
        sessions = StudySession.objects.filter(
            user=request.user,
            date__gte=start_date
        ).order_by('date')
        
        serializer = StudySessionSerializer(sessions, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """Notification management"""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        self.get_queryset().update(read=True)
        return Response({'status': 'success'})
