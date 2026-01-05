# FILE: notes/serializers.py
# ============================================================================

from rest_framework import serializers
from .models import (
    Note, Chapter, ChapterTopic, TopicExplanation, 
    TopicCodeSnippet, TopicSource, NoteVersion, 
    AIGeneratedContent, NoteShare
)
import os
from django.conf import settings



class TopicExplanationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicExplanation
        fields = ['id', 'content', 'created_at', 'updated_at']


class TopicCodeSnippetSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicCodeSnippet
        fields = ['id', 'language', 'code', 'created_at', 'updated_at']


class TopicSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopicSource
        fields = ['id', 'title', 'url', 'created_at']


class ChapterTopicSerializer(serializers.ModelSerializer):
    explanation = TopicExplanationSerializer(required=False, allow_null=True)
    code_snippet = TopicCodeSnippetSerializer(required=False, allow_null=True)
    source = TopicSourceSerializer(required=False, allow_null=True)
    
    has_explanation = serializers.BooleanField(read_only=True)
    has_code = serializers.BooleanField(read_only=True)
    has_source = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ChapterTopic
        fields = [
            'id', 'name', 'order', 
            'explanation', 'code_snippet', 'source',
            'has_explanation', 'has_code', 'has_source',
            'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        explanation_data = validated_data.pop('explanation', None)
        code_data = validated_data.pop('code_snippet', None)
        source_data = validated_data.pop('source', None)
        
        topic = ChapterTopic.objects.create(**validated_data)
        
        if explanation_data:
            explanation = TopicExplanation.objects.create(**explanation_data)
            topic.explanation = explanation
        
        if code_data:
            code = TopicCodeSnippet.objects.create(**code_data)
            topic.code_snippet = code
        
        if source_data:
            source = TopicSource.objects.create(**source_data)
            topic.source = source
        
        topic.save()
        return topic
    
    def update(self, instance, validated_data):
        explanation_data = validated_data.pop('explanation', None)
        code_data = validated_data.pop('code_snippet', None)
        source_data = validated_data.pop('source', None)
        
        # Update topic fields
        instance.name = validated_data.get('name', instance.name)
        instance.order = validated_data.get('order', instance.order)
        
        # Update or create explanation
        if explanation_data is not None:
            if instance.explanation:
                for key, value in explanation_data.items():
                    setattr(instance.explanation, key, value)
                instance.explanation.save()
            else:
                explanation = TopicExplanation.objects.create(**explanation_data)
                instance.explanation = explanation
        
        # Update or create code snippet
        if code_data is not None:
            if instance.code_snippet:
                for key, value in code_data.items():
                    setattr(instance.code_snippet, key, value)
                instance.code_snippet.save()
            else:
                code = TopicCodeSnippet.objects.create(**code_data)
                instance.code_snippet = code
        
        # Update or create source
        if source_data is not None:
            if instance.source:
                for key, value in source_data.items():
                    setattr(instance.source, key, value)
                instance.source.save()
            else:
                source = TopicSource.objects.create(**source_data)
                instance.source = source
        
        instance.save()
        return instance


class ChapterSerializer(serializers.ModelSerializer):
    topics = ChapterTopicSerializer(many=True, read_only=True)
    topic_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'topics', 'topic_count', 'created_at', 'updated_at']
    
    def get_topic_count(self, obj):
        return obj.topics.count()


class NoteListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    chapter_count = serializers.SerializerMethodField()
    total_topics = serializers.SerializerMethodField()
    
    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'tags', 'status',
            'course', 'chapter_count', 'total_topics',
            'created_at', 'updated_at'
        ]
    
    def get_chapter_count(self, obj):
        return obj.chapters.count()
    
    def get_total_topics(self, obj):
        return ChapterTopic.objects.filter(chapter__note=obj).count()


# Add to your NoteDetailSerializer:

class NoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['title', 'status', 'tags', 'course', 'course_topic', 'course_subtopic', 'session_date']
    
    def create(self, validated_data):
        # Get the user from context (set by the view)
        user = self.context['request'].user
        return Note.objects.create(user=user, **validated_data)
    
class NoteDetailSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    version_count = serializers.SerializerMethodField()
    google_drive_status = serializers.SerializerMethodField()  # NEW

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'slug', 'tags', 'status',
            'course', 'course_topic', 'course_subtopic',
            'chapters', 'version_count', 'session_date',
            'google_drive_status',  # NEW
            'created_at', 'updated_at'
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at']
    
    def get_version_count(self, obj):
        return obj.versions.count()
    
    def get_google_drive_status(self, obj):
        """Check if user has Google Drive connected"""
        user = self.context['request'].user
        token_path = os.path.join(
            settings.MEDIA_ROOT,
            'google_tokens',
            f'token_{user.id}.pickle'
        )
        return {
            'connected': os.path.exists(token_path),
            'can_export': os.path.exists(token_path)
        }



class NoteVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteVersion
        fields = ['id', 'version_number', 'snapshot', 'changes_summary', 'saved_at']
        read_only_fields = ['version_number', 'saved_at']


class AIGeneratedContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIGeneratedContent
        fields = [
            'id', 'action_type', 'input_content', 'generated_content',
            'model_used', 'tokens_used', 'created_at'
        ]
        read_only_fields = ['created_at']


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


# AI Action Serializers
class AIActionSerializer(serializers.Serializer):
    """Serializer for AI actions"""
    action_type = serializers.ChoiceField(choices=[
        'generate_explanation',
        'improve_explanation',
        'summarize_explanation',
        'generate_code'
    ])
    input_content = serializers.CharField()
    topic_id = serializers.IntegerField(required=False)
    language = serializers.CharField(required=False, default='python')


class TopicCreateSerializer(serializers.Serializer):
    """Serializer for creating a topic with all components"""
    chapter_id = serializers.IntegerField()
    name = serializers.CharField(max_length=500)
    order = serializers.IntegerField(required=False, default=0)
    
    explanation_content = serializers.CharField(required=False, allow_blank=True)
    code_language = serializers.CharField(required=False, default='python')
    code_content = serializers.CharField(required=False, allow_blank=True)
    source_title = serializers.CharField(required=False, allow_blank=True)
    source_url = serializers.URLField(required=False, allow_blank=True)


class TopicUpdateSerializer(serializers.Serializer):
    """Serializer for updating topic components"""
    name = serializers.CharField(max_length=500, required=False)
    order = serializers.IntegerField(required=False)
    
    explanation_content = serializers.CharField(required=False, allow_blank=True)
    code_language = serializers.CharField(required=False)
    code_content = serializers.CharField(required=False, allow_blank=True)
    source_title = serializers.CharField(required=False, allow_blank=True)
    source_url = serializers.URLField(required=False, allow_blank=True)