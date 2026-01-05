# FILE: notes/ai_service.py - AI Content Generation Service
# ============================================================================

from django.conf import settings
import logging
import re

logger = logging.getLogger(__name__)
# Add at the top of the file, after imports
import markdown
from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor
class FormatExtension(Extension):
    """Custom markdown extension for educational content"""
    def extendMarkdown(self, md):
        md.registerExtension(self)


def markdown_to_html(text):
    """Convert markdown to HTML with proper formatting"""
    if not text:
        return ""
    
    try:
        # Configure markdown with extensions
        extensions = [
            'extra',          # Adds tables, footnotes, etc.
            'codehilite',     # Syntax highlighting
            'admonition',     # Notes and warnings
            'tables',         # Table support
            'smarty',         # Smart quotes, dashes
            FormatExtension() # Custom formatting
        ]
        
        # Convert markdown to HTML
        html = markdown.markdown(text, extensions=extensions)
        
        # Add Bootstrap-like classes for better styling
        html = re.sub(r'<h1>(.*?)</h1>', r'<h1 class="text-3xl font-bold mt-4 mb-2">\1</h1>', html)
        html = re.sub(r'<h2>(.*?)</h2>', r'<h2 class="text-2xl font-bold mt-3 mb-2">\1</h2>', html)
        html = re.sub(r'<h3>(.*?)</h3>', r'<h3 class="text-xl font-bold mt-2 mb-1">\1</h3>', html)
        html = re.sub(r'<p>(.*?)</p>', r'<p class="mb-3 leading-relaxed">\1</p>', html)
        html = re.sub(r'<ul>', r'<ul class="list-disc pl-5 mb-3">', html)
        html = re.sub(r'<ol>', r'<ol class="list-decimal pl-5 mb-3">', html)
        html = re.sub(r'<li>', r'<li class="mb-1">', html)
        html = re.sub(r'<code>(.*?)</code>', r'<code class="bg-gray-100 text-red-600 px-1 rounded">\1</code>', html)
        html = re.sub(r'<blockquote>', r'<blockquote class="border-l-4 border-blue-500 pl-4 italic my-3">', html)
        
        return html
        
    except Exception as e:
        logger.error(f"Markdown conversion error: {e}")
        # Return as plain HTML if conversion fails
        return text.replace('\n', '<br/>')



