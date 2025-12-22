# FILE: roadmaps/views.py
# ============================================================================

from rest_framework import viewsets, permissions
from .models import Roadmap, Milestone, RoadmapTask
from .serializers import RoadmapSerializer, MilestoneSerializer, RoadmapTaskSerializer


class RoadmapViewSet(viewsets.ModelViewSet):
    """Roadmap management"""
    
    serializer_class = RoadmapSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Roadmap.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MilestoneViewSet(viewsets.ModelViewSet):
    """Milestone management"""
    
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Milestone.objects.filter(roadmap__user=self.request.user)


class RoadmapTaskViewSet(viewsets.ModelViewSet):
    """Task management"""
    
    serializer_class = RoadmapTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RoadmapTask.objects.filter(milestone__roadmap__user=self.request.user)

