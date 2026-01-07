# FILE: notes/services.py
# ============================================================================
# Core Business Logic for Notes, Chapters, Topics
# ============================================================================
# Import models at the end to avoid circular imports
from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import (
    Note, Chapter, ChapterTopic, TopicExplanation,
    TopicCodeSnippet, TopicSource, NoteVersion
)


class NoteService:
    """Service for Note operations"""
    
    @staticmethod
    def create_note(user, title, **kwargs):
        """Create a new note with validation"""
        # Check for duplicate title
        if Note.objects.filter(user=user, title__iexact=title).exists():
            raise ValidationError(
                f'A note with the title "{title}" already exists. '
                'Please choose a different name.'
            )
        
        return Note.objects.create(
            user=user,
            title=title,
            **kwargs
        )
    
    @staticmethod
    def update_note(note, **data):
        """Update note with validation"""
        title = data.get('title')
        
        if title and title != note.title:
            # Check for duplicate
            if Note.objects.filter(
                user=note.user, 
                title__iexact=title
            ).exclude(id=note.id).exists():
                raise ValidationError(
                    f'A note with the title "{title}" already exists.'
                )
        
        for key, value in data.items():
            setattr(note, key, value)
        
        note.save()
        return note
    
    @staticmethod
    def delete_note(note):
        """Delete note with proper cleanup"""
        with transaction.atomic():
            # Get all chapters for this note
            chapters = note.chapters.all()
            
            # Delete all topics and their components
            for chapter in chapters:
                ChapterService.delete_chapter(chapter)
            
            # Delete note versions
            note.versions.all().delete()
            
            # Delete note shares
            note.shares.all().delete()
            
            # Delete the note
            note.delete()
    
    @staticmethod
    def create_version_snapshot(note):
        """Create a version snapshot of current note state"""
        version_number = note.versions.count() + 1
        
        snapshot = {
            'title': note.title,
            'tags': note.tags,
            'status': note.status,
            'chapters': []
        }
        
        for chapter in note.chapters.all():
            chapter_data = {
                'title': chapter.title,
                'order': chapter.order,
                'topics': []
            }
            
            for topic in chapter.topics.all():
                topic_data = {
                    'name': topic.name,
                    'order': topic.order,
                    'explanation': topic.explanation.content if topic.explanation else None,
                    'code_snippet': {
                        'language': topic.code_snippet.language,
                        'code': topic.code_snippet.code
                    } if topic.code_snippet else None,
                    'source': {
                        'title': topic.source.title,
                        'url': topic.source.url
                    } if topic.source else None
                }
                chapter_data['topics'].append(topic_data)
            
            snapshot['chapters'].append(chapter_data)
        
        return NoteVersion.objects.create(
            note=note,
            version_number=version_number,
            snapshot=snapshot,
            changes_summary=f"Version {version_number} snapshot"
        )
    
    @staticmethod
    def restore_version(note, version):
        """Restore note from version snapshot"""
        with transaction.atomic():
            # Create snapshot of current state first
            NoteService.create_version_snapshot(note)
            
            snapshot = version.snapshot
            
            # Update note fields
            note.title = snapshot.get('title', note.title)
            note.tags = snapshot.get('tags', note.tags)
            note.status = snapshot.get('status', note.status)
            note.save()
            
            # Delete existing chapters
            note.chapters.all().delete()
            
            # Recreate chapters and topics from snapshot
            for chapter_data in snapshot.get('chapters', []):
                chapter = Chapter.objects.create(
                    note=note,
                    title=chapter_data['title'],
                    order=chapter_data['order']
                )
                
                for topic_data in chapter_data.get('topics', []):
                    TopicService.create_topic(
                        chapter=chapter,
                        name=topic_data['name'],
                        order=topic_data['order'],
                        explanation_content=topic_data.get('explanation'),
                        code_language=topic_data.get('code_snippet', {}).get('language'),
                        code_content=topic_data.get('code_snippet', {}).get('code'),
                        source_title=topic_data.get('source', {}).get('title'),
                        source_url=topic_data.get('source', {}).get('url')
                    )


