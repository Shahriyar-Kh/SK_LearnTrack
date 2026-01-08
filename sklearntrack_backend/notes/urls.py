# FILE: notes/urls.py - UPDATE with AI Tools routes

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
router.register(r'ai-tools', AIToolsViewSet, basename='ai-tools')  # NEW

urlpatterns = [
    # Put the callback URL BEFORE the router includes
    path('notes/google-callback/', GoogleOAuthCallbackView.as_view(), name='google_callback'),
    # Put run_code BEFORE the router includes
    path('run_code/', execute_code, name='run_code'),
    path('', include(router.urls)),
]