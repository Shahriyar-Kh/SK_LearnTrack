# FILE: notes/utils.py
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
import re
from html import unescape


def export_note_to_pdf(note):
    """
    Export note to PDF with professional hierarchical structure
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
    
    all_sources = {}
    source_counter = 1
    
    chapter_num = 1
    for chapter in note.chapters.all().order_by('order'):
        chapter_title = f"Chapter {chapter_num}: {chapter.title}"
        story.append(Paragraph(chapter_title, chapter_style))
        story.append(Spacer(1, 0.2*inch))
        
        topic_num = 1
        for topic in chapter.topics.all().order_by('order'):
            topic_title = f"{chapter_num}.{topic_num} {topic.name}"
            story.append(Paragraph(topic_title, topic_style))
            story.append(Spacer(1, 0.1*inch))
            
            if topic.explanation:
                explanation_text = topic.explanation.content
                
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
                
                explanation_text = format_text_for_pdf(explanation_text)
                story.append(Paragraph(explanation_text, body_style))
                story.append(Spacer(1, 0.15*inch))
            
            if topic.code_snippet:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    f"<b>Example Code ({topic.code_snippet.language.upper()}):</b>",
                    code_header_style
                ))
                story.append(Spacer(1, 0.08*inch))
                
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
        
        sorted_sources = sorted(all_sources.values(), key=lambda x: x['number'])
        
        for source in sorted_sources:
            ref_text = f"<b>[{source['number']}]</b> {source['title']}"
            story.append(Paragraph(ref_text, reference_style))
            
            url_text = f"<font color='#2563eb'><link href='{source['url']}'>{source['url']}</link></font>"
            story.append(Paragraph(url_text, reference_style))
            story.append(Spacer(1, 0.12*inch))
    
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"note_{note.slug}_{date.today()}.pdf"
    return ContentFile(pdf_content, name=filename)


def format_text_for_pdf(text):
    """Format HTML/rich text content for PDF"""
    if not text:
        return ""
    
    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Convert HTML headings
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
    
    # Convert paragraphs and breaks
    text = re.sub(r'<p[^>]*>', '', text, flags=re.IGNORECASE)
    text = re.sub(r'</p>', '<br/>', text, flags=re.IGNORECASE)
    text = re.sub(r'<br\s*/?>', '<br/>', text, flags=re.IGNORECASE)
    
    # Convert blockquotes and code
    text = re.sub(r'<blockquote[^>]*>', '<i>', text, flags=re.IGNORECASE)
    text = re.sub(r'</blockquote>', '</i><br/>', text, flags=re.IGNORECASE)
    text = re.sub(r'<pre[^>]*>', '<font face="Courier">', text, flags=re.IGNORECASE)
    text = re.sub(r'</pre>', '</font>', text, flags=re.IGNORECASE)
    text = re.sub(r'<code[^>]*>(.*?)</code>', r'<font face="Courier"><b>\1</b></font>', text, flags=re.IGNORECASE)
    
    # Remove remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape HTML entities
    text = unescape(text)
    
    # Clean up multiple line breaks
    text = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', text)
    
    return text


# ========================================================================
# GROQ AI INTEGRATION - Free and Fast Alternative to OpenAI
# ========================================================================

def _get_groq_client():
    """
    Get Groq client for AI operations
    Groq provides free, fast AI inference compatible with OpenAI API
    Get your free API key from: https://console.groq.com
    """
    try:
        from groq import Groq
        from django.conf import settings
        
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not api_key:
            return None
        
        return Groq(api_key=api_key)
    except ImportError:
        # Fallback to OpenAI-compatible client if groq package not installed
        try:
            import openai
            from django.conf import settings
            
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            if not api_key:
                return None
            
            return openai.OpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )
        except ImportError:
            return None
    except Exception as e:
        print(f"Error initializing Groq client: {e}")
        return None


def generate_ai_explanation(topic_name):
    """Generate explanation for a topic using Groq API"""
    client = _get_groq_client()
    
    if not client:
        return f"""# {topic_name}

## Overview
This is a placeholder explanation. To enable AI-powered content generation:

1. Get your free API key from https://console.groq.com
2. Add it to your .env file: `GROQ_API_KEY=your_key_here`
3. Install the Groq SDK: `pip install groq`

**What is {topic_name}?**

{topic_name} is an important concept that requires detailed explanation. Once you configure the Groq API, this content will be automatically generated with comprehensive explanations, examples, and insights.

