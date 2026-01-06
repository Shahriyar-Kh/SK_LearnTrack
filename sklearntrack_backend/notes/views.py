# FILE: notes/views.py - COMPLETE FIXED VERSION
# ============================================================================

import logging
from sqlite3 import IntegrityError

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
from rest_framework.decorators import api_view  # Add this import

import os
from django.conf import settings
from .code_execution_service import CodeExecutionService

# Import the unified Google Drive service
from .google_drive_service import GoogleDriveService, GoogleAuthService, SCOPES
from .daily_report_service import DailyNotesReportService  # FIX: Add this import

from .models import (
    Note, Chapter, ChapterTopic, TopicExplanation,
    TopicCodeSnippet, TopicSource, NoteVersion,
    AIGeneratedContent, NoteShare
)
from .serializers import (
    NoteListSerializer, NoteDetailSerializer, NoteCreateSerializer, ChapterSerializer,
    ChapterTopicSerializer, NoteVersionSerializer, AIGeneratedContentSerializer,
    NoteShareSerializer, AIActionSerializer, TopicCreateSerializer,
    TopicUpdateSerializer
)
from .ai_service import (
    generate_ai_explanation,
    generate_ai_code,
    improve_explanation,
    summarize_explanation
)
from .pdf_service import export_note_to_pdf

logger = logging.getLogger(__name__)


