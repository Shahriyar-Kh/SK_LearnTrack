# FILE: notes/utils.py - PDF Export Section
# ============================================================================

from io import BytesIO
from datetime import date
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Preformatted
)
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY


def export_note_to_pdf(note):
    """
    Export note to PDF with professional hierarchical structure
    
    Structure:
    - Title Page with Note name
    - Table of Contents (Chapters and Topics)
    - Chapters with Topics
    - Each Topic: Explanation (with citations), Code Examples
    - References section at end
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=60,
        leftMargin=60,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    story = []
    
    # Enhanced Custom Styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=32,
        textColor=colors.HexColor('#1a202c'),
        spaceAfter=40,
        alignment=TA_CENTER,
        bold=True,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    toc_title_style = ParagraphStyle(
        'TOCTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a202c'),
        spaceAfter=30,
        spaceBefore=20,
        alignment=TA_CENTER,
        bold=True,
        fontName='Helvetica-Bold'
    )
    
    chapter_style = ParagraphStyle(
        'ChapterHeading',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=15,
        spaceBefore=40,
        bold=True,
        fontName='Helvetica-Bold',
        keepWithNext=1
    )
    
    topic_style = ParagraphStyle(
        'TopicHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=10,
        spaceBefore=25,
        bold=True,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    code_header_style = ParagraphStyle(
        'CodeHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=5,
        bold=True,
        fontName='Helvetica-Bold'
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
    
    reference_style = ParagraphStyle(
        'Reference',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        spaceAfter=8,
        leftIndent=20,
        fontName='Helvetica'
    )
    
    # ========================================================================
    # TITLE PAGE
    # ========================================================================
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph(note.title, title_style))
    story.append(Spacer(1, 0.6*inch))
    
    metadata_text = f"""
    <para alignment="center" fontSize="12">
    <b>Study Notes Document</b><br/><br/>
    Created: {note.created_at.strftime('%B %d, %Y')}<br/>
    Last Updated: {note.updated_at.strftime('%B %d, %Y')}<br/>
    Status: {note.get_status_display()}
    </para>
    """
    story.append(Paragraph(metadata_text, subtitle_style))
    
    if note.tags:
        tags_text = f"<para alignment='center' fontSize='11'><b>Tags:</b> {', '.join(note.tags)}</para>"
        story.append(Spacer(1, 0.4*inch))
        story.append(Paragraph(tags_text, subtitle_style))
    
    story.append(PageBreak())
    
    # ========================================================================
    # TABLE OF CONTENTS
    # ========================================================================
    story.append(Paragraph("Table of Contents", toc_title_style))
    story.append(Spacer(1, 0.3*inch))
    
    toc_data = []
    chapter_num = 1
    
    for chapter in note.chapters.all().order_by('order'):
        # Chapter row with bold styling
        toc_data.append([
            Paragraph(f"<b>Chapter {chapter_num}: {chapter.title}</b>", 
                     ParagraphStyle('TOCChapter', parent=styles['Normal'], fontSize=12, 
                                   textColor=colors.HexColor('#2563eb'), fontName='Helvetica-Bold')),
            ""
        ])
        
        topic_num = 1
        for topic in chapter.topics.all().order_by('order'):
            toc_data.append([
                Paragraph(f"&nbsp;&nbsp;&nbsp;&nbsp;{chapter_num}.{topic_num} {topic.name}", 
                         ParagraphStyle('TOCTopic', parent=styles['Normal'], fontSize=10, 
                                       textColor=colors.black, leftIndent=20, fontName='Helvetica')),
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
    
    story.append(PageBreak())
    
    # ========================================================================
    # CHAPTERS AND TOPICS
    # ========================================================================
    
    # Collect all unique sources for references
    all_sources = {}
    source_counter = 1
    
    chapter_num = 1
    for chapter in note.chapters.all().order_by('order'):
        # Chapter heading
        chapter_title = f"Chapter {chapter_num}: {chapter.title}"
        story.append(Paragraph(chapter_title, chapter_style))
        story.append(Spacer(1, 0.2*inch))
        
        topic_num = 1
        for topic in chapter.topics.all().order_by('order'):
            # Topic heading
            topic_title = f"{chapter_num}.{topic_num} {topic.name}"
            story.append(Paragraph(topic_title, topic_style))
            story.append(Spacer(1, 0.1*inch))
            
            # Topic explanation
            if topic.explanation:
                explanation_text = topic.explanation.content
                
                # Add inline citation if source exists
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
                    explanation_text += f" [{citation_num}]"
                
                # Format explanation (handle markdown-like formatting)
                explanation_text = format_text_for_pdf(explanation_text)
                story.append(Paragraph(explanation_text, body_style))
                story.append(Spacer(1, 0.15*inch))
            
            # Code snippet
            if topic.code_snippet:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    f"<b>Example Code ({topic.code_snippet.language.upper()}):</b>",
                    code_header_style
                ))
                story.append(Spacer(1, 0.08*inch))
                
                # Use Preformatted for code to preserve formatting
                code_block = Preformatted(
                    topic.code_snippet.code,
                    code_style,
                    maxLineLength=85
                )
                story.append(code_block)
                story.append(Spacer(1, 0.2*inch))
            
            topic_num += 1
        
        chapter_num += 1
        story.append(Spacer(1, 0.3*inch))
    
    # ========================================================================
    # REFERENCES SECTION
    # ========================================================================
    if all_sources:
        story.append(PageBreak())
        story.append(Paragraph("References", chapter_style))
        story.append(Spacer(1, 0.25*inch))
        
        # Sort sources by number
        sorted_sources = sorted(all_sources.values(), key=lambda x: x['number'])
        
        for source in sorted_sources:
            ref_text = f"<b>[{source['number']}]</b> {source['title']}"
            story.append(Paragraph(ref_text, reference_style))
            
            url_text = f"<font color='#2563eb'><link href='{source['url']}'>{source['url']}</link></font>"
            story.append(Paragraph(url_text, reference_style))
            story.append(Spacer(1, 0.12*inch))
    
    # ========================================================================
    # BUILD PDF
    # ========================================================================
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"note_{note.slug}_{date.today()}.pdf"
    return ContentFile(pdf_content, name=filename)


def format_text_for_pdf(text):
    """
    Format HTML/rich text content for PDF
    Handles HTML tags from ReactQuill editor
    """
    import re
    from html import unescape
    
    if not text:
        return ""
    
    # Remove script and style tags for security
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert HTML headings to appropriate sizes
    text = re.sub(r'<h1[^>]*>(.*?)</h1>', r'<b><font size="14">\1</font></b>', text, flags=re.IGNORECASE)
    text = re.sub(r'<h2[^>]*>(.*?)</h2>', r'<b><font size="12">\1</font></b>', text, flags=re.IGNORECASE)
    text = re.sub(r'<h3[^>]*>(.*?)</h3>', r'<b><font size="11">\1</font></b>', text, flags=re.IGNORECASE)
    
    # Convert lists
    text = re.sub(r'<ul[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</ul>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<ol[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</ol>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'<li[^>]*>', '• ', text, flags=re.IGNORECASE)
    text = re.sub(r'</li>', '<br/>', text, flags=re.IGNORECASE)
    
    # Convert paragraphs
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '<br/>', text, flags=re.IGNORECASE)
    
    # Convert line breaks
    text = re.sub(r'<br\s*/?>', '<br/>', text, flags=re.IGNORECASE)
    
    # Convert blockquotes
    text = re.sub(r'<blockquote[^>]*>', '<i>', text, flags=re.IGNORECASE)
    text = re.sub(r'</blockquote>', '</i><br/>', text, flags=re.IGNORECASE)
    
    # Convert code blocks (keep as is, will be handled separately if needed)
    text = re.sub(r'<pre[^>]*>', '<font face="Courier">', text, flags=re.IGNORECASE)
    text = re.sub(r'</pre>', '</font>', text, flags=re.IGNORECASE)
    
    # Convert inline code
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'<font face="Courier"><b>\1</b></font>', text, flags=re.IGNORECASE)
    
    # Remove remaining HTML tags that aren't supported by ReportLab
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape HTML entities
    text = unescape(text)
    
    # Clean up multiple line breaks
    text = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', text)
    
    return text


# ========================================================================
# AI GENERATION FUNCTIONS - Groq API Integration (Free Alternative to OpenAI)
# ========================================================================

def _get_groq_client():
    """Get Groq client if available (Free AI API compatible with OpenAI)"""
    try:
        import openai
        from django.conf import settings
        
        api_key = getattr(settings, 'GROQ_API_KEY', None) or getattr(settings, 'OPENAI_API_KEY', None)
        if not api_key:
            return None
        
        # Use Groq API (OpenAI-compatible endpoint)
        # Groq provides free API access with fast inference
        return openai.OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    except ImportError:
        return None
    except Exception:
        return None


def generate_ai_explanation(topic_name):
    """Generate explanation for a topic using Groq API (Free)"""
    client = _get_groq_client()
    
    if not client:
        return f"# {topic_name}\n\nThis is a placeholder explanation. Please configure GROQ_API_KEY in settings to enable AI generation.\n\n**What is {topic_name}?**\n\n{topic_name} is a concept that requires detailed explanation. Get your free API key from https://console.groq.com"
    
    try:
        # Use Groq's fast models (llama3-8b-8192 or mixtral-8x7b-32768)
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and free Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful educational assistant. Provide clear, detailed explanations suitable for study notes."
                },
                {
                    "role": "user",
                    "content": f"Provide a clear, detailed explanation of: {topic_name}. Format the response using Markdown with headings, bullet points, and code blocks where appropriate."
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"# {topic_name}\n\nError generating AI explanation: {str(e)}\n\nPlease check your GROQ_API_KEY in settings or try again later."


def improve_explanation(current_explanation):
    """Improve existing explanation using Groq API (Free)"""
    client = _get_groq_client()
    
    if not client:
        return f"{current_explanation}\n\n---\n\n*Note: AI improvement requires GROQ_API_KEY configuration. Get free key from https://console.groq.com*"
    
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and free Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful educational assistant. Improve explanations for clarity, structure, and educational value."
                },
                {
                    "role": "user",
                    "content": f"Improve the following explanation for clarity, structure, and educational value. Keep the same format (Markdown):\n\n{current_explanation}"
                }
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"{current_explanation}\n\n---\n\n*Error improving explanation: {str(e)}*"


def summarize_explanation(explanation):
    """Summarize explanation to key points using Groq API (Free)"""
    client = _get_groq_client()
    
    if not client:
        return f"## Key Points\n\n• Main concept from the explanation\n• Important detail\n• Practical application\n\n*Note: AI summarization requires GROQ_API_KEY configuration. Get free key from https://console.groq.com*"
    
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and free Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful educational assistant. Summarize content into clear, concise key points."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following explanation into key points (use bullet points with Markdown):\n\n{explanation}"
                }
            ],
            temperature=0.5,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"## Key Points\n\n• Error summarizing: {str(e)}\n• Please try again or summarize manually."


def generate_ai_code(topic_name, language='python'):
    """Generate code example for a topic using Groq API (Free)"""
    client = _get_groq_client()
    
    if not client:
        # Return a basic template
        if language == 'python':
            return f"# {topic_name} example\n\ndef example_function():\n    \"\"\"Example implementation\"\"\"\n    # TODO: Implement {topic_name}\n    pass\n\nif __name__ == '__main__':\n    example_function()"
        else:
            return f"// {topic_name} example\n// TODO: Implement {topic_name}\n\nfunction exampleFunction() {{\n    // Implementation here\n}}"
    
    try:
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Fast and free Groq model
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful coding assistant. Generate clean, well-commented code examples in {language}."
                },
                {
                    "role": "user",
                    "content": f"Generate a {language} code example demonstrating: {topic_name}. Include comments explaining the code."
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    except Exception as e:
        if language == 'python':
            return f"# {topic_name} example\n# Error generating code: {str(e)}\n\ndef example_function():\n    pass"
        else:
            return f"// {topic_name} example\n// Error generating code: {str(e)}\n\nfunction exampleFunction() {{\n    // Implementation here\n}}"