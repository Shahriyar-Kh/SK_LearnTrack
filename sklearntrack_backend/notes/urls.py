# FILE: notes/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, ChapterViewSet, TopicViewSet

router = DefaultRouter()
router.register('notes', NoteViewSet, basename='note')
router.register('chapters', ChapterViewSet, basename='chapter')
router.register('topics', TopicViewSet, basename='topic')

urlpatterns = router.urls