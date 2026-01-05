# FILE: notes/pdf_service.py - PDF Export Service
# ============================================================================

from io import BytesIO
from datetime import date
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Preformatted
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import re
from html import unescape
import logging
import html
from html.parser import HTMLParser

logger = logging.getLogger(__name__)


class HTMLStripper(HTMLParser):
    """Custom HTML parser that preserves formatting tags"""
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []
        self.tags = []
    
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        if tag == 'h1':
            self.text.append('\n\n## ')
        elif tag == 'h2':
            self.text.append('\n\n### ')
        elif tag == 'h3':
            self.text.append('\n\n#### ')
        elif tag == 'p':
            self.text.append('\n\n')
        elif tag == 'br':
            self.text.append('\n')
        elif tag == 'li':
            self.text.append('\n• ')
        elif tag == 'strong' or tag == 'b':
            self.text.append('**')
        elif tag == 'em' or tag == 'i':
            self.text.append('*')
        elif tag == 'code':
            self.text.append('`')
        elif tag == 'pre':
            self.text.append('\n```\n')
        elif tag == 'ul' or tag == 'ol':
            self.text.append('\n')
        elif tag == 'blockquote':
            self.text.append('\n> ')
    
    def handle_endtag(self, tag):
        if self.tags and self.tags[-1] == tag:
            self.tags.pop()
        
        if tag == 'strong' or tag == 'b':
            self.text.append('**')
        elif tag == 'em' or tag == 'i':
            self.text.append('*')
        elif tag == 'code':
            self.text.append('`')
        elif tag == 'pre':
            self.text.append('\n```\n')
        elif tag == 'p':
            self.text.append('\n')
        elif tag == 'h1' or tag == 'h2' or tag == 'h3':
            self.text.append('\n')
        elif tag == 'li':
            self.text.append('')
        elif tag == 'blockquote':
            self.text.append('\n')
    
    def handle_data(self, data):
        self.text.append(data)
    
    def get_text(self):
        return ''.join(self.text)


