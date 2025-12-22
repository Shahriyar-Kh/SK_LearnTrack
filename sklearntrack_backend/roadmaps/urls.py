# FILE: roadmaps/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoadmapViewSet, MilestoneViewSet, RoadmapTaskViewSet

router = DefaultRouter()
router.register('', RoadmapViewSet, basename='roadmap')
router.register('milestones', MilestoneViewSet, basename='milestone')
router.register('tasks', RoadmapTaskViewSet, basename='task')

urlpatterns = router.urls
