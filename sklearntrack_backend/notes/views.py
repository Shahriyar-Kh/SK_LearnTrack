# FILE: notes/views.py - FINAL FIX
# ============================================================================

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction, connection
from django.db.models import Q, Count, Prefetch, Max
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from uuid import uuid4
import os

from .models import (
    Note, Chapter, ChapterTopic, TopicExplanation,
    TopicCodeSnippet, TopicSource, NoteVersion,
    AIGeneratedContent, NoteShare
)
from .serializers import (
    NoteListSerializer, NoteDetailSerializer, ChapterSerializer,
    ChapterTopicSerializer, NoteVersionSerializer, AIGeneratedContentSerializer,
    NoteShareSerializer, AIActionSerializer, TopicCreateSerializer,
    TopicUpdateSerializer
)
from .utils import (
    generate_ai_explanation, generate_ai_code,
    improve_explanation, summarize_explanation,
    export_note_to_pdf
)


class NoteViewSet(viewsets.ModelViewSet):
    """Note CRUD with chapters and topics"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        return NoteDetailSerializer
    
    def create(self, request, *args, **kwargs):
        """Create note with unique title validation"""
        title = request.data.get('title', '').strip()
        
        if not title:
            return Response(
                {'error': 'Note title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if note with same title exists for this user
        existing_note = Note.objects.filter(
            user=request.user,
            title__iexact=title
        ).first()
        
        if existing_note:
            return Response(
                {'error': f'A note with the title "{title}" already exists. Please choose a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """Update note with unique title validation"""
        # Get partial parameter
        partial = kwargs.pop('partial', False)
        
        title = request.data.get('title', '').strip()
        note = self.get_object()
        
        if title and title != note.title:
            # Check if another note with same title exists for this user
            existing_note = Note.objects.filter(
                user=request.user,
                title__iexact=title
            ).exclude(id=note.id).first()
            
            if existing_note:
                return Response(
                    {'error': f'A note with the title "{title}" already exists. Please choose a different name.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get the serializer
        serializer = self.get_serializer(note, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user).prefetch_related(
            Prefetch('chapters', queryset=Chapter.objects.order_by('order')),
            Prefetch('chapters__topics', queryset=ChapterTopic.objects.order_by('order').select_related(
                'explanation', 'code_snippet', 'source'
            ))
        )
        
        # Filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        course_id = self.request.query_params.get('course')
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        # Tag filter
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag.strip()])
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(tags__contains=[search]) |
                Q(chapters__title__icontains=search) |
                Q(chapters__topics__name__icontains=search)
            ).distinct()
        
        return queryset.order_by('-updated_at')
    
    @action(detail=True, methods=['get'])
    def structure(self, request, pk=None):
        """Get full note structure with all nested data"""
        note = self.get_object()
        serializer = NoteDetailSerializer(note)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        """Upload image for use in note explanations"""
        if 'image' not in request.FILES:
            return Response(
                {'error': 'No image file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        image_file = request.FILES['image']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if image_file.content_type not in allowed_types:
            return Response(
                {'error': 'Invalid file type. Only images (JPEG, PNG, GIF, WebP) are allowed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (max 5MB)
        if image_file.size > 5 * 1024 * 1024:
            return Response(
                {'error': 'File size too large. Maximum size is 5MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique filename
        file_ext = os.path.splitext(image_file.name)[1]
        filename = f"notes/images/{uuid4()}{file_ext}"
        
        # Save file
        saved_path = default_storage.save(filename, ContentFile(image_file.read()))
        
        # Return URL
        file_url = request.build_absolute_uri(default_storage.url(saved_path))
        
        return Response({
            'url': file_url,
            'filename': saved_path
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        """Export note to PDF with proper formatting"""
        note = self.get_object()
        
        try:
            pdf_file = export_note_to_pdf(note)
            
            if not pdf_file:
                return Response(
                    {'error': 'Failed to generate PDF'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create HTTP response with PDF content
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            filename = f"note_{note.slug}_{timezone.now().strftime('%Y%m%d')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            return Response(
                {'error': f'Failed to export PDF: {str(e)}', 'details': error_details},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get note version history"""
        note = self.get_object()
        versions = note.versions.all()
        serializer = NoteVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore_version(self, request, pk=None):
        """Restore a specific version"""
        note = self.get_object()
        version_id = request.data.get('version_id')
        
        try:
            version = NoteVersion.objects.get(id=version_id, note=note)
            
            # Create new version before restoring
            self._create_version_snapshot(note)
            
            # Restore from snapshot
            self._restore_from_snapshot(note, version.snapshot)
            
            serializer = self.get_serializer(note)
            return Response(serializer.data)
        except NoteVersion.DoesNotExist:
            return Response(
                {'error': 'Version not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def _create_version_snapshot(self, note):
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
        
        NoteVersion.objects.create(
            note=note,
            version_number=version_number,
            snapshot=snapshot,
            changes_summary=f"Auto-save at {note.updated_at}"
        )
    
    def destroy(self, request, *args, **kwargs):
        """Delete note with proper cascade deletion - FIXED for roadmap_tasks issue"""
        note = self.get_object()
        note_title = note.title
        
        try:
            with transaction.atomic():
                # Check if roadmap_tasks table exists
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'roadmap_tasks'
                        );
                    """)
                    roadmap_tasks_exists = cursor.fetchone()[0]
                
                # If roadmap_tasks exists, clear the foreign key reference
                if roadmap_tasks_exists:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            "UPDATE roadmap_tasks SET note_id = NULL WHERE note_id = %s;",
                            [note.id]
                        )
                
                # Get all topic IDs for AI content deletion
                topic_ids = list(ChapterTopic.objects.filter(
                    chapter__note=note
                ).values_list('id', flat=True))
                
                # Delete all chapters and their topics
                for chapter in note.chapters.all():
                    for topic in chapter.topics.all():
                        # Delete related objects
                        if topic.explanation:
                            topic.explanation.delete()
                        if topic.code_snippet:
                            topic.code_snippet.delete()
                        if topic.source:
                            topic.source.delete()
                        topic.delete()
                    chapter.delete()
                
                # Delete AI generated content
                AIGeneratedContent.objects.filter(topic_id__in=topic_ids).delete()
                
                # Delete note versions
                note.versions.all().delete()
                
                # Delete note shares
                note.shares.all().delete()
                
                # Delete the note
                note.delete()
            
            return Response(
                {
                    'message': f'Note "{note_title}" has been successfully deleted.',
                    'success': True
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error deleting note: {error_details}")
            return Response(
                {
                    'error': f'Failed to delete note: {str(e)}',
                    'details': error_details,
                    'success': False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _restore_from_snapshot(self, note, snapshot):
        """Restore note from snapshot"""
        with transaction.atomic():
            # Update note fields
            note.title = snapshot.get('title', note.title)
            note.tags = snapshot.get('tags', note.tags)
            note.status = snapshot.get('status', note.status)
            note.save()
            
            # Delete existing chapters
            note.chapters.all().delete()
            
            # Recreate chapters and topics
            for chapter_data in snapshot.get('chapters', []):
                chapter = Chapter.objects.create(
                    note=note,
                    title=chapter_data['title'],
                    order=chapter_data['order']
                )
                
                for topic_data in chapter_data.get('topics', []):
                    topic = ChapterTopic.objects.create(
                        chapter=chapter,
                        name=topic_data['name'],
                        order=topic_data['order']
                    )
                    
                    # Create explanation
                    if topic_data.get('explanation'):
                        explanation = TopicExplanation.objects.create(
                            content=topic_data['explanation']
                        )
                        topic.explanation = explanation
                    
                    # Create code snippet
                    if topic_data.get('code_snippet'):
                        code = TopicCodeSnippet.objects.create(
                            language=topic_data['code_snippet']['language'],
                            code=topic_data['code_snippet']['code']
                        )
                        topic.code_snippet = code
                    
                    # Create source
                    if topic_data.get('source'):
                        source = TopicSource.objects.create(
                            title=topic_data['source']['title'],
                            url=topic_data['source']['url']
                        )
                        topic.source = source
                    
                    topic.save()


class ChapterViewSet(viewsets.ModelViewSet):
    """Chapter CRUD operations"""
    
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Chapter.objects.filter(
            note__user=self.request.user
        ).prefetch_related('topics').order_by('order')
    
    def create(self, request):
        note_id = request.data.get('note_id')
        
        if not note_id:
            return Response(
                {'error': 'note_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            note = Note.objects.get(id=note_id, user=request.user)
        except Note.DoesNotExist:
            return Response(
                {'error': 'Note not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        title = request.data.get('title', '').strip()
        if not title:
            return Response(
                {'error': 'Chapter title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get next order number
        max_order_result = Chapter.objects.filter(note=note).aggregate(
            max_order=Max('order')
        )
        max_order = max_order_result['max_order']
        next_order = (max_order + 1) if max_order is not None else 0
        
        try:
            chapter = Chapter.objects.create(
                note=note,
                title=title,
                order=next_order
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to create chapter: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        serializer = self.get_serializer(chapter)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update chapter - support both PUT and PATCH"""
        partial = kwargs.pop('partial', False)
        chapter = self.get_object()
        
        serializer = self.get_serializer(chapter, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete chapter with all its topics"""
        chapter = self.get_object()
        chapter_title = chapter.title
        
        try:
            with transaction.atomic():
                # Delete all topics and their related objects
                for topic in chapter.topics.all():
                    if topic.explanation:
                        topic.explanation.delete()
                    if topic.code_snippet:
                        topic.code_snippet.delete()
                    if topic.source:
                        topic.source.delete()
                    topic.delete()
                
                # Delete the chapter
                chapter.delete()
            
            return Response(
                {
                    'message': f'Chapter "{chapter_title}" has been successfully deleted.',
                    'success': True
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'error': f'Failed to delete chapter: {str(e)}',
                    'success': False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder chapter"""
        chapter = self.get_object()
        new_order = request.data.get('order')
        
        if new_order is not None:
            chapter.order = new_order
            chapter.save()
        
        serializer = self.get_serializer(chapter)
        return Response(serializer.data)


class TopicViewSet(viewsets.ModelViewSet):
    """Topic CRUD operations"""
    
    serializer_class = ChapterTopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChapterTopic.objects.filter(
            chapter__note__user=self.request.user
        ).select_related('explanation', 'code_snippet', 'source').order_by('order')
    
    def create(self, request):
        """Create topic with optional components"""
        serializer = TopicCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        chapter_id = data['chapter_id']
        
        try:
            chapter = Chapter.objects.get(id=chapter_id, note__user=request.user)
        except Chapter.DoesNotExist:
            return Response(
                {'error': 'Chapter not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        with transaction.atomic():
            # Calculate next order number
            max_order_result = ChapterTopic.objects.filter(chapter=chapter).aggregate(
                max_order=Max('order')
            )
            max_order = max_order_result['max_order']
            next_order = (max_order + 1) if max_order is not None else 0
            
            # Create topic
            topic = ChapterTopic.objects.create(
                chapter=chapter,
                name=data['name'],
                order=next_order
            )
            
            # Create explanation if provided
            if data.get('explanation_content'):
                explanation = TopicExplanation.objects.create(
                    content=data['explanation_content']
                )
                topic.explanation = explanation
            
            # Create code snippet if provided
            if data.get('code_content'):
                code = TopicCodeSnippet.objects.create(
                    language=data.get('code_language', 'python'),
                    code=data['code_content']
                )
                topic.code_snippet = code
            
            # Create source if provided
            if data.get('source_url'):
                source = TopicSource.objects.create(
                    title=data.get('source_title', 'Reference'),
                    url=data['source_url']
                )
                topic.source = source
            
            topic.save()
        
        response_serializer = ChapterTopicSerializer(topic)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update topic and its components - FIXED partial parameter"""
        # Handle partial parameter correctly
        partial = kwargs.pop('partial', False)
        
        topic = self.get_object()
        serializer = TopicUpdateSerializer(data=request.data, partial=True)  # Always allow partial
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        with transaction.atomic():
            # Update topic fields
            if 'name' in data:
                topic.name = data['name']
            if 'order' in data:
                topic.order = data['order']
            
            # Update explanation
            if 'explanation_content' in data:
                if topic.explanation:
                    topic.explanation.content = data['explanation_content']
                    topic.explanation.save()
                elif data['explanation_content']:
                    explanation = TopicExplanation.objects.create(
                        content=data['explanation_content']
                    )
                    topic.explanation = explanation
            
            # Update code snippet
            if 'code_content' in data:
                if topic.code_snippet:
                    topic.code_snippet.code = data['code_content']
                    if 'code_language' in data:
                        topic.code_snippet.language = data['code_language']
                    topic.code_snippet.save()
                elif data['code_content']:
                    code = TopicCodeSnippet.objects.create(
                        language=data.get('code_language', 'python'),
                        code=data['code_content']
                    )
                    topic.code_snippet = code
            
            # Update source
            if 'source_url' in data:
                if topic.source:
                    topic.source.url = data['source_url']
                    if 'source_title' in data:
                        topic.source.title = data['source_title']
                    topic.source.save()
                elif data['source_url']:
                    source = TopicSource.objects.create(
                        title=data.get('source_title', 'Reference'),
                        url=data['source_url']
                    )
                    topic.source = source
            
            topic.save()
        
        response_serializer = ChapterTopicSerializer(topic)
        return Response(response_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete topic with all its related objects"""
        topic = self.get_object()
        topic_name = topic.name
        
        try:
            with transaction.atomic():
                # Delete related objects
                if topic.explanation:
                    topic.explanation.delete()
                if topic.code_snippet:
                    topic.code_snippet.delete()
                if topic.source:
                    topic.source.delete()
                
                # Delete the topic
                topic.delete()
            
            return Response(
                {
                    'message': f'Topic "{topic_name}" has been successfully deleted.',
                    'success': True
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    'error': f'Failed to delete topic: {str(e)}',
                    'success': False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def ai_action(self, request, pk=None):
        """Perform AI action on topic using Groq"""
        topic = self.get_object()
        serializer = AIActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action_type']
        input_content = serializer.validated_data['input_content']
        
        try:
            # Perform AI action
            generated_content = None
            
            if action_type == 'generate_explanation':
                generated_content = generate_ai_explanation(input_content)
            elif action_type == 'improve_explanation':
                generated_content = improve_explanation(input_content)
            elif action_type == 'summarize_explanation':
                generated_content = summarize_explanation(input_content)
            elif action_type == 'generate_code':
                language = serializer.validated_data.get('language', 'python')
                generated_content = generate_ai_code(input_content, language)
            
            # Save AI generation record
            AIGeneratedContent.objects.create(
                user=request.user,
                topic=topic,
                action_type=action_type,
                input_content=input_content,
                generated_content=generated_content,
                model_used='llama-3.3-70b-versatile'
            )
            
            return Response({
                'generated_content': generated_content,
                'action_type': action_type,
                'success': True
            })
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"AI Action Error: {error_details}")
            return Response(
                {
                    'error': f'AI action failed: {str(e)}',
                    'details': error_details,
                    'success': False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def reorder(self, request, pk=None):
        """Reorder topic"""
        topic = self.get_object()
        new_order = request.data.get('order')
        
        if new_order is not None:
            topic.order = new_order
            topic.save()
        
        serializer = self.get_serializer(topic)
        return Response(serializer.data)


class NoteShareViewSet(viewsets.ModelViewSet):
    """Share notes with others"""
    
    serializer_class = NoteShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NoteShare.objects.filter(
            Q(shared_by=self.request.user) | Q(shared_with=self.request.user)
        )