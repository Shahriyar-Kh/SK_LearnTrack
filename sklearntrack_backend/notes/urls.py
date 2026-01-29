# FILE: notes/urls.py - ADD STANDALONE AI ROUTE

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, ChapterViewSet, TopicViewSet, NoteShareViewSet, AIToolsViewSet
from .google_callback import GoogleOAuthCallbackView
from .views import execute_code

router = DefaultRouter()
router.register(r'notes', NoteViewSet, basename='note')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'shares', NoteShareViewSet, basename='share')
router.register(r'ai-tools', AIToolsViewSet, basename='ai-tools')

urlpatterns = [
    # Standalone routes (MUST come before router)
    path('notes/google-callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    path('run_code/', execute_code, name='run_code'),
    
    # NEW: Standalone AI action route
    path('topics/ai-action-standalone/', TopicViewSet.as_view({'post': 'ai_action_standalone'}), name='topic-ai-standalone'),
    
    # Router URLs
    path('', include(router.urls)),
]