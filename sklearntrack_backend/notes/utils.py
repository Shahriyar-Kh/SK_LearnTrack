# FILE: notes/utils.py
# ============================================================================

import re
import json
from datetime import date
from io import BytesIO
from typing import Dict, List, Optional
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors


# ============================================================================
# AI Integration Functions
# ============================================================================

def generate_ai_summary(content: str, length: str = 'medium') -> str:
    """
    Generate AI summary of content
    
    Args:
        content: The content to summarize
        length: 'short', 'medium', or 'detailed'
    
    Returns:
        str: Summarized content
    """
    # TODO: Integrate with OpenAI API or other AI service
    # This is a placeholder implementation
    
    prompt_templates = {
        'short': f"Summarize the following in 2-3 sentences:\n\n{content}",
        'medium': f"Provide a medium-length summary (1 paragraph) of:\n\n{content}",
        'detailed': f"Provide a detailed summary with key points of:\n\n{content}"
    }
    
    prompt = prompt_templates.get(length, prompt_templates['medium'])
    
    # Placeholder - replace with actual AI API call
    return f"[AI Summary - {length}]\n\n{content[:500]}..."


def generate_ai_expansion(content: str) -> str:
    """
    Expand content with more details using AI
    
    Args:
        content: The content to expand
    
    Returns:
        str: Expanded content
    """
    # TODO: Integrate with AI API
    prompt = f"Expand the following content with more details and examples:\n\n{content}"
    
    # Placeholder
    return f"[AI Expanded Content]\n\n{content}\n\n[Additional AI-generated details would appear here]"


def generate_ai_rewrite(content: str, mode: str = 'clarity') -> str:
    """
    Rewrite content for clarity or break down topics
    
    Args:
        content: The content to rewrite
        mode: 'clarity' or 'breakdown'
    
    Returns:
        str: Rewritten content
    """
    # TODO: Integrate with AI API
    if mode == 'clarity':
        prompt = f"Rewrite the following for better clarity:\n\n{content}"
    else:  # breakdown
        prompt = f"Break down the following into structured topics:\n\n{content}"
    
    # Placeholder
    return f"[AI Rewritten - {mode}]\n\n{content}"


# ============================================================================
# YouTube Integration Functions
# ============================================================================

def fetch_youtube_transcript(video_url: str) -> Dict:
    """
    Fetch transcript from YouTube video
    
    Args:
        video_url: YouTube video URL
    
    Returns:
        Dict with video_id, title, transcript, and timestamps
    """
    # TODO: Implement using youtube-transcript-api library
    # pip install youtube-transcript-api
    
    # from youtube_transcript_api import YouTubeTranscriptApi
    # import re
    
    # Extract video ID
    video_id_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', video_url)
    if not video_id_match:
        raise ValueError("Invalid YouTube URL")
    
    video_id = video_id_match.group(1)
    
    # Placeholder implementation
    return {
        'video_id': video_id,
        'title': 'Sample Video Title',
        'transcript': 'This is a sample transcript. In a real implementation, this would contain the actual video transcript.',
        'timestamps': [
            {'time': '0:00', 'text': 'Introduction'},
            {'time': '1:30', 'text': 'Main content'},
            {'time': '5:00', 'text': 'Conclusion'}
        ]
    }


def generate_notes_from_transcript(transcript: str) -> str:
    """
    Generate structured notes from transcript using AI
    
    Args:
        transcript: Video transcript text
    
    Returns:
        str: Structured notes
    """
    # TODO: Use AI to generate structured notes
    prompt = f"Convert the following transcript into structured study notes with headings:\n\n{transcript}"
    
    # Placeholder
    return f"# Notes from Transcript\n\n## Key Points\n\n{transcript[:500]}..."


# ============================================================================
# PDF Export Functions
# ============================================================================

