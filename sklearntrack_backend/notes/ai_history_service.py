# FILE: notes/ai_history_service.py - COMPLETE FIXED VERSION
# ============================================================================

import os
from io import BytesIO
from datetime import date, timedelta
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re
from html import unescape
import logging

from .models import AIHistory

logger = logging.getLogger(__name__)


class AIHistoryService:
    """Service for AI History management"""
    
    # Folder mapping for Google Drive
    DRIVE_FOLDERS = {
        'generate_explanation': 'AI-Explain-Topic',
        'improve_explanation': 'AI-Improve',
        'summarize_explanation': 'AI-Summarize',
        'generate_code': 'AI-Generated-Code',
    }
    
    # File extensions for code
    CODE_EXTENSIONS = {
        'python': 'py',
        'javascript': 'js',
        'typescript': 'ts',
        'java': 'java',
        'cpp': 'cpp',
        'c': 'c',
        'go': 'go',
        'rust': 'rs',
        'php': 'php',
        'ruby': 'rb',
        'swift': 'swift',
        'kotlin': 'kt',
        'csharp': 'cs',
        'sql': 'sql',
        'html': 'html',
        'css': 'css',
        'bash': 'sh',
    }
    
    @staticmethod
    def create_history(user, action_type, prompt, generated_content, language=None, title=None):
        """Create AI history record"""
        if not title:
            # Auto-generate title from prompt
            title = prompt[:50] + "..." if len(prompt) > 50 else prompt
        
        history = AIHistory.objects.create(
            user=user,
            action_type=action_type,
            prompt=prompt,
            generated_content=generated_content,
            language=language,
            title=title,
            status='temporary'
        )
        
        logger.info(f"Created AI history {history.id} for user {user.id}: {action_type}")
        return history
    
    @staticmethod
    def get_user_history(user, action_type=None, status=None):
        """Get user's AI history with filters"""
        queryset = AIHistory.objects.filter(user=user)
        
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def update_history(history, **data):
        """Update AI history record"""
        for key, value in data.items():
            setattr(history, key, value)
        history.save()
        logger.info(f"Updated AI history {history.id}")
        return history
    
    @staticmethod
    def delete_history(history):
        """Delete AI history record"""
        history_id = history.id
        user_id = history.user.id
        
        # Delete PDF if exists
        if history.pdf_path and os.path.exists(history.pdf_path):
            try:
                os.remove(history.pdf_path)
            except Exception as e:
                logger.warning(f"Failed to delete PDF file: {e}")
        
        history.delete()
        logger.info(f"Deleted AI history {history_id} for user {user_id}")
    
    @staticmethod
    def delete_temporary_old_records(days=7):
        """Delete temporary records older than specified days"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_records = AIHistory.objects.filter(
            status='temporary',
            created_at__lt=cutoff_date
        )
        count = old_records.count()
        old_records.delete()
        logger.info(f"Cleaned up {count} old temporary AI history records")
        return count
    
    @staticmethod
    def export_to_pdf(history):
        """Export AI history to PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=60,
            leftMargin=60,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a202c'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#4a5568'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16,
            spaceAfter=12
        )
        
        code_style = ParagraphStyle(
            'CodeStyle',
            parent=styles['Code'],
            fontSize=9,
            leading=13,
            leftIndent=15,
            rightIndent=15,
            backColor=colors.HexColor('#f7fafc'),
            borderColor=colors.HexColor('#cbd5e0'),
            borderWidth=1,
            borderPadding=12,
            fontName='Courier'
        )
        
        # Title
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph(history.title, title_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Metadata
        metadata = f"""
        <para alignment="center">
        <b>Type:</b> {history.get_action_type_display()}<br/>
        <b>Generated:</b> {history.created_at.strftime('%B %d, %Y at %I:%M %p')}<br/>
        {f'<b>Language:</b> {history.language.upper()}<br/>' if history.language else ''}
        </para>
        """
        story.append(Paragraph(metadata, subtitle_style))
        story.append(Spacer(1, 0.4*inch))
        
        # Prompt section
        story.append(Paragraph("<b>Prompt:</b>", body_style))
        story.append(Spacer(1, 0.1*inch))
        prompt_text = AIHistoryService._format_html_content(history.prompt)
        story.append(Paragraph(prompt_text, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Generated content section
        story.append(Paragraph("<b>Generated Content:</b>", body_style))
        story.append(Spacer(1, 0.1*inch))
        
        if history.action_type == 'generate_code':
            # Code block
            code_block = Preformatted(
                history.generated_content,
                code_style,
                maxLineLength=85
            )
            story.append(code_block)
        else:
            # Regular content
            content_text = AIHistoryService._format_html_content(history.generated_content)
            story.append(Paragraph(content_text, body_style))
        
        # Build PDF
        doc.build(story)
        
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Save PDF
        filename = f"ai_{history.action_type}_{history.id}_{date.today()}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'ai_history', filename)
        os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
        
        with open(pdf_path, 'wb') as f:
            f.write(pdf_content)
        
        # Update history
        history.pdf_generated = True
        history.pdf_path = pdf_path
        history.save()
        
        logger.info(f"Generated PDF for AI history {history.id}")
        return ContentFile(pdf_content, name=filename)
    
    @staticmethod
    def _format_html_content(html_text):
        """Convert HTML to PDF-friendly format"""
        if not html_text:
            return ""
        
        text = html_text
        
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert headers
        text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'<b><font size="14">\1</font></b><br/>', text, flags=re.IGNORECASE)
        text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'<b><font size="12">\1</font></b><br/>', text, flags=re.IGNORECASE)
        text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'<b><font size="11">\1</font></b><br/>', text, flags=re.IGNORECASE)
        
        # Convert lists
        text = re.sub(r'<ul[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</ul>', '<br/>', text, flags=re.IGNORECASE)
        text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
        text = re.sub(r'</li>', '<br/>', text, flags=re.IGNORECASE)
        
        # Convert paragraphs
        text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
        text = re.sub(r'</p>', '<br/>', text, flags=re.IGNORECASE)
        text = re.sub(r'<br\s*/?>', '<br/>', text, flags=re.IGNORECASE)
        
        # Convert code
        text = re.sub(r'<code[^>]*>(.*?)</code>', r'<font face="Courier"><b>\1</b></font>', text, flags=re.IGNORECASE)
        
        # Remove remaining HTML
        text = re.sub(r'<[^>]+>', '', text)
        
        # Unescape entities
        text = unescape(text)
        
        # Clean up
        text = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', text)
        
        return text.strip()
    
    @staticmethod
    def get_drive_folder_name(action_type):
        """Get Google Drive folder name for action type"""
        return AIHistoryService.DRIVE_FOLDERS.get(action_type, 'AI-Output')
    
    @staticmethod
    def generate_filename(history):
        """Generate appropriate filename for export"""
        timestamp = history.created_at.strftime('%Y%m%d_%H%M%S')
        safe_title = re.sub(r'[^\w\s-]', '', history.title).strip().replace(' ', '_')[:50]
        
        if history.action_type == 'generate_code' and history.language:
            # Code files with proper extension
            ext = AIHistoryService.CODE_EXTENSIONS.get(history.language.lower(), 'txt')
            return f"{safe_title}_{timestamp}.{ext}"
        else:
            # PDF for text content
            return f"{safe_title}_{timestamp}.pdf"
    
    @staticmethod
    def prepare_drive_content(history):
        """Prepare content for Google Drive upload"""
        filename = AIHistoryService.generate_filename(history)
        
        if history.action_type == 'generate_code':
            # Return code as-is
            content = ContentFile(
                history.generated_content.encode('utf-8'),
                name=filename
            )
            mime_type = 'text/plain'
        else:
            # Generate PDF
            content = AIHistoryService.export_to_pdf(history)
            mime_type = 'application/pdf'
        
        return content, filename, mime_type