class PDFExportService:
    """Service for exporting notes to professional PDFs"""
    
    def __init__(self, note):
        self.note = note
        self.styles = self._setup_styles()

    
    def _setup_styles(self):
        """Setup PDF styles"""
        base_styles = getSampleStyleSheet()
        
        return {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Heading1'],
                fontSize=32,
                textColor=colors.HexColor('#1a202c'),
                spaceAfter=40,
                alignment=TA_CENTER,
                bold=True,
                fontName='Helvetica-Bold'
            ),
            'subtitle': ParagraphStyle(
                'Subtitle',
                parent=base_styles['Normal'],
                fontSize=14,
                textColor=colors.HexColor('#4a5568'),
                spaceAfter=20,
                alignment=TA_CENTER,
                fontName='Helvetica'
            ),
            'toc_title': ParagraphStyle(
                'TOCTitle',
                parent=base_styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a202c'),
                spaceAfter=30,
                spaceBefore=20,
                alignment=TA_CENTER,
                bold=True,
                fontName='Helvetica-Bold'
            ),
            'chapter': ParagraphStyle(
                'ChapterHeading',
                parent=base_styles['Heading1'],
                fontSize=22,
                textColor=colors.HexColor('#2563eb'),
                spaceAfter=15,
                spaceBefore=40,
                bold=True,
                fontName='Helvetica-Bold',
                keepWithNext=1
            ),
            'topic': ParagraphStyle(
                'TopicHeading',
                parent=base_styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#1e40af'),
                spaceAfter=10,
                spaceBefore=25,
                bold=True,
                fontName='Helvetica-Bold'
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                spaceAfter=12,
                fontName='Helvetica'
            ),
            'code_header': ParagraphStyle(
                'CodeHeader',
                parent=base_styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#2d3748'),
                spaceAfter=5,
                bold=True,
                fontName='Helvetica-Bold'
            ),
            'code': ParagraphStyle(
                'CodeStyle',
                parent=base_styles['Code'],
                fontSize=9,
                leading=13,
                leftIndent=15,
                rightIndent=15,
                backColor=colors.HexColor('#f7fafc'),
                borderColor=colors.HexColor('#cbd5e0'),
                borderWidth=1,
                borderPadding=12,
                fontName='Courier'
            ),
            'reference': ParagraphStyle(
                'Reference',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=8,
                leftIndent=20,
                fontName='Helvetica'
            ),
        }
    
    def export(self):
        """Export note to PDF"""
        try:
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
            
            # Build PDF content
            self._add_title_page(story)
            story.append(PageBreak())
            
            self._add_table_of_contents(story)
            story.append(PageBreak())
            
            sources = self._add_chapters_and_topics(story)
            
            if sources:
                story.append(PageBreak())
                self._add_references(story, sources)
            
            # Build PDF
            doc.build(story)
            
            pdf_content = buffer.getvalue()
            buffer.close()
            
            filename = f"note_{self.note.slug}_{date.today()}.pdf"
            return ContentFile(pdf_content, name=filename)
            
        except Exception as e:
            logger.error(f"PDF export error for note {self.note.id}: {e}")
            raise
    
    def _add_title_page(self, story):
        """Add title page"""
        story.append(Spacer(1, 2.5*inch))
        story.append(Paragraph(self.note.title, self.styles['title']))
        story.append(Spacer(1, 0.6*inch))
        
        metadata_text = f"""
        <para alignment="center" fontSize="12">
        <b>Study Notes Document</b><br/><br/>
        Created: {self.note.created_at.strftime('%B %d, %Y')}<br/>
        Last Updated: {self.note.updated_at.strftime('%B %d, %Y')}<br/>
        Status: {self.note.get_status_display()}
        </para>
        """
        story.append(Paragraph(metadata_text, self.styles['subtitle']))
        
        if self.note.tags:
            tags_text = f"<para alignment='center' fontSize='11'><b>Tags:</b> {', '.join(self.note.tags)}</para>"
            story.append(Spacer(1, 0.4*inch))
            story.append(Paragraph(tags_text, self.styles['subtitle']))
    
    def _add_table_of_contents(self, story):
        """Add table of contents"""
        story.append(Paragraph("Table of Contents", self.styles['toc_title']))
        story.append(Spacer(1, 0.3*inch))
        
        toc_data = []
        chapter_num = 1
        
        for chapter in self.note.chapters.all().order_by('order'):
            toc_data.append([
                Paragraph(
                    f"<b>Chapter {chapter_num}: {chapter.title}</b>",
                    ParagraphStyle(
                        'TOCChapter', 
                        parent=self.styles['body'],
                        fontSize=12, 
                        textColor=colors.HexColor('#2563eb'),
                        fontName='Helvetica-Bold'
                    )
                ),
                ""
            ])
            
            topic_num = 1
            for topic in chapter.topics.all().order_by('order'):
                toc_data.append([
                    Paragraph(
                        f"&nbsp;&nbsp;&nbsp;&nbsp;{chapter_num}.{topic_num} {topic.name}",
                        ParagraphStyle(
                            'TOCTopic', 
                            parent=self.styles['body'],
                            fontSize=10, 
                            textColor=colors.black,
                            leftIndent=20,
                            fontName='Helvetica'
                        )
                    ),
                    ""
                ])
                topic_num += 1
            
            chapter_num += 1
        
        if toc_data:
            toc_table = Table(toc_data, colWidths=[5.5*inch, 0.5*inch])
            toc_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (0, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ]))
            story.append(toc_table)
    
    def _add_chapters_and_topics(self, story):
        """Add chapters and topics content"""
        all_sources = {}
        source_counter = 1
        
        chapter_num = 1
        for chapter in self.note.chapters.all().order_by('order'):
            chapter_title = f"Chapter {chapter_num}: {chapter.title}"
            story.append(Paragraph(chapter_title, self.styles['chapter']))
            story.append(Spacer(1, 0.2*inch))
            
            topic_num = 1
            for topic in chapter.topics.all().order_by('order'):
                # Topic Number and Name
                topic_title = f"{chapter_num}.{topic_num} {topic.name}"
                story.append(Paragraph(topic_title, self.styles['topic']))
                story.append(Spacer(1, 0.15*inch))
                
                # Explanation Content - PRESERVE EXACT FORMATTING
                if topic.explanation:
                    explanation_text = topic.explanation.content
                    
                    # Clean HTML but preserve structure
                    explanation_text = format_text_for_pdf(explanation_text)
                    
                    # Add source citation if exists
                    if topic.source:
                        source_key = topic.source.url
                        if source_key not in all_sources:
                            all_sources[source_key] = {
                                'number': source_counter,
                                'title': topic.source.title,
                                'url': topic.source.url
                            }
                            source_counter += 1
                        
                        citation_num = all_sources[source_key]['number']
                        explanation_text += f" <super>[{citation_num}]</super>"
                    
                    # Split by <br/> to handle paragraphs properly
                    paragraphs = explanation_text.split('<br/>')
                    for para in paragraphs:
                        if para.strip():  # Only add non-empty paragraphs
                            story.append(Paragraph(para.strip(), self.styles['body']))
                            story.append(Spacer(1, 0.05*inch))
                    
                    story.append(Spacer(1, 0.2*inch))
                
                # Code Snippet
                if topic.code_snippet:
                    story.append(Spacer(1, 0.1*inch))
                    story.append(Paragraph(
                        f"<b>Code Example ({topic.code_snippet.language.upper()}):</b>",
                        self.styles['code_header']
                    ))
                    story.append(Spacer(1, 0.08*inch))
                    
                    # Clean the code - remove any HTML that might be there
                    clean_code = re.sub(r'<[^>]+>', '', topic.code_snippet.code)
                    clean_code = unescape(clean_code)
                    
                    code_block = Preformatted(
                        clean_code,
                        self.styles['code'],
                        maxLineLength=85
                    )
                    story.append(code_block)
                    story.append(Spacer(1, 0.25*inch))
                
                topic_num += 1
            
            chapter_num += 1
            story.append(Spacer(1, 0.3*inch))
        
        return all_sources
        
    def _add_references(self, story, sources):
        """Add references section"""
        story.append(Paragraph("References", self.styles['chapter']))
        story.append(Spacer(1, 0.25*inch))
        
        sorted_sources = sorted(sources.values(), key=lambda x: x['number'])
        
        for source in sorted_sources:
            ref_text = f"<b>[{source['number']}]</b> {source['title']}"
            story.append(Paragraph(ref_text, self.styles['reference']))
            
            url_text = f"<font color='#2563eb'><link href='{source['url']}'>{source['url']}</link></font>"
            story.append(Paragraph(url_text, self.styles['reference']))
            story.append(Spacer(1, 0.12*inch))


