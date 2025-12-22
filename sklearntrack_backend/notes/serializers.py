# FILE: notes/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import Note, CodeSnippet, NoteHistory


class CodeSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSnippet
        fields = ['id', 'title', 'language', 'code', 'description', 'tags']


class NoteSerializer(serializers.ModelSerializer):
    code_snippets = CodeSnippetSerializer(many=True, read_only=True)
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'tags',
            'course', 'topic', 'subtopic',
            'code_snippets', 'created_at', 'updated_at'
        ]


class NoteHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteHistory
        fields = ['id', 'content', 'saved_at']