## Key Points
- Configure Groq API for AI features
- Free tier available with generous limits
- Fast inference with Llama models
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Best Groq model
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational assistant. Provide clear, detailed explanations suitable for study notes. Use Markdown formatting with headings (##), bullet points, and code blocks where appropriate. Be comprehensive but concise."
                },
                {
                    "role": "user",
                    "content": f"Provide a comprehensive explanation of: {topic_name}. Include: 1) Overview, 2) Key concepts, 3) Practical examples, 4) Common use cases or applications. Format using Markdown."
                }
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            stream=False
        )
        
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        return f"""# {topic_name}

## Error Generating AI Content

**Error:** {error_msg}

**Troubleshooting:**
1. Check your GROQ_API_KEY in settings
2. Verify API key is valid at https://console.groq.com
3. Ensure you have internet connectivity
4. Check Groq API status at https://status.groq.com

**Manual Entry:**
Please write your explanation manually or try the AI generation again after fixing the configuration.
"""


def improve_explanation(current_explanation):
    """Improve existing explanation using Groq API"""
    client = _get_groq_client()
    
    if not client:
        return f"""{current_explanation}

---

**💡 AI Improvement Available**

Configure GROQ_API_KEY to enable AI-powered explanation improvements. Get your free key from https://console.groq.com
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert editor and educational content improver. Enhance explanations for clarity, structure, accuracy, and educational value. Maintain Markdown formatting. Add examples where helpful."
                },
                {
                    "role": "user",
                    "content": f"Improve the following explanation for better clarity, structure, and educational value. Add relevant examples if missing. Keep Markdown format:\n\n{current_explanation}"
                }
            ],
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            stream=False
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"""{current_explanation}

---

**⚠️ AI Improvement Error:** {str(e)}

Please check your Groq API configuration or improve the content manually.
"""


def summarize_explanation(explanation):
    """Summarize explanation to key points using Groq API"""
    client = _get_groq_client()
    
    if not client:
        return f"""## Key Points Summary

• Main concept from the explanation
• Important detail to remember
• Practical application
• Key takeaway

---

**Note:** AI summarization requires GROQ_API_KEY configuration. Get free key from https://console.groq.com
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating concise summaries. Extract and present the most important points in clear bullet format. Use Markdown."
                },
                {
                    "role": "user",
                    "content": f"Summarize the following explanation into 4-8 key bullet points. Focus on the most important concepts and practical takeaways:\n\n{explanation}"
                }
            ],
            temperature=0.5,
            max_tokens=800,
            top_p=1,
            stream=False
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"""## Summary Error

**Error:** {str(e)}

**Original Length:** {len(explanation)} characters

Please summarize manually or fix Groq API configuration.
"""


def generate_ai_code(topic_name, language='python'):
    """Generate code example for a topic using Groq API"""
    client = _get_groq_client()
    
    if not client:
        # Return language-specific template
        templates = {
            'python': f'''# {topic_name} Example
"""
Complete example demonstrating {topic_name}
Configure Groq API to auto-generate this code
"""

def example_function():
    """Implementation of {topic_name}"""
    # TODO: Implement {topic_name}
    pass

if __name__ == '__main__':
    example_function()
''',
            'javascript': f'''// {topic_name} Example
// Configure Groq API to auto-generate code

/**
 * Example implementation of {topic_name}
 */
function exampleFunction() {{
    // TODO: Implement {topic_name}
}}

exampleFunction();
''',
            'java': f'''// {topic_name} Example

public class Example {{
    /**
     * Implementation of {topic_name}
     */
    public static void main(String[] args) {{
        // TODO: Implement {topic_name}
    }}
}}
''',
        }
        return templates.get(language, templates['python'])
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {language} programmer. Generate clean, well-commented, production-ready code examples. Include docstrings/comments explaining the code. Follow {language} best practices."
                },
                {
                    "role": "user",
                    "content": f"Generate a complete, working {language} code example demonstrating: {topic_name}. Include:\n1) Clear comments explaining each part\n2) Error handling where appropriate\n3) Example usage\n4) Best practices\n\nProvide ONLY the code, no markdown formatting."
                }
            ],
            temperature=0.7,
            max_tokens=1200,
            top_p=1,
            stream=False
        )
        
        code = response.choices[0].message.content
        # Remove markdown code fences if present
        code = re.sub(r'^```[\w]*\n|```$', '', code, flags=re.MULTILINE).strip()
        return code
    except Exception as e:
        templates = {
            'python': f'# {topic_name} Example\n# Error: {str(e)}\n\ndef example():\n    pass',
            'javascript': f'// {topic_name} Example\n// Error: {str(e)}\n\nfunction example() {{\n    // Implementation\n}}',
        }
        return templates.get(language, f'// {topic_name}\n// Error: {str(e)}')