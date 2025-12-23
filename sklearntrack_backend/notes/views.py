# FILE: notes/views.py
# ============================================================================

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q, Count
from datetime import date, timedelta

from .models import (
    Note, NoteVersion, CodeSnippet, NoteSource,
    NoteTemplate, DailyNoteReport, AIGeneratedNote,
    YouTubeTranscript, NoteShare
)
from .serializers import (
    NoteListSerializer, NoteDetailSerializer, NoteVersionSerializer,
    CodeSnippetSerializer, NoteSourceSerializer, NoteTemplateSerializer,
    DailyNoteReportSerializer, AIGeneratedNoteSerializer,
    YouTubeTranscriptSerializer, NoteShareSerializer,
    AIActionSerializer, YouTubeImportSerializer, ExportNoteSerializer
)
from .utils import (
    generate_ai_summary, generate_ai_expansion, generate_ai_rewrite,
    fetch_youtube_transcript, generate_notes_from_transcript,
    export_note_to_pdf, generate_daily_report_pdf
)


class NoteViewSet(viewsets.ModelViewSet):
    """Enhanced Note management with AI and export features"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        return NoteDetailSerializer
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user).prefetch_related(
            'sources', 'code_snippets'
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
                Q(content__icontains=search) |
                Q(tags__contains=[search])
            )
        
        # Date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        
        return queryset.order_by('-updated_at')
    
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
            note.content = version.content
            note.content_json = version.content_json
            note.save()
            
            serializer = self.get_serializer(note)
            return Response(serializer.data)
        except NoteVersion.DoesNotExist:
            return Response(
                {'error': 'Version not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """Duplicate a note"""
        note = self.get_object()
        new_note = Note.objects.create(
            user=request.user,
            title=f"{note.title} (Copy)",
            content=note.content,
            content_json=note.content_json,
            tags=note.tags,
            status='draft',
            course=note.course,
            topic=note.topic,
            subtopic=note.subtopic
        )
        
        # Copy sources
        new_note.sources.set(note.sources.all())
        
        serializer = self.get_serializer(new_note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def ai_action(self, request):
        """Perform AI actions on content"""
        serializer = AIActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action_type']
        content = serializer.validated_data['content']
        note_id = serializer.validated_data.get('note_id')
        
        # Get note if provided
        note = None
        if note_id:
            try:
                note = Note.objects.get(id=note_id, user=request.user)
            except Note.DoesNotExist:
                pass
        
        # Perform AI action
        generated_content = None
        if 'summarize' in action_type:
            length = action_type.split('_')[1]  # short, medium, detailed
            generated_content = generate_ai_summary(content, length)
        elif action_type == 'expand':
            generated_content = generate_ai_expansion(content)
        elif action_type == 'rewrite':
            generated_content = generate_ai_rewrite(content)
        elif action_type == 'breakdown':
            generated_content = generate_ai_rewrite(content, mode='breakdown')
        
        # Save AI generation record
        ai_note = AIGeneratedNote.objects.create(
            user=request.user,
            note=note,
            action_type=action_type,
            source_content=content,
            generated_content=generated_content,
            model_used='gpt-4'
        )
        
        return Response({
            'generated_content': generated_content,
            'ai_note_id': ai_note.id
        })
    
    @action(detail=False, methods=['post'])
    def approve_ai_content(self, request):
        """Approve AI generated content"""
        ai_note_id = request.data.get('ai_note_id')
        note_id = request.data.get('note_id')
        
        try:
            ai_note = AIGeneratedNote.objects.get(id=ai_note_id, user=request.user)
            ai_note.approved = True
            ai_note.approved_at = timezone.now()
            ai_note.save()
            
            # Optionally update the note
            if note_id:
                note = Note.objects.get(id=note_id, user=request.user)
                note.content = ai_note.generated_content
                note.save()
            
            return Response({'status': 'approved'})
        except (AIGeneratedNote.DoesNotExist, Note.DoesNotExist):
            return Response(
                {'error': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def import_youtube(self, request):
        """Import YouTube video and generate notes"""
        serializer = YouTubeImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        video_url = serializer.validated_data['video_url']
        generate_notes = serializer.validated_data['generate_notes']
        note_title = serializer.validated_data.get('note_title')
        
        # Fetch transcript
        video_data = fetch_youtube_transcript(video_url)
        
        # Save transcript
        yt_transcript = YouTubeTranscript.objects.create(
            user=request.user,
            video_url=video_url,
            video_id=video_data['video_id'],
            video_title=video_data['title'],
            transcript=video_data['transcript'],
            timestamps=video_data['timestamps']
        )
        
        response_data = {
            'transcript_id': yt_transcript.id,
            'video_title': video_data['title']
        }
        
        # Generate notes if requested
        if generate_notes:
            notes_content = generate_notes_from_transcript(video_data['transcript'])
            
            note = Note.objects.create(
                user=request.user,
                title=note_title or f"Notes: {video_data['title']}",
                content=notes_content,
                status='draft'
            )
            
            # Create source reference
            source = NoteSource.objects.create(
                user=request.user,
                source_type='youtube',
                title=video_data['title'],
                url=video_url,
                reference_number=NoteSource.objects.filter(user=request.user).count() + 1
            )
            note.sources.add(source)
            
            yt_transcript.processed = True
            yt_transcript.notes_generated = note
            yt_transcript.save()
            
            response_data['note_id'] = note.id
            response_data['note_title'] = note.title
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def export_pdf(self, request, pk=None):
        """Export note to PDF"""
        note = self.get_object()
        serializer = ExportNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        include_sources = serializer.validated_data.get('include_sources', True)
        include_code = serializer.validated_data.get('include_code', True)
        
        # Generate PDF
        pdf_file = export_note_to_pdf(
            note,
            include_sources=include_sources,
            include_code=include_code
        )
        
        return Response({
            'pdf_url': pdf_file.url if pdf_file else None,
            'message': 'PDF generated successfully'
        })
    
    @action(detail=False, methods=['get'])
    def daily_notes(self, request):
        """Get notes for a specific day"""
        target_date = request.query_params.get('date', date.today())
        notes = Note.objects.filter(
            user=request.user,
            session_date=target_date
        )
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)


class CodeSnippetViewSet(viewsets.ModelViewSet):
    """Code snippet management"""
    
    serializer_class = CodeSnippetSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = CodeSnippet.objects.filter(user=self.request.user)
        
        # Filter by language
        language = self.request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        # Filter by note
        note_id = self.request.query_params.get('note')
        if note_id:
            queryset = queryset.filter(note_id=note_id)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(code__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteSourceViewSet(viewsets.ModelViewSet):
    """Manage note sources and references"""
    
    serializer_class = NoteSourceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NoteSource.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def auto_fetch(self, request):
        """Automatically fetch source metadata from URL"""
        url = request.data.get('url')
        source_type = request.data.get('source_type', 'url')
        
        # TODO: Implement metadata fetching
        # Use libraries like newspaper3k, BeautifulSoup, etc.
        
        return Response({
            'title': 'Fetched Title',
            'author': 'Fetched Author',
            'date': date.today()
        })


class NoteTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """Note templates for quick creation"""
    
    serializer_class = NoteTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NoteTemplate.objects.filter(
            Q(is_system=True) | Q(user=self.request.user)
        )
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Create a note from template"""
        template = self.get_object()
        title = request.data.get('title', 'New Note')
        
        note = Note.objects.create(
            user=request.user,
            title=title,
            content_json=template.template_content,
            status='draft'
        )
        
        serializer = NoteDetailSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DailyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """Daily learning reports"""
    
    serializer_class = DailyNoteReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DailyNoteReport.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def generate_today(self, request):
        """Manually generate today's report"""
        today = date.today()
        
        # Get today's notes
        notes_created = Note.objects.filter(
            user=request.user,
            created_at__date=today
        ).count()
        
        notes_updated = Note.objects.filter(
            user=request.user,
            updated_at__date=today
        ).exclude(created_at__date=today).count()
        
        # Get topics covered
        topics = Note.objects.filter(
            user=request.user,
            session_date=today
        ).values_list('topic__title', flat=True).distinct()
        
        # Generate AI summary
        ai_summary = "Your daily learning summary..."  # TODO: Implement
        
        # Create or update report
        report, created = DailyNoteReport.objects.update_or_create(
            user=request.user,
            report_date=today,
            defaults={
                'notes_created': notes_created,
                'notes_updated': notes_updated,
                'topics_covered': list(topics),
                'ai_summary': ai_summary
            }
        )
        
        # Generate PDF
        pdf_file = generate_daily_report_pdf(report)
        report.pdf_file = pdf_file
        report.save()
        
        serializer = self.get_serializer(report)
        return Response(serializer.data)


class NoteShareViewSet(viewsets.ModelViewSet):
    """Share notes with others"""
    
    serializer_class = NoteShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return NoteShare.objects.filter(
            Q(shared_by=self.request.user) | Q(shared_with=self.request.user)
        )
    
    @action(detail=False, methods=['post'])
    def create_public_share(self, request):
        """Create a public shareable link"""
        note_id = request.data.get('note_id')
        
        try:
            note = Note.objects.get(id=note_id, user=request.user)
            
            share = NoteShare.objects.create(
                note=note,
                shared_by=request.user,
                is_public=True,
                permission='view'
            )
            
            serializer = self.get_serializer(share)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Note.DoesNotExist:
            return Response(
                {'error': 'Note not found'},
                status=status.HTTP_404_NOT_FOUND
            )