class ChapterService:
    """Service for Chapter operations"""
    
    @staticmethod
    def create_chapter(note, title, order=None):
        """Create a new chapter"""
        if order is None:
            # Get next order number
            max_order = Chapter.objects.filter(note=note).aggregate(
                max_order=models.Max('order')
            )['max_order']
            order = (max_order + 1) if max_order is not None else 0
        
        return Chapter.objects.create(
            note=note,
            title=title,
            order=order
        )
    
    @staticmethod
    def update_chapter(chapter, **data):
        """Update chapter"""
        for key, value in data.items():
            setattr(chapter, key, value)
        chapter.save()
        return chapter
    
    @staticmethod
    def delete_chapter(chapter):
        """Delete chapter with all topics"""
        with transaction.atomic():
            # Delete all topics in this chapter
            for topic in chapter.topics.all():
                TopicService.delete_topic(topic)
            
            # Delete the chapter
            chapter.delete()


class TopicService:
    """Service for Topic operations"""
    
    @staticmethod
    def create_topic(
        chapter, name, order=None,
        explanation_content=None,
        code_language='python', code_content=None,
        source_title=None, source_url=None
    ):
        """Create a new topic with all components"""
        if order is None:
            # Get next order number
            max_order = ChapterTopic.objects.filter(chapter=chapter).aggregate(
                max_order=models.Max('order')
            )['max_order']
            order = (max_order + 1) if max_order is not None else 0
        
        with transaction.atomic():
            # Create topic
            topic = ChapterTopic.objects.create(
                chapter=chapter,
                name=name,
                order=order
            )
            
            # Create explanation if provided
            if explanation_content:
                explanation = TopicExplanation.objects.create(
                    content=explanation_content
                )
                topic.explanation = explanation
            
            # Create code snippet if provided
            if code_content:
                code = TopicCodeSnippet.objects.create(
                    language=code_language,
                    code=code_content
                )
                topic.code_snippet = code
            
            # Create source if provided
            if source_url:
                source = TopicSource.objects.create(
                    title=source_title or 'Reference',
                    url=source_url
                )
                topic.source = source
            
            topic.save()
            return topic
    
    @staticmethod
    def update_topic(topic, **data):
        """Update topic and its components"""
        with transaction.atomic():
            # Update topic fields
            if 'name' in data:
                topic.name = data['name']
            if 'order' in data:
                topic.order = data['order']
            
            # Update explanation
            explanation_content = data.get('explanation_content')
            if explanation_content is not None:
                if topic.explanation:
                    topic.explanation.content = explanation_content
                    topic.explanation.save()
                elif explanation_content:
                    explanation = TopicExplanation.objects.create(
                        content=explanation_content
                    )
                    topic.explanation = explanation
            
            # Update code snippet
            code_content = data.get('code_content')
            if code_content is not None:
                if topic.code_snippet:
                    topic.code_snippet.code = code_content
                    if 'code_language' in data:
                        topic.code_snippet.language = data['code_language']
                    topic.code_snippet.save()
                elif code_content:
                    code = TopicCodeSnippet.objects.create(
                        language=data.get('code_language', 'python'),
                        code=code_content
                    )
                    topic.code_snippet = code
            
            # Update source
            source_url = data.get('source_url')
            if source_url is not None:
                if topic.source:
                    topic.source.url = source_url
                    if 'source_title' in data:
                        topic.source.title = data['source_title']
                    topic.source.save()
                elif source_url:
                    source = TopicSource.objects.create(
                        title=data.get('source_title', 'Reference'),
                        url=source_url
                    )
                    topic.source = source
            
            topic.save()
            return topic
    
    @staticmethod
    def delete_topic(topic):
        """Delete topic with all related objects"""
        with transaction.atomic():
            # Delete related objects (CASCADE will handle this, but explicit is better)
            if topic.explanation:
                topic.explanation.delete()
            if topic.code_snippet:
                topic.code_snippet.delete()
            if topic.source:
                topic.source.delete()
            
            # Delete the topic
            topic.delete()