# Then update the AIService class methods to use markdown_to_html:
class AIService:
    """Service for AI-powered content generation using Groq"""
    
    def __init__(self):
        self.client = self._get_groq_client()
    
    def _get_groq_client(self):
        """Get Groq client for AI operations"""
        try:
            from groq import Groq
            
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            if not api_key:
                logger.warning("GROQ_API_KEY not configured")
                return None
            
            return Groq(api_key=api_key)
        except ImportError:
            try:
                import openai
                api_key = getattr(settings, 'GROQ_API_KEY', None)
                if not api_key:
                    return None
                
                return openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
            except ImportError:
                logger.error("Neither groq nor openai package is installed")
                return None
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            return None
    
    def is_available(self):
        """Check if AI service is available"""
        return self.client is not None
    
    def generate_explanation(self, topic_name):
        """Generate explanation for a topic"""
        if not self.client:
            return markdown_to_html(self._get_config_message(topic_name))
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert educational assistant. Provide clear, detailed explanations suitable for study notes. 

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
            return markdown_to_html(markdown_content)
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return markdown_to_html(self._get_error_message(topic_name, str(e))) 
          
    def improve_explanation(self, current_explanation):
        """Improve existing explanation"""
        if not self.client:
            return f"{current_explanation}\n\n---\n**💡 AI Improvement Available**\nConfigure GROQ_API_KEY to enable AI-powered explanation improvements."
        
        # Convert HTML back to text for processing
        text_content = re.sub(r'<[^>]+>', ' ', current_explanation)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert editor and educational content improver. Enhance explanations for clarity, structure, accuracy, and educational value.

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
                        "content": f"Improve the following explanation for better clarity, structure, and educational value. Add relevant examples if missing. Maintain good formatting:\n\n{text_content}"
                    }
                ],
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                stream=False
            )
            
            markdown_content = response.choices[0].message.content
            return markdown_to_html(markdown_content)
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return markdown_to_html(self._get_error_message(current_explanation, str(e))) 
    
    def summarize_explanation(self, explanation):
        """Summarize explanation to key points"""
        if not self.client:
            return """## Key Points Summary

- Configure GROQ_API_KEY to enable AI summarization
- Get your free API key from https://console.groq.com
- Install the Groq SDK: `pip install groq`
"""
        
        # Convert HTML to text
        text_content = re.sub(r'<[^>]+>', ' ', explanation)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        try:
            response = self.client.chat.completions.create(
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
            return markdown_to_html(markdown_content)
        except Exception as e:
            logger.error(f"AI generation error: {e}")
            return markdown_to_html(self._get_error_message(summarize_explanation, str(e))) 
    
    def generate_code(self, topic_name, language='python'):
        """Generate code example"""
        if not self.client:
            return self._get_code_template(topic_name, language)
        
        try:
            response = self.client.chat.completions.create(
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
            logger.error(f"AI code generation error: {e}")
            return self._get_code_template(topic_name, language, error=str(e))
    
    def _get_config_message(self, topic_name):
        """Get configuration message"""
        return f"""# {topic_name}

## Configuration Required

To enable AI-powered content generation, please configure your Groq API key:

1. Get your free API key from https://console.groq.com
2. Add it to your .env file: `GROQ_API_KEY=your_key_here`
3. Install the Groq SDK: `pip install groq`

**What is {topic_name}?**

Once configured, AI will generate comprehensive explanations, examples, and insights automatically.

## Key Benefits
- Free tier available with generous limits
- Fast inference with Llama models
- High-quality educational content
- Support for multiple programming languages
"""
    
    def _get_error_message(self, topic_name, error):
        """Get error message"""
        return f"""# {topic_name}

## Error Generating AI Content

**Error:** {error}

### Troubleshooting:
- Check your GROQ_API_KEY in settings
- Verify API key is valid at https://console.groq.com
- Ensure you have internet connectivity
- Check Groq API status at https://status.groq.com

### Manual Entry:
Please write your explanation manually or try the AI generation again after fixing the configuration.
"""
    
    def _get_code_template(self, topic_name, language, error=None):
        """Get code template"""
        templates = {
            'python': f'''# {topic_name} Example
"""
Complete example demonstrating {topic_name}
{f"Error: {error}" if error else "Configure Groq API to auto-generate this code"}
"""

def example_function():
    """Implementation of {topic_name}"""
    # TODO: Implement {topic_name}
    pass

if __name__ == '__main__':
    example_function()
''',
            'javascript': f'''// {topic_name} Example
{f"// Error: {error}" if error else "// Configure Groq API to auto-generate code"}

/**
 * Example implementation of {topic_name}
 */
function exampleFunction() {{
    // TODO: Implement {topic_name}
}}

exampleFunction();
''',
            'java': f'''// {topic_name} Example
{f"// Error: {error}" if error else ""}

public class Example {{
    /**
     * Implementation of {topic_name}
     */
    public static void main(String[] args) {{
        // TODO: Implement {topic_name}
    }}
}}
''',
            'typescript': f'''// {topic_name} Example
{f"// Error: {error}" if error else ""}

/**
 * Example implementation of {topic_name}
 */
function exampleFunction(): void {{
    // TODO: Implement {topic_name}
}}

exampleFunction();
''',
            'cpp': f'''// {topic_name} Example
{f"// Error: {error}" if error else ""}

#include <iostream>

/**
 * Implementation of {topic_name}
 */
int main() {{
    // TODO: Implement {topic_name}
    return 0;
}}
''',
        }
        return templates.get(language, templates['python'])


# Global AI service instance (Singleton pattern)
_ai_service = None


def get_ai_service():
    """Get singleton AI service instance"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# Convenience functions for backward compatibility
def generate_ai_explanation(topic_name):
    """Generate explanation for a topic"""
    return get_ai_service().generate_explanation(topic_name)


def improve_explanation(current_explanation):
    """Improve existing explanation"""
    return get_ai_service().improve_explanation(current_explanation)


def summarize_explanation(explanation):
    """Summarize explanation to key points"""
    return get_ai_service().summarize_explanation(explanation)


def generate_ai_code(topic_name, language='python'):
    """Generate code example for a topic"""
    return get_ai_service().generate_code(topic_name, language)