# FILE: notes/views.py
# ============================================================================

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Note, CodeSnippet, NoteHistory
from .serializers import NoteSerializer, CodeSnippetSerializer, NoteHistorySerializer


class NoteViewSet(viewsets.ModelViewSet):
    """Note management"""
    
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        
        # Filter by tags
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__contains=tag_list)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search) | \
                       queryset.filter(content__icontains=search)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get note history"""
        note = self.get_object()
        history = NoteHistory.objects.filter(note=note)
        serializer = NoteHistorySerializer(history, many=True)
        return Response(serializer.data)


class CodeSnippetViewSet(viewsets.ModelViewSet):
    """Code snippet management"""
    
    serializer_class = CodeSnippetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return CodeSnippet.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
