# FILE: notes/utils.py - PDF Export with HTML Preservation
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
from html.parser import HTMLParser


class HTMLToParagraph(HTMLParser):
    """Convert HTML to ReportLab Paragraph-compatible format"""
    
    def __init__(self):
        super().__init__()
        self.result = []
        self.current_tag = None
        
    def handle_starttag(self, tag, attrs):
        tag_map = {
            'strong': '<b>',
            'b': '<b>',
            'em': '<i>',
            'i': '<i>',
            'u': '<u>',
            'h1': '<b><font size="14">',
            'h2': '<b><font size="12">',
            'h3': '<b><font size="11">',
            'code': '<font face="Courier" backColor="#f0f0f0">',
            'ul': '',
            'ol': '',
            'li': '• ',
        }
        self.current_tag = tag
        if tag in tag_map:
            self.result.append(tag_map[tag])
    
    def handle_endtag(self, tag):
        tag_map = {
            'strong': '</b>',
            'b': '</b>',
            'em': '</i>',
            'i': '</i>',
            'u': '</u>',
            'h1': '</font></b><br/>',
            'h2': '</font></b><br/>',
            'h3': '</font></b><br/>',
            'code': '</font>',
            'p': '<br/>',
            'li': '<br/>',
            'ul': '<br/>',
            'ol': '<br/>',
        }
        if tag in tag_map:
            self.result.append(tag_map[tag])
        self.current_tag = None
    
    def handle_data(self, data):
        # Clean up whitespace but preserve structure
        if self.current_tag in ['pre', 'code']:
            self.result.append(data)
        else:
            cleaned = ' '.join(data.split())
            if cleaned:
                self.result.append(cleaned)
    
    def get_result(self):
        return ''.join(self.result)


def format_text_for_pdf(html_text):
    """
    Convert HTML to ReportLab Paragraph format while preserving formatting
    """
    if not html_text:
        return ""
    
    # Remove script and style tags
    html_text = re.sub(r'<script[^>]*>.*?</script>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    html_text = re.sub(r'<style[^>]*>.*?</style>', '', html_text, flags=re.DOTALL | re.IGNORECASE)
    
    # Parse HTML
    parser = HTMLToParagraph()
    try:
        parser.feed(html_text)
        result = parser.get_result()
    except:
        # Fallback to simple cleaning
        result = re.sub(r'<[^>]+>', '', html_text)
    
    # Unescape HTML entities
    result = unescape(result)
    
    # Clean up excessive breaks
    result = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', result)
    
    return result


def export_note_to_pdf(note):
    """Export note to PDF with proper HTML formatting"""
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
    
    # Custom Styles
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
        leading=18,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica',
        allowWidows=0,
        allowOrphans=0,
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
    
    # Title Page
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
    story.append(Paragraph(metadata_text, body_style))
    story.append(PageBreak())
    
    # Chapters and Topics
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
            
            # Explanation with HTML formatting preserved
            if topic.explanation:
                explanation_text = format_text_for_pdf(topic.explanation.content)
                story.append(Paragraph(explanation_text, body_style))
                story.append(Spacer(1, 0.15*inch))
            
            # Code snippet
            if topic.code_snippet:
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    f"<b>Code Example ({topic.code_snippet.language.upper()}):</b>",
                    body_style
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
    
    doc.build(story)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    filename = f"note_{note.slug}_{date.today()}.pdf"
    return ContentFile(pdf_content, name=filename)


# Keep existing AI functions from your original utils.py
# (generate_ai_explanation, improve_explanation, etc.)

# ========================================================================
# GROQ AI INTEGRATION - IMPROVED FORMATTING
# ========================================================================

def _get_groq_client():
    """Get Groq client for AI operations"""
    try:
        from groq import Groq
        from django.conf import settings
        
        api_key = getattr(settings, 'GROQ_API_KEY', None)
        if not api_key:
            return None
        
        return Groq(api_key=api_key)
    except ImportError:
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

def markdown_to_html(markdown_text):
    """
    Convert Markdown to HTML formatted for ReactQuill
    This makes the AI-generated content look beautiful in the editor
    """
    if not markdown_text:
        return ""
    
    html = markdown_text
    
    # Convert headers (## to <h2>, ### to <h3>)
    html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    
    # Convert bold (**text** or __text__)
    html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__(.*?)__', r'<strong>\1</strong>', html)
    
    # Convert italic (*text* or _text_)
    html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
    html = re.sub(r'_(.*?)_', r'<em>\1</em>', html)
    
    # Convert inline code (`code`)
    html = re.sub(r'`(.*?)`', r'<code>\1</code>', html)
    
    # Convert code blocks (```language ... ```)
    def code_block_replacer(match):
        language = match.group(1) or 'plaintext'
        code = match.group(2).strip()
        return f'<pre><code class="language-{language}">{code}</code></pre>'
    
    html = re.sub(r'```(\w*)\n(.*?)```', code_block_replacer, html, flags=re.DOTALL)
    
    # Convert bullet lists (* item or - item)
    lines = html.split('\n')
    in_list = False
    result = []
    
    for line in lines:
        stripped = line.strip()
        
        # Check if line is a bullet point
        if stripped.startswith('* ') or stripped.startswith('- '):
            if not in_list:
                result.append('<ul>')
                in_list = True
            content = stripped[2:]  # Remove '* ' or '- '
            result.append(f'<li>{content}</li>')
        else:
            if in_list:
                result.append('</ul>')
                in_list = False
            if stripped:  # Not empty line
                result.append(f'<p>{line}</p>')
            else:
                result.append('<br/>')
    
    if in_list:
        result.append('</ul>')
    
    html = '\n'.join(result)
    
    # Convert links [text](url)
    html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
    
    # Clean up multiple line breaks
    html = re.sub(r'(<br/>\s*){3,}', '<br/><br/>', html)
    html = re.sub(r'(<p></p>\s*)+', '', html)
    
    return html


def generate_ai_explanation(topic_name):
    """Generate explanation for a topic using Groq API - IMPROVED FORMATTING"""
    client = _get_groq_client()
    
    if not client:
        return """<h2>Configuration Required</h2>
<p>To enable AI-powered content generation, please configure your Groq API key:</p>
<ol>
<li>Get your free API key from <a href="https://console.groq.com">https://console.groq.com</a></li>
<li>Add it to your .env file: <code>GROQ_API_KEY=your_key_here</code></li>
<li>Install the Groq SDK: <code>pip install groq</code></li>
</ol>
<p>Once configured, AI will generate beautiful, well-structured explanations automatically.</p>"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert educational content writer. Create clear, well-structured explanations for study notes.

IMPORTANT FORMATTING RULES:
- Use ## for main section headers
- Use ### for subsection headers  
- Use bullet points with * for lists
- Use **bold** for key terms
- Use `code` for inline code/technical terms
- Keep paragraphs concise (2-3 sentences max)
- Add blank lines between sections
- Make content visually scannable

Structure your response with:
1. Overview section
2. Key Concepts section (with bullet points)
3. Practical Examples section (with code if applicable)
4. Common Applications section"""
                },
                {
                    "role": "user",
                    "content": f"Provide a comprehensive, well-structured explanation of: {topic_name}"
                }
            ],
            temperature=0.7,
            max_tokens=1500,
            top_p=1,
            stream=False
        )
        
        markdown_content = response.choices[0].message.content
        html_content = markdown_to_html(markdown_content)
        
        return html_content
        
    except Exception as e:
        error_msg = str(e)
        return f"""<h2>Error Generating AI Content</h2>
<p><strong>Error:</strong> {error_msg}</p>
<h3>Troubleshooting:</h3>
<ul>
<li>Check your GROQ_API_KEY in settings</li>
<li>Verify API key is valid at <a href="https://console.groq.com">console.groq.com</a></li>
<li>Ensure you have internet connectivity</li>
<li>Check Groq API status at <a href="https://status.groq.com">status.groq.com</a></li>
</ul>
<p>Please write your explanation manually or try the AI generation again after fixing the configuration.</p>"""