def export_note_to_pdf(note, include_sources=True, include_code=True) -> Optional[ContentFile]:
    """
    Export a note to PDF format with IEEE citations
    
    Args:
        note: Note model instance
        include_sources: Include references section
        include_code: Include code snippets
    
    Returns:
        ContentFile: PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph(note.title, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Metadata
    metadata_text = f"Created: {note.created_at.strftime('%Y-%m-%d')} | Updated: {note.updated_at.strftime('%Y-%m-%d')}"
    story.append(Paragraph(metadata_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Content
    content_paragraphs = note.content.split('\n')
    for para in content_paragraphs:
        if para.strip():
            # Check if it's a heading
            if para.startswith('#'):
                story.append(Paragraph(para.replace('#', '').strip(), heading_style))
            else:
                story.append(Paragraph(para, styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    
    # Code snippets
    if include_code and note.code_snippets.exists():
        story.append(PageBreak())
        story.append(Paragraph("Code Snippets", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        for snippet in note.code_snippets.all():
            story.append(Paragraph(f"<b>{snippet.title}</b> ({snippet.language})", styles['Normal']))
            code_text = f"<pre>{snippet.code}</pre>"
            story.append(Paragraph(code_text, styles['Code']))
            story.append(Spacer(1, 0.2*inch))
    
    # References (IEEE Style)
    if include_sources and note.sources.exists():
        story.append(PageBreak())
        story.append(Paragraph("References", heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        for source in note.sources.all():
            ref_text = format_ieee_reference(source)
            story.append(Paragraph(f"[{source.reference_number}] {ref_text}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
    
    # Build PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"note_{note.slug}_{date.today()}.pdf"
    return ContentFile(pdf_content, name=filename)


def format_ieee_reference(source) -> str:
    """
    Format a source in IEEE citation style
    
    Args:
        source: NoteSource instance
    
    Returns:
        str: Formatted IEEE reference
    """
    parts = []
    
    if source.author:
        parts.append(source.author)
    
    parts.append(f'"{source.title},"')
    
    if source.source_type == 'youtube':
        parts.append('[Video].')
    elif source.source_type == 'url':
        parts.append('[Online].')
    
    if source.url:
        parts.append(f'Available: {source.url}')
    
    if source.date:
        parts.append(f'[Accessed: {source.date.strftime("%d-%b-%Y")}]')
    
    return ' '.join(parts)


def generate_daily_report_pdf(report) -> Optional[ContentFile]:
    """
    Generate PDF for daily learning report
    
    Args:
        report: DailyNoteReport instance
    
    Returns:
        ContentFile: PDF file
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title = f"Daily Learning Report - {report.report_date.strftime('%B %d, %Y')}"
    story.append(Paragraph(title, styles['Title']))
    story.append(Spacer(1, 0.3*inch))
    
    # Statistics
    stats_data = [
        ['Metric', 'Count'],
        ['Notes Created', str(report.notes_created)],
        ['Notes Updated', str(report.notes_updated)],
        ['Time Spent', f"{report.time_spent_minutes} minutes"]
    ]
    
    stats_table = Table(stats_data)
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(stats_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Topics covered
    if report.topics_covered:
        story.append(Paragraph("Topics Covered:", styles['Heading2']))
        for topic in report.topics_covered:
            story.append(Paragraph(f"• {topic}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # AI Summary
    if report.ai_summary:
        story.append(Paragraph("Daily Summary:", styles['Heading2']))
        story.append(Paragraph(report.ai_summary, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"daily_report_{report.report_date}.pdf"
    return ContentFile(pdf_content, name=filename)


# ============================================================================
# Content Processing Functions
# ============================================================================

def generate_table_of_contents(content: str) -> List[Dict]:
    """
    Generate table of contents from note content
    
    Args:
        content: Note content (HTML or Markdown)
    
    Returns:
        List of TOC items with title and level
    """
    toc = []
    
    # Extract headings (Markdown style)
    heading_pattern = r'^(#{1,6})\s+(.+)$'
    lines = content.split('\n')
    
    for line in lines:
        match = re.match(heading_pattern, line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            toc.append({
                'level': level,
                'title': title,
                'slug': slugify_heading(title)
            })
    
    return toc


def slugify_heading(heading: str) -> str:
    """Convert heading to URL-friendly slug"""
    return re.sub(r'[^\w\s-]', '', heading.lower()).replace(' ', '-')


def sanitize_html_content(html: str) -> str:
    """
    Sanitize HTML content for safe storage
    
    Args:
        html: Raw HTML content
    
    Returns:
        str: Sanitized HTML
    """
    # TODO: Implement using bleach or similar library
    # pip install bleach
    
    # Placeholder - just return as is for now
    return html


def extract_code_blocks(content: str) -> List[Dict]:
    """
    Extract code blocks from markdown content
    
    Args:
        content: Note content
    
    Returns:
        List of code blocks with language and code
    """
    code_blocks = []
    
    # Pattern for fenced code blocks
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.finditer(pattern, content, re.DOTALL)
    
    for match in matches:
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        code_blocks.append({
            'language': language,
            'code': code
        })
    
    return code_blocks