# FILE: notes/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import (
    Note, NoteVersion, CodeSnippet, NoteSource, 
    NoteTemplate, DailyNoteReport, AIGeneratedNote,
    YouTubeTranscript, NoteShare
)


class NoteSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteSource
        fields = [
            'id', 'source_type', 'title', 'url', 'author', 
            'date', 'reference_number', 'metadata', 'created_at'
        ]
        read_only_fields = ['reference_number', 'created_at']
    
    def create(self, validated_data):
        # Auto-assign reference number
        user = self.context['request'].user
        last_ref = NoteSource.objects.filter(user=user).order_by('-reference_number').first()
        validated_data['reference_number'] = (last_ref.reference_number + 1) if last_ref else 1
        validated_data['user'] = user
        return super().create(validated_data)


class CodeSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeSnippet
        fields = [
            'id', 'title', 'language', 'code', 'description', 
            'tags', 'course', 'note', 'created_at', 'updated_at'
        ]


class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = [
            'id', 'version_number', 'content', 'content_json',
            'changes_summary', 'saved_at'
        ]
        read_only_fields = ['version_number', 'saved_at']


class NoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    source_count = serializers.SerializerMethodField()
    snippet_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'tags', 'status',
            'course', 'topic', 'subtopic',
            'source_count', 'snippet_count',
            'created_at', 'updated_at'
        ]
    
    def get_source_count(self, obj):
        return obj.sources.count()
    
    def get_snippet_count(self, obj):
        return obj.code_snippets.count()


class NoteDetailSerializer(serializers.ModelSerializer):
    sources = NoteSourceSerializer(many=True, read_only=True)
    code_snippets = CodeSnippetSerializer(many=True, read_only=True)
    version_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'content', 'content_json',
            'tags', 'status', 'course', 'topic', 'subtopic',
            'sources', 'code_snippets', 'toc', 'session_date',
            'version_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_version_count(self, obj):
        return obj.versions.count()
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # Create version before updating
        version_number = instance.versions.count() + 1
        NoteVersion.objects.create(
            note=instance,
            version_number=version_number,
            content=instance.content,
            content_json=instance.content_json,
            changes_summary=f"Update on {instance.updated_at}"
        )
        return super().update(instance, validated_data)


class NoteTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteTemplate
        fields = [
            'id', 'name', 'description', 'template_content',
            'is_system', 'created_at'
        ]
        read_only_fields = ['is_system', 'created_at']


class DailyNoteReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyNoteReport
        fields = [
            'id', 'report_date', 'notes_created', 'notes_updated',
            'topics_covered', 'time_spent_minutes', 'ai_summary',
            'pdf_file', 'email_sent', 'email_sent_at', 'created_at'
        ]
        read_only_fields = ['created_at']


class AIGeneratedNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGeneratedNote
        fields = [
            'id', 'action_type', 'source_content', 'generated_content',
            'approved', 'approved_at', 'model_used', 'tokens_used',
            'created_at'
        ]
        read_only_fields = ['created_at']


class YouTubeTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = YouTubeTranscript
        fields = [
            'id', 'video_url', 'video_id', 'video_title',
            'transcript', 'timestamps', 'processed',
            'notes_generated', 'created_at'
        ]
        read_only_fields = ['video_id', 'created_at']


class NoteShareSerializer(serializers.ModelSerializer):
    note_title = serializers.CharField(source='note.title', read_only=True)
    shared_by_name = serializers.CharField(source='shared_by.full_name', read_only=True)
    shared_with_name = serializers.CharField(source='shared_with.full_name', read_only=True)
    
    class Meta:
        model = NoteShare
        fields = [
            'id', 'note', 'note_title', 'shared_by', 'shared_by_name',
            'shared_with', 'shared_with_name', 'permission',
            'is_public', 'public_slug', 'created_at', 'expires_at'
        ]
        read_only_fields = ['shared_by', 'public_slug', 'created_at']
    
    def create(self, validated_data):
        validated_data['shared_by'] = self.context['request'].user
        return super().create(validated_data)


# AI Action Request Serializers
class AIActionSerializer(serializers.Serializer):
    """Base serializer for AI actions"""
    action_type = serializers.ChoiceField(choices=[
        'summarize_short', 'summarize_medium', 'summarize_detailed',
        'expand', 'rewrite', 'breakdown'
    ])
    content = serializers.CharField()
    note_id = serializers.IntegerField(required=False)


class YouTubeImportSerializer(serializers.Serializer):
    """Serializer for YouTube video import"""
    video_url = serializers.URLField()
    generate_notes = serializers.BooleanField(default=True)
    note_title = serializers.CharField(required=False)


class ExportNoteSerializer(serializers.Serializer):
    """Serializer for note export"""
    export_type = serializers.ChoiceField(choices=[
        'daily', 'full', 'topic'
    ])
    date = serializers.DateField(required=False)
    topic_id = serializers.IntegerField(required=False)
    include_sources = serializers.BooleanField(default=True)
    include_code = serializers.BooleanField(default=True)