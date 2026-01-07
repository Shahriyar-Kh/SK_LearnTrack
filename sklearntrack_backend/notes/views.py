# FILE: notes/views.py - REFACTORED WITH SERVICES
# ============================================================================

import logging
from django.core.exceptions import ValidationError

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, permission_classes, api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction, connection
from django.db.models import Q, Count, Prefetch, Max
from django.http import HttpResponse
from django.utils import timezone
from uuid import uuid4

import os
from django.conf import settings
from .code_execution_service import CodeExecutionService

# Import services
from .google_drive_service import GoogleDriveService, GoogleAuthService, SCOPES
from .daily_report_service import DailyNotesReportService
from .services import NoteService, ChapterService, TopicService

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
        """Create note using NoteService"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use NoteService to create note
            note = NoteService.create_note(
                user=request.user,
                **serializer.validated_data
            )
            
            response_serializer = NoteDetailSerializer(note, context={'request': request})
            headers = self.get_success_headers(response_serializer.data)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Note creation error: {str(e)}")
            return Response(
                {'error': f'Failed to create note: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Update note using NoteService"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        try:
            # Use NoteService to update note
            updated_note = NoteService.update_note(instance, **serializer.validated_data)
            response_serializer = NoteDetailSerializer(updated_note, context={'request': request})
            return Response(response_serializer.data)
            
        except ValidationError as e:
            return Response(
                {'error': str(e.message) if hasattr(e, 'message') else str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Note update error: {str(e)}")
            return Response(
                {'error': 'Failed to update note'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def structure(self, request, pk=None):
        """Get full note structure"""
        note = self.get_object()
        serializer = NoteDetailSerializer(note, context={'request': request})
        return Response(serializer.data)
    
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
            
            logger.info(f"PDF exported successfully for note {note.id}, size: {pdf_file.size} bytes")
            return response
            
        except Exception as e:
            logger.error(f"PDF Export Error for note {note.id}: {str(e)}")
            return Response(
                {'error': f'Failed to export PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        """Export note to Google Drive"""
        note = self.get_object()
        
        try:
            drive_service = GoogleDriveService(request.user)
            pdf_file = export_note_to_pdf(note)
            
            filename = f"{note.title}_{timezone.now().date()}.pdf"
            result = drive_service.upload_or_update_pdf(
                pdf_file,
                filename,
                existing_file_id=note.drive_file_id
            )
            
            if result['success']:
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
            
            logger.error(f"Drive Export Error: {str(e)}")
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
            
            random_token = secrets.token_urlsafe(32)
            state = f"{request.user.id}:{random_token}"
            
            request.session['google_auth_state'] = state
            request.session['google_auth_user_id'] = request.user.id
            request.session['user_id'] = request.user.id
            request.session.save()
            
            logger.info(f"Generated state for user {request.user.id}: {state}")
            
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
            
            return Response({
                'success': True,
                'auth_url': authorization_url,
                'state': state,
                'user_id': request.user.id,
                'session_key': request.session.session_key
            })
            
        except Exception as e:
            logger.error(f"Auth URL generation error: {str(e)}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'])
    def daily_report(self, request):
        """User-based daily report"""
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
        """Send daily report email"""
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
        """Delete note using NoteService"""
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
                
                # Use NoteService to delete
                NoteService.delete_note(note)
            
            return Response({
                'message': f'Note "{note_title}" deleted successfully',
                'success': True
            })
        except Exception as e:
            logger.error(f"Delete Error: {str(e)}")
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
        """Create chapter using ChapterService"""
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
                {'error': f'A chapter titled "{title}" already exists in this note (case-insensitive).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use ChapterService to create chapter
            chapter = ChapterService.create_chapter(note, title)
            serializer = self.get_serializer(chapter)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Chapter Creation Error: {str(e)}")
            return Response(
                {'error': f'Failed to create chapter: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def update(self, request, *args, **kwargs):
        """Update chapter using ChapterService"""
        partial = kwargs.pop('partial', False)
        chapter = self.get_object()
        
        serializer = self.get_serializer(chapter, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use ChapterService to update
            updated_chapter = ChapterService.update_chapter(chapter, **serializer.validated_data)
            response_serializer = self.get_serializer(updated_chapter)
            return Response(response_serializer.data)
        except Exception as e:
            logger.error(f"Chapter update error: {str(e)}")
            return Response(
                {'error': 'Failed to update chapter'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete chapter using ChapterService"""
        chapter = self.get_object()
        chapter_title = chapter.title
        
        try:
            # Use ChapterService to delete
            ChapterService.delete_chapter(chapter)
            
            return Response(
                {
                    'message': f'Chapter "{chapter_title}" has been successfully deleted.',
                    'success': True
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Chapter delete error: {str(e)}")
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
            ChapterService.update_chapter(chapter, order=new_order)
        
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
        """Create topic using TopicService"""
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
                {'error': f'Topic "{topic_name}" already exists in this chapter (case-insensitive).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Use TopicService to create topic
            topic = TopicService.create_topic(
                chapter=chapter,
                name=topic_name,
                explanation_content=data.get('explanation_content'),
                code_language=data.get('code_language', 'python'),
                code_content=data.get('code_content'),
                source_title=data.get('source_title'),
                source_url=data.get('source_url')
            )
            
            response_serializer = ChapterTopicSerializer(topic)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Topic creation error: {str(e)}")
            return Response(
                {'error': f'Failed to create topic: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        """Update topic using TopicService"""
        partial = kwargs.pop('partial', False)
        topic = self.get_object()
        
        serializer = TopicUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Use TopicService to update topic
            updated_topic = TopicService.update_topic(topic, **serializer.validated_data)
            response_serializer = ChapterTopicSerializer(updated_topic)
            return Response(response_serializer.data)
            
        except Exception as e:
            logger.error(f"Topic update error: {str(e)}")
            return Response(
                {'error': 'Failed to update topic'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """Delete topic using TopicService"""
        topic = self.get_object()
        topic_name = topic.name
        
        try:
            # Use TopicService to delete
            TopicService.delete_topic(topic)
            
            return Response(
                {
                    'message': f'Topic "{topic_name}" has been successfully deleted.',
                    'success': True
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Topic delete error: {str(e)}")
            return Response(
                {
                    'error': f'Failed to delete topic: {str(e)}',
                    'success': False
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def ai_action(self, request, pk=None):
        """Perform AI action on topic"""
        topic = self.get_object()
        serializer = AIActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action_type']
        input_content = serializer.validated_data['input_content']
        
        try:
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
            logger.error(f"AI Action Error: {str(e)}")
            return Response(
                {
                    'error': f'AI action failed: {str(e)}',
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
            TopicService.update_topic(topic, order=new_order)
        
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


# ============================================================================
# CODE EXECUTION API
# ============================================================================

def extract_input_requirements(code, language):
    """Check if code requires input"""
    if not code:
        return False
    
    patterns = {
        'python': [r'input\s*\(', r'raw_input\s*\('],
        'java': [r'Scanner\s*\.\s*', r'System\.in', r'BufferedReader'],
        'c': [r'scanf\s*\(', r'gets\s*\(', r'fgets\s*\('],
        'cpp': [r'cin\s*>>', r'getline\s*\(', r'std::cin'],
        'javascript': [r'prompt\s*\(', r'readline\s*\(', r'console\.read'],
        'go': [r'fmt\.Scan', r'bufio\.NewReader'],
    }
    
    if language in patterns:
        import re
        for pattern in patterns[language]:
            if re.search(pattern, code, re.IGNORECASE):
                return True
    return False


@api_view(['POST'])
@permission_classes([AllowAny])
def execute_code(request):
    """Execute code with input support"""
    code = request.data.get('code', '')
    language = request.data.get('language', 'python')
    stdin = request.data.get('stdin', '')
    
    if not code:
        return Response({'success': False, 'error': 'No code provided'}, status=400)
    
    # Validate code length
    if len(code) > 10000:
        return Response({
            'success': False, 
            'error': 'Code is too long. Maximum 10,000 characters allowed.'
        }, status=400)
    
    try:
        # Check if code requires input but stdin is not provided
        requires_input = extract_input_requirements(code, language)
        if requires_input and not stdin:
            return Response({
                'success': False,
                'output': '',
                'error': f'This {language} code requires input. Please provide input in the stdin field.',
                'exit_code': None,
                'runtime_ms': 0,
                'requires_input': True
            })
        
        # Execute code
        result = CodeExecutionService.execute_code(
            code=code,
            language=language,
            stdin=stdin
        )
        
        # Format output for display
        if not result.get('success'):
            error = result.get('error', '')
            if not error and result.get('output'):
                error = result.get('output')
            
            result['formatted_error'] = format_error_output(
                error,
                language,
                code
            )
        else:
            output = result.get('output', '').strip()
            if output:
                result['formatted_output'] = f"✅ Execution Successful\n\n{output}"
                if result.get('runtime_ms'):
                    result['formatted_output'] += f"\n\n⏱️ Runtime: {result['runtime_ms']}ms"
        
        return Response(result)
        
    except Exception as e:
        logger.error(f"Code execution error: {str(e)}")
        return Response({
            'success': False,
            'output': '',
            'error': f'Server error: {str(e)}',
            'formatted_error': f"🚨 Server Error\n\n{str(e)}\n\nPlease try again or contact support."
        }, status=500)


def format_error_output(error_output, language, original_code):
    """Format error output to look like VS Code with line numbers"""
    if not error_output:
        error_output = "No error output received"
    
    lines = original_code.split('\n')
    formatted_error = []
    
    # Add header
    formatted_error.append("🔍 CODE WITH LINE NUMBERS:\n")
    formatted_error.append("=" * 80)
    
    # Add line numbers to the code
    for i, line in enumerate(lines, 1):
        line_num = f"{i:3d}"
        formatted_error.append(f"{line_num} | {line}")
    
    formatted_error.append("=" * 80)
    formatted_error.append("\n🚨 ERROR DETAILS:\n")
    
    # Clean and format error message
    error_lines = error_output.split('\n')
    
    # Remove any empty lines at start/end
    while error_lines and not error_lines[0].strip():
        error_lines.pop(0)
    while error_lines and not error_lines[-1].strip():
        error_lines.pop(-1)
    
    # Format based on language
    for error_line in error_lines:
        error_line = error_line.strip()
        if not error_line:
            continue
            
        # Highlight specific patterns
        if any(keyword in error_line.lower() for keyword in ['error:', 'exception:', 'traceback', 'failed', 'undefined']):
            formatted_error.append(f"🔥 {error_line}")
        elif any(keyword in error_line.lower() for keyword in ['warning:', 'note:', 'hint:']):
            formatted_error.append(f"⚠️  {error_line}")
        elif 'line' in error_line.lower() and ('file' in error_line.lower() or '.py' in error_line or '.js' in error_line):
            formatted_error.append(f"📍 {error_line}")
        else:
            formatted_error.append(f"   {error_line}")
    
    # Add debugging tips
    formatted_error.append("\n" + "=" * 80)
    formatted_error.append("\n💡 DEBUGGING TIPS:")
    
    if language == 'python':
        formatted_error.append("• Check for syntax errors (missing colons, parentheses, etc.)")
        formatted_error.append("• Verify all variables are defined before use")
        formatted_error.append("• Ensure proper indentation (Python is strict about this!)")
        formatted_error.append("• Check for infinite loops or recursion")
    elif language in ['javascript', 'typescript']:
        formatted_error.append("• Check for missing semicolons or braces")
        formatted_error.append("• Verify variable declarations (let/const/var)")
        formatted_error.append("• Check for undefined variables or functions")
    elif language in ['java', 'cpp', 'c']:
        formatted_error.append("• Check for missing semicolons or braces")
        formatted_error.append("• Verify all required imports/includes")
        formatted_error.append("• Check for type mismatches")
    
    return '\n'.join(formatted_error)