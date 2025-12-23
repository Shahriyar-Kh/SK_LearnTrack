# FILE: notes/urls.py
# ============================================================================

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    NoteViewSet, CodeSnippetViewSet, NoteSourceViewSet,
    NoteTemplateViewSet, DailyReportViewSet, NoteShareViewSet
)

router = DefaultRouter()
router.register('notes', NoteViewSet, basename='note')
router.register('snippets', CodeSnippetViewSet, basename='snippet')
router.register('sources', NoteSourceViewSet, basename='source')
router.register('templates', NoteTemplateViewSet, basename='template')
router.register('reports', DailyReportViewSet, basename='report')
router.register('shares', NoteShareViewSet, basename='share')

urlpatterns = router.urls