class NoteViewSet(viewsets.ModelViewSet):
    """Note CRUD with chapters and topics"""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        elif self.action == 'create':
            return NoteCreateSerializer
        return NoteDetailSerializer
    
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
        
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = tags.split(',')
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag.strip()])
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(tags__contains=[search]) |
                Q(chapters__title__icontains=search) |
                Q(chapters__topics__name__icontains=search)
            ).distinct()
        
        return queryset.order_by('-updated_at')
    
    def create(self, request, *args, **kwargs):
        """Create note with case-insensitive unique title validation"""
        title = request.data.get('title', '').strip()
        
        if not title:
            return Response(
                {'error': 'Note title is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if note with same title exists (case-insensitive)
        if Note.objects.check_exists('title', title, user=request.user):
            return Response(
                {'error': f'A note titled "{title}" already exists (case-insensitive). Please choose a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            # Add user to validated data
            validated_data = serializer.validated_data
            validated_data['user'] = request.user
            
            # Create the note
            note = Note.objects.create(**validated_data)
            
            # Return response with the created note
            response_serializer = NoteDetailSerializer(note, context={'request': request})
            headers = self.get_success_headers(response_serializer.data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            import traceback
            logger.error(f"Note creation error: {traceback.format_exc()}")
            return Response(
                {'error': f'Failed to create note: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Update note with proper error handling"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except IntegrityError as e:
            error_str = str(e).lower()
            if 'unique_user_note_title' in error_str or 'duplicate' in error_str:
                return Response(
                    {'error': f'You already have a note titled "{request.data.get("title", "")}". Please choose a different name.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': 'Failed to update note: Database constraint violation'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def structure(self, request, pk=None):
        """Get full note structure"""
        note = self.get_object()
        serializer = NoteDetailSerializer(note, context={'request': request})
        return Response(serializer.data)
    
    # In views.py, update the export_pdf action:
    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        """Export note to PDF"""
        note = self.get_object()
        
        try:
            pdf_file = export_note_to_pdf(note)
            
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            filename = f"note_{note.slug}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = pdf_file.size
            
            # Log success
            logger.info(f"PDF exported successfully for note {note.id}, size: {pdf_file.size} bytes")
            
            return response
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            logger.error(f"PDF Export Error for note {note.id}: {error_details}")
            return Response(
                {
                    'error': f'Failed to export PDF: {str(e)}',
                    'details': 'Please check the server logs for more information'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content_type='application/json'
            )
    
    @action(detail=False, methods=['get'])
    def drive_status(self, request):
        """Check Google Drive connection status"""
        try:
            drive_service = GoogleDriveService(request.user)
            is_connected = drive_service.is_connected()
            
            return Response({
                'connected': is_connected,
                'can_export': is_connected
            })
        except Exception as e:
            logger.error(f"Drive status check error: {e}")
            return Response({
                'connected': False,
                'can_export': False,
                'error': str(e)
            })
    
    @action(detail=True, methods=['post'])
    def export_to_drive(self, request, pk=None):
        """Export note to Google Drive (manual upload)"""
        note = self.get_object()
        
        try:
            # Initialize Drive service
            drive_service = GoogleDriveService(request.user)
            
            # Generate PDF
            pdf_file = export_note_to_pdf(note)
            
            # Upload or update
            filename = f"{note.title}_{timezone.now().date()}.pdf"
            result = drive_service.upload_or_update_pdf(
                pdf_file,
                filename,
                existing_file_id=note.drive_file_id
            )
            
            if result['success']:
                # Update note metadata
                note.drive_file_id = result['id']
                note.last_drive_sync_at = timezone.now()
                note.upload_type = 'manual'
                note.save()
                
                return Response({
                    'success': True,
                    'message': 'Updated in Google Drive' if result.get('updated') else 'Uploaded to Google Drive',
                    'drive_link': result.get('webViewLink'),
                    'file_id': result.get('id'),
                    'updated': result.get('updated', False)
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            error_msg = str(e)
            if 'authentication required' in error_msg.lower():
                return Response({
                    'success': False,
                    'error': 'Google Drive authentication required',
                    'needs_auth': True
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            import traceback
            logger.error(f"Drive Export Error: {traceback.format_exc()}")
            return Response({
                'success': False,
                'error': error_msg
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def google_auth_url(self, request):
        """Get Google OAuth URL"""
        try:
            from google_auth_oauthlib.flow import Flow
            import secrets
            
            client_secret_path = os.path.join(
                settings.BASE_DIR.parent,
                'client_secret.json'
            )
            
            if not os.path.exists(client_secret_path):
                return Response({
                    'success': False,
                    'error': 'Google Drive not configured. Please add client_secret.json'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Generate secure state token with user_id embedded - FIX: Use colon separator
            random_token = secrets.token_urlsafe(32)
            state = f"{request.user.id}:{random_token}"  # CHANGE: Use colon, not underscore
            
            # Store in session with explicit saving
            request.session['google_auth_state'] = state
            request.session['google_auth_user_id'] = request.user.id
            request.session['user_id'] = request.user.id
            
            # Force session to save
            request.session.save()
            
            logger.info(f"Generated state for user {request.user.id}: {state}")
            logger.info(f"Session saved with ID: {request.session.session_key}")
            
            # Create redirect URI
            redirect_uri = 'http://localhost:8000/api/notes/google-callback/'
            
            flow = Flow.from_client_secrets_file(
                client_secret_path,
                scopes=SCOPES,
                redirect_uri=redirect_uri
            )
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            logger.info(f"Generated auth URL for user {request.user.id}")
            
            return Response({
                'success': True,
                'auth_url': authorization_url,
                'state': state,
                'user_id': request.user.id,
                'session_key': request.session.session_key
            })
            
        except Exception as e:
            logger.error(f"Auth URL generation error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        """
        USER-based daily report (works even if no notes exist)
        """
        try:
            report_data = DailyNotesReportService.generate_daily_report(request.user)

            return Response({
                'success': True,
                'report': {
                    'date': report_data['date'],
                    'notes_created': report_data['notes_created'],
                    'notes_updated': report_data['notes_updated'],
                    'topics_created': report_data['topics_created'],
                    'study_time_estimate': report_data['study_time_estimate'],
                    'notes_list': [
                        {
                            'id': note.id,
                            'title': note.title,
                            'status': note.status,
                            'chapters_count': note.chapters.count()
                        }
                        for note in report_data['notes_list']
                    ]
                }
            })
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['post'])
    def send_daily_report_email(self, request):
        """
        Send daily report email (no note ID required)
        """
        try:
            report_data = DailyNotesReportService.generate_daily_report(request.user)
            success = DailyNotesReportService.send_daily_report_email(
                request.user,
                report_data
            )

            if success:
                return Response({
                    'success': True,
                    'message': 'Daily report sent to your email'
                })

            return Response(
                {'success': False, 'error': 'Failed to send email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except Exception as e:
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
    def destroy(self, request, *args, **kwargs):
        """Delete note with proper cleanup"""
        note = self.get_object()
        note_title = note.title
        
        try:
            with transaction.atomic():
                # Clear roadmap_tasks reference if table exists
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'roadmap_tasks'
                        );
                    """)
                    if cursor.fetchone()[0]:
                        cursor.execute(
                            "UPDATE roadmap_tasks SET note_id = NULL WHERE note_id = %s;",
                            [note.id]
                        )
                
                # Delete note (cascade will handle related objects)
                note.delete()
            
            return Response({
                'message': f'Note "{note_title}" deleted successfully',
                'success': True
            })
        except Exception as e:
            import traceback
            print(f"Delete Error: {traceback.format_exc()}")
            return Response({
                'error': f'Failed to delete note: {str(e)}',
                'success': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        
        # Check if chapter with same title exists (case-insensitive)
        if Chapter.objects.check_exists('title', title, note=note):
            return Response(
                {'error': f'A chapter titled "{title}" already exists in this note (case-insensitive). Please use a different name.'},
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
        except IntegrityError:
            return Response(
                {'error': f'A chapter titled "{title}" already exists in this note. Please use a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import traceback
            print(f"Chapter Creation Error: {traceback.format_exc()}")
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
        """Create topic with case-insensitive validation"""
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
        
        topic_name = data['name'].strip()
        
        # Check if topic with same name exists (case-insensitive)
        if ChapterTopic.objects.check_exists('name', topic_name, chapter=chapter):
            return Response(
                {'error': f'Topic "{topic_name}" already exists in this chapter (case-insensitive). Please use a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate next order number
        max_order_result = ChapterTopic.objects.filter(chapter=chapter).aggregate(
            max_order=Max('order')
        )
        max_order = max_order_result['max_order']
        next_order = (max_order + 1) if max_order is not None else 0

        try:
            with transaction.atomic():
                # Create topic
                topic = ChapterTopic.objects.create(
                    chapter=chapter,
                    name=topic_name,
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

        except IntegrityError:
            return Response(
                {'error': f'Topic "{topic_name}" already exists in this chapter. Please use a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
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

# Add this view function
@api_view(['POST'])
def execute_code(request):
    """Execute code and return results with detailed error handling"""
    code = request.data.get('code', '')
    language = request.data.get('language', 'python')
    
    if not code:
        return Response({'error': 'No code provided'}, status=400)
    
    try:
        result = CodeExecutionService.execute_code(code, language)
        
        # Format error output to look like VS Code
        if result.get('error') and not result.get('success'):
            error_output = result.get('output', '')
            formatted_error = format_error_output(error_output, language, code)
            result['formatted_error'] = formatted_error
            result['has_line_numbers'] = True
        
        return Response(result)
    except Exception as e:
        logger.error(f"Code execution error: {str(e)}")
        return Response({
            'success': False,
            'output': f"Execution failed: {str(e)}",
            'error': True,
            'formatted_error': format_generic_error(str(e), code)
        }, status=500)


def format_error_output(error_output, language, original_code):
    """Format error output to look like VS Code with line numbers"""
    lines = original_code.split('\n')
    formatted_error = []
    
    # Add line numbers to the code
    for i, line in enumerate(lines, 1):
        formatted_error.append(f"{i:3d} | {line}")
    
    formatted_error.append("\n" + "═" * 80 + "\n")
    formatted_error.append("🚨 ERROR OUTPUT:\n")
    
    # Parse and format error messages
    if language == 'python':
        # Format Python errors
        error_lines = error_output.split('\n')
        for error_line in error_lines:
            if 'File' in error_line and 'line' in error_line:
                # Extract line number from traceback
                import re
                match = re.search(r'line (\d+)', error_line)
                if match:
                    line_num = int(match.group(1))
                    formatted_error.append(f"❌ Error at line {line_num}: {error_line}")
                else:
                    formatted_error.append(f"❌ {error_line}")
            elif 'Error:' in error_line or 'error:' in error_line.lower():
                formatted_error.append(f"🔥 {error_line}")
            elif error_line.strip():
                formatted_error.append(f"   {error_line}")
    elif language in ['javascript', 'typescript']:
        # Format JavaScript errors
        error_lines = error_output.split('\n')
        for error_line in error_lines:
            if 'at' in error_line and ('.js:' in error_line or '.ts:' in error_line):
                formatted_error.append(f"🔧 {error_line}")
            elif 'Error:' in error_line or 'error:' in error_line.lower():
                formatted_error.append(f"🔥 {error_line}")
            elif error_line.strip():
                formatted_error.append(f"   {error_line}")
    elif language in ['java', 'cpp', 'c']:
        # Format Java/C++ errors
        error_lines = error_output.split('\n')
        for error_line in error_lines:
            if '.java:' in error_line or '.cpp:' in error_line or '.c:' in error_line:
                formatted_error.append(f"🔧 {error_line}")
            elif 'error:' in error_line.lower() or 'Error:' in error_line:
                formatted_error.append(f"🔥 {error_line}")
            elif error_line.strip():
                formatted_error.append(f"   {error_line}")
    else:
        # Generic formatting for other languages
        formatted_error.append(error_output)
    
    return '\n'.join(formatted_error)


def format_generic_error(error_message, code):
    """Format generic errors with code context"""
    lines = code.split('\n')
    formatted = []
    
    formatted.append("📋 YOUR CODE:")
    for i, line in enumerate(lines, 1):
        formatted.append(f"{i:3d} | {line}")
    
    formatted.append("\n" + "═" * 80 + "\n")
    formatted.append(f"🚨 SERVER ERROR: {error_message}")
    formatted.append("\n💡 TROUBLESHOOTING:")
    formatted.append("• Check if the programming language is supported")
    formatted.append("• Make sure your code syntax is correct")
    formatted.append("• For timeouts, simplify your code")
    formatted.append("• Check for infinite loops")
    
    return '\n'.join(formatted)