def improve_explanation(current_explanation):
    """Improve existing explanation using Groq API - IMPROVED FORMATTING"""
    client = _get_groq_client()
    
    if not client:
        return f"""{current_explanation}
<hr/>
<p><strong>💡 AI Improvement Available</strong></p>
<p>Configure GROQ_API_KEY to enable AI-powered explanation improvements. Get your free key from <a href="https://console.groq.com">console.groq.com</a></p>"""
    
    # Convert HTML back to text for processing
    text_content = re.sub(r'<[^>]+>', ' ', current_explanation)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert editor for educational content. Improve explanations for clarity, structure, and educational value.

FORMATTING REQUIREMENTS:
- Use ## for main headers
- Use ### for subheaders
- Use bullet points with * for lists
- Use **bold** for emphasis on key terms
- Use `code` for technical terms
- Keep paragraphs short and focused
- Add clear section breaks
- Make content easy to scan visually"""
                },
                {
                    "role": "user",
                    "content": f"""Improve the following explanation for better clarity, structure, and educational value. 
Add relevant examples if missing. Maintain good formatting:

{text_content}"""
                }
            ],
            temperature=0.7,
            max_tokens=2000,
            top_p=1,
            stream=False
        )
        
        markdown_content = response.choices[0].message.content
        html_content = markdown_to_html(markdown_content)
        
        return html_content
        
    except Exception as e:
        return f"""{current_explanation}
<hr/>
<p><strong>⚠️ AI Improvement Error:</strong> {str(e)}</p>
<p>Please check your Groq API configuration or improve the content manually.</p>"""


def summarize_explanation(explanation):
    """Summarize explanation to key points using Groq API - IMPROVED FORMATTING"""
    client = _get_groq_client()
    
    if not client:
        return """<h2>Key Points Summary</h2>
<ul>
<li>Main concept from the explanation</li>
<li>Important detail to remember</li>
<li>Practical application</li>
<li>Key takeaway</li>
</ul>
<hr/>
<p><strong>Note:</strong> AI summarization requires GROQ_API_KEY configuration. Get free key from <a href="https://console.groq.com">console.groq.com</a></p>"""
    
    # Convert HTML to text
    text_content = re.sub(r'<[^>]+>', ' ', explanation)
    text_content = re.sub(r'\s+', ' ', text_content).strip()
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert at creating concise summaries. Extract the most important points in clear, well-formatted bullet lists.

FORMATTING RULES:
- Start with ## Key Points or ## Summary header
- Use bullet points with * for each key point
- Each bullet should be one clear, complete sentence
- Use **bold** for critical terms
- Limit to 5-8 key points
- Make each point actionable and memorable"""
                },
                {
                    "role": "user",
                    "content": f"Summarize the following explanation into key bullet points:\n\n{text_content}"
                }
            ],
            temperature=0.5,
            max_tokens=800,
            top_p=1,
            stream=False
        )
        
        markdown_content = response.choices[0].message.content
        html_content = markdown_to_html(markdown_content)
        
        return html_content
        
    except Exception as e:
        return f"""<h2>Summary Error</h2>
<p><strong>Error:</strong> {str(e)}</p>
<p><strong>Original Length:</strong> {len(explanation)} characters</p>
<p>Please summarize manually or fix Groq API configuration.</p>"""


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