def format_text_for_pdf(text):
    """Format HTML/rich text content for PDF - PRESERVE EXACT FORMATTING"""
    if not text:
        return ""
    
    try:
        # First, preserve basic HTML structure but clean it up
        # Keep only the tags we want to support
        allowed_tags = {
            'h1': '## ',
            'h2': '### ',
            'h3': '#### ',
            'h4': '##### ',
            'strong': '**',
            'b': '**',
            'em': '*',
            'i': '*',
            'u': '_',
            'code': '`',
            'pre': '```\n',
            'br': '\n',
            'p': '\n\n',
            'li': '* ',
            'blockquote': '> ',
            'hr': '\n---\n'
        }
        
        # Convert HTML to markdown-like text with proper spacing
        result = text
        
        # Remove script and style tags completely
        result = re.sub(r'<script[^>]*>.*?</script>', '', result, flags=re.DOTALL | re.IGNORECASE)
        result = re.sub(r'<style[^>]*>.*?</style>', '', result, flags=re.DOTALL | re.IGNORECASE)
        
        # Convert headings (handle both HTML and markdown)
        result = re.sub(r'<h1[^>]*>(.*?)</h1>', r'\n## \1\n', result, flags=re.IGNORECASE)
        result = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n### \1\n', result, flags=re.IGNORECASE)
        result = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n#### \1\n', result, flags=re.IGNORECASE)
        
        # Convert bold/strong
        result = re.sub(r'<strong[^>]*>(.*?)</strong>', r'**\1**', result, flags=re.IGNORECASE)
        result = re.sub(r'<b[^>]*>(.*?)</b>', r'**\1**', result, flags=re.IGNORECASE)
        
        # Convert italic/emphasis
        result = re.sub(r'<em[^>]*>(.*?)</em>', r'*\1*', result, flags=re.IGNORECASE)
        result = re.sub(r'<i[^>]*>(.*?)</i>', r'*\1*', result, flags=re.IGNORECASE)
        
        # Convert inline code
        result = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', result, flags=re.IGNORECASE)
        
        # Convert paragraphs - handle with care
        result = re.sub(r'<p[^>]*>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</p>', '\n\n', result, flags=re.IGNORECASE)
        
        # Convert line breaks
        result = re.sub(r'<br\s*/?>', '\n', result, flags=re.IGNORECASE)
        
        # Convert lists
        result = re.sub(r'<ul[^>]*>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</ul>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'<ol[^>]*>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</ol>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'<li[^>]*>', '* ', result, flags=re.IGNORECASE)
        result = re.sub(r'</li>', '\n', result, flags=re.IGNORECASE)
        
        # Convert blockquotes
        result = re.sub(r'<blockquote[^>]*>', '\n> ', result, flags=re.IGNORECASE)
        result = re.sub(r'</blockquote>', '\n\n', result, flags=re.IGNORECASE)
        
        # Convert pre/code blocks - preserve exactly
        def replace_code_block(match):
            code = match.group(1)
            # Clean any remaining HTML tags inside code
            code = re.sub(r'<[^>]+>', '', code)
            return f'\n```\n{code}\n```\n'
        
        result = re.sub(r'<pre[^>]*>(.*?)</pre>', replace_code_block, result, flags=re.DOTALL | re.IGNORECASE)
        
        # Remove all other HTML tags
        result = re.sub(r'<[^>]+>', '', result)
        
        # Unescape HTML entities
        result = unescape(result)
        
        # Clean up markdown formatting to make it PDF-friendly
        # Convert markdown to simple HTML for PDF
        lines = result.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Handle headings
            if line.startswith('## '):
                formatted_lines.append(f'<b><font size="14">{line[3:]}</font></b><br/>')
            elif line.startswith('### '):
                formatted_lines.append(f'<b><font size="12">{line[4:]}</font></b><br/>')
            elif line.startswith('#### '):
                formatted_lines.append(f'<b>{line[5:]}</b><br/>')
            # Handle bold
            elif '**' in line:
                line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                formatted_lines.append(f'{line}<br/>')
            # Handle italic
            elif '*' in line and not line.startswith('* '):  # Not a list item
                line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
                formatted_lines.append(f'{line}<br/>')
            # Handle inline code
            elif '`' in line:
                line = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', line)
                formatted_lines.append(f'{line}<br/>')
            # Handle code blocks
            elif line.startswith('```'):
                continue  # Skip the ``` markers
            # Handle list items
            elif line.startswith('* '):
                formatted_lines.append(f'• {line[2:]}<br/>')
            # Handle blockquotes
            elif line.startswith('> '):
                formatted_lines.append(f'<i>{line[2:]}</i><br/>')
            # Handle horizontal rule
            elif line.strip() == '---':
                formatted_lines.append('<br/>' + '-' * 50 + '<br/>')
            # Handle empty lines
            elif line.strip() == '':
                formatted_lines.append('<br/>')
            # Regular text
            else:
                formatted_lines.append(f'{line}<br/>')
        
        result = ''.join(formatted_lines)
        
        # Clean up excessive line breaks
        result = re.sub(r'(<br/>){4,}', '<br/><br/>', result)
        
        # Remove leading/trailing breaks
        result = re.sub(r'^(<br/>)+', '', result)
        result = re.sub(r'(<br/>)+$', '', result)
        
        return result
        
    except Exception as e:
        logger.error(f"Error formatting text for PDF: {e}")
        # Fallback: just strip HTML and preserve text
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = text.replace('\n', '<br/>')
        return text

def export_note_to_pdf(note):
    """Export note to PDF - convenience function for backward compatibility"""
    service = PDFExportService(note)
    return service.export()

# Add this function at the end of the file
def markdown_to_html(text):
    """Convert markdown to HTML for PDF export"""
    if not text:
        return ""
    
    import markdown
    try:
        # Convert markdown to HTML
        html = markdown.markdown(text, extensions=['extra', 'codehilite'])
        return html
    except:
        # If markdown conversion fails, return the original text
        return text