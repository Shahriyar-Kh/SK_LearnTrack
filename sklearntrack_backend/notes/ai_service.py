# FILE: notes/ai_service.py - STRICT EDTECH STRUCTURE ENFORCEMENT
# ============================================================================

from django.conf import settings
import logging
import re
from typing import Dict
import markdown

logger = logging.getLogger(__name__)


class AIService:
    """
    EdTech AI Service with STRICT structure enforcement for 4 levels
    Each level has a DIFFERENT structure that MUST be followed exactly
    """
    
    def __init__(self):
        self.client = self._get_groq_client()
        self.temperature = 0.7
    
    def _get_groq_client(self):
        """Initialize Groq client"""
        try:
            from groq import Groq
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            if not api_key:
                logger.warning("GROQ_API_KEY not configured")
                return None
            return Groq(api_key=api_key)
        except ImportError:
            logger.error("groq package not installed. Run: pip install groq")
            return None
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None
    
    def _get_level_specific_prompt(self, level: str, topic: str, subject_area: str) -> Dict[str, str]:
        """Get STRICT prompts for each level - DIFFERENT STRUCTURES"""
        
        level = level.lower()
        
        # ====================================================================
        # BEGINNER LEVEL - UNIQUE STRUCTURE
        # ====================================================================
        if level == 'beginner':
            if subject_area == 'programming':
                system_prompt = """You are a teacher for COMPLETE BEGINNERS. Follow this EXACT structure:

You MUST use this EXACT structure with these EXACT headings (copy them exactly):

## Definition
1-3 short sentences defining the concept in simple terms.

## Explanation
4-5 short sentences in very simple language. Assume NO prior knowledge.

## 💻 Syntax & Usage
```language
# Show basic syntax
# Include inline comments explaining each part
# Every line must have a comment
```

## Key Points
- **Point 1:** Short, clear explanation
- **Point 2:** Short, clear explanation
- **Point 3:** Short, clear explanation
(3-5 points total)

## Simple Examples
Example 1: [Easy example with lots of comments]
```language
# Comment explaining this line
code here
```

Example 2: [Another easy example] (optional)

## Practice Set
Exercise 1: [Beginner-friendly task]
Exercise 2: [Another simple task]
Exercise 3: [One more practice] (optional)

CRITICAL RULES:
- You MUST use "Definition" as first heading (not "Topic Explanation")
- You MUST use "Explanation" as second heading
- You MUST use exactly these heading names
- DO NOT use emojis in headings except for "💻 Syntax & Usage"
- Keep everything SIMPLE for beginners
- Add LOTS of code comments"""

                user_prompt = f"""Teach **{topic}** following the EXACT beginner structure.

Use these EXACT headings in this EXACT order:
1. Definition
2. Explanation
3. 💻 Syntax & Usage
4. Key Points
5. Simple Examples
6. Practice Set

Make it very simple for complete beginners."""

            else:  # Non-programming beginner
                system_prompt = """Follow this EXACT structure for beginners:

## Definition
1-3 simple sentences

## Explanation
4-5 simple sentences

## Key Points
- Point 1
- Point 2
- Point 3

## Simple Examples
Example 1
Example 2"""

                user_prompt = f"""Explain **{topic}** for beginners using EXACT headings: Definition, Explanation, Key Points, Simple Examples."""
        
        # ====================================================================
        # INTERMEDIATE LEVEL - UNIQUE STRUCTURE
        # ====================================================================
        elif level == 'intermediate':
            if subject_area == 'programming':
                system_prompt = """You are teaching INTERMEDIATE learners. Follow this EXACT structure:

You MUST use this EXACT structure with these EXACT headings:

## Definition
1-3 short sentences defining the concept in technical terms.

## Explanation
4-5 sentences with moderate depth. Slightly technical language is OK.

## Core Concept Section
Explain clearly:
- **What problem does this solve?** [Answer here]
- **When should it be used?** [Answer here]
- **How does it fit in the bigger picture?** [Answer here]

## Key Points
- **Point 1:** Detailed explanation
- **Point 2:** Detailed explanation
- **Point 3:** Detailed explanation
(3-5 points total)

## Practical Examples
Example 1: [Real-world usage with explanation]
```language
# Practical code
```
Explanation: [Why and how it works]

Example 2: [Another practical example]

## Practice Set
Exercise 1: [Moderate difficulty task]
Exercise 2: [Another moderate task]
Exercise 3: [One more practice] (optional)

CRITICAL RULES:
- You MUST use "Definition" as first heading
- You MUST use "Explanation" as second heading
- You MUST use "Core Concept Section" as third heading
- You MUST answer the 3 questions in Core Concept Section
- NO emojis in headings
- Moderate technical depth"""

                user_prompt = f"""Teach **{topic}** following the EXACT intermediate structure.

Use these EXACT headings in this EXACT order:
1. Definition
2. Explanation
3. Core Concept Section (with 3 questions answered)
4. Key Points
5. Practical Examples
6. Practice Set

Make it practical for intermediate learners."""

            else:  # Non-programming intermediate
                system_prompt = """Follow EXACT structure:

## Definition
1-3 sentences

## Explanation
4-5 sentences with moderate depth

## Core Concept
Main idea, why it matters, how it's used

## Key Points
3-5 detailed points

## Practical Examples
2 real-world examples"""

                user_prompt = f"""Explain **{topic}** for intermediate learners."""
        
        # ====================================================================
        # ADVANCED LEVEL - UNIQUE STRUCTURE WITH EMOJIS
        # ====================================================================
        elif level == 'advanced':
            if subject_area == 'programming':
                system_prompt = """You are teaching ADVANCED programmers. Follow this EXACT structure:

You MUST use this EXACT structure with these EXACT headings (including emojis):

## 🎯 Overview
2-3 sentences explaining why this topic matters.

## 🔑 Core Concept
Simple but deep explanation covering:
- **Problem solved:** [Explanation]
- **Use cases:** [When to use it]
- **Bigger system context:** [How it fits]

## 📚 Key Points
Break into NAMED components:
- **Component 1 Name:** Clear explanation of this component
- **Component 2 Name:** Clear explanation of this component
- **Component 3 Name:** Clear explanation of this component
(3-5 components)

## 💻 Syntax & Usage
```language
// Annotated syntax showing structure
// Each part labeled with comments
// Show all important parameters/options
```

## 🔍 Detailed Explanation
Cover these aspects:
- **Internal working:** [How it works internally (simplified)]
- **Common patterns:** [Typical usage patterns]
- **Best practices:** [What experts recommend]
- **Performance considerations:** [Speed/efficiency notes]
- **Memory considerations:** [Memory usage if applicable]

## ✨ Practical Examples

### Example 1: Basic Usage
```language
// Basic example
```
**Explanation:** [How and why this works]

### Example 2: Advanced Usage
```language
// More complex example
```
**Explanation:** [Advanced techniques shown]

CRITICAL RULES:
- You MUST use emojis in ALL headings (🎯 🔑 📚 💻 🔍 ✨)
- You MUST use these EXACT emoji + heading combinations
- NO "Definition" or "Explanation" sections (that's for beginner/intermediate)
- Use ## for main headings, ### for sub-headings
- Technical depth expected"""

                user_prompt = f"""Teach **{topic}** following the EXACT advanced structure.

Use these EXACT headings with emojis in this EXACT order:
1. 🎯 Overview
2. 🔑 Core Concept
3. 📚 Key Points
4. 💻 Syntax & Usage
5. 🔍 Detailed Explanation
6. ✨ Practical Examples

Provide deep technical content."""

            else:  # Non-programming advanced
                system_prompt = """Follow EXACT structure with emojis:

## 🎯 Overview
2-3 sentences on importance

## 🔑 Core Concept
Deep explanation

## 📚 Key Points
Multiple detailed points

## ✨ Practical Examples
Advanced examples"""

                user_prompt = f"""Explain **{topic}** for advanced learners."""
        
        # ====================================================================
        # EXPERT LEVEL - MOST COMPREHENSIVE STRUCTURE
        # ====================================================================
        else:  # expert
            if subject_area == 'programming':
                system_prompt = """You are consulting with EXPERT engineers. Follow this EXACT structure:

You MUST use this EXACT structure with ALL these sections:

## 🎯 Overview
2-4 sentences focusing on impact and importance in production systems.

## 🔑 Core Concept
Deep, clear explanation covering:
- **Problem solved:** [What problem this addresses]
- **Real-world usage:** [How it's used in production]
- **System-level relevance:** [Impact on architecture]

## 📚 Key Components
Break topic into MAJOR components:
- **Component 1:** [Thorough explanation]
- **Component 2:** [Thorough explanation]
- **Component 3:** [Thorough explanation]
(3-5 major components)

## 💻 Syntax & Usage
```language
// Professional-level annotated syntax
// Show all parameters, options, variations
// Include type hints, error handling
```

## 🔍 Detailed Explanation
Comprehensive coverage:
- **Internal mechanics:** [How it works under the hood]
- **Advanced patterns:** [Expert-level usage patterns]
- **Performance trade-offs:** [Speed vs memory vs complexity]
- **Memory implications:** [Memory model, allocation, GC impact]

## ✨ Practical Examples

### Example 1: Basic Usage
```language
// Clean, production-ready code
```
**Explanation:** [Professional implementation notes]

### Example 2: Real-World Application
```language
// Actual production scenario
```
**Explanation:** [Why this approach in production]

### Example 3: Advanced Pattern
```language
// Expert-level technique
```
**Explanation:** [When and why to use this]

## ⚠️ Common Mistakes & Pitfalls
- **[Description]** → **Why it happens:** [Reason] → **How to avoid:** [Solution]
- **Mistake 2:** [Description] → **Why it happens:** [Reason] → **How to avoid:** [Solution]
- **Mistake 3:** [Description] → **Why it happens:** [Reason] → **How to avoid:** [Solution]

## 🎓 Best Practices
- **Practice 1:** [Industry recommendation with reasoning]
- **Practice 2:** [Industry recommendation with reasoning]
- **Practice 3:** [Industry recommendation with reasoning]

## 🔗 Related Concepts
- **Concept 1:** [How it relates and why it matters]
- **Concept 2:** [How it relates and why it matters]
- **Concept 3:** [How it relates and why it matters]

## 🏋️ Practice Exercises

### Beginner-Level Task
[Simple exercise to reinforce basics]

### Intermediate-Level Task
[Moderate challenge requiring understanding]

### Advanced Real-World Problem
[Complex production-level scenario]

CRITICAL RULES:
- You MUST use ALL 10 sections with emojis
- You MUST use these EXACT emoji + heading combinations
- NO "Definition" or "Explanation" (that's beginner/intermediate only)
- This is the MOST comprehensive structure
- Production-level depth required"""

                user_prompt = f"""Teach **{topic}** following the EXACT expert structure.

Use these EXACT headings with emojis in this EXACT order:
1. 🎯 Overview
2. 🔑 Core Concept
3. 📚 Key Components
4. 💻 Syntax & Usage
5. 🔍 Detailed Explanation
6. ✨ Practical Examples (3 examples)
7. ⚠️ Common Mistakes & Pitfalls
8. 🎓 Best Practices
9. 🔗 Related Concepts
10. 🏋️ Practice Exercises (3 levels)

Provide complete expert-level coverage."""

            else:  # Non-programming expert
                system_prompt = """Follow EXACT expert structure:

## 🎯 Overview
## 🔑 Core Concept
## 📚 Key Components
## 🔍 Detailed Explanation
## ✨ Practical Examples
## 🎓 Best Practices
## 🔗 Related Concepts"""

                user_prompt = f"""Explain **{topic}** for experts."""
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def generate_explanation(
        self, 
        topic_name: str, 
        subject_area: str = "programming",
        level: str = "beginner"
    ) -> str:
        """Generate explanation with STRICT structure enforcement"""
        if not self.client:
            return self._get_config_message(topic_name)
        
        try:
            prompts = self._get_level_specific_prompt(level, topic_name, subject_area)
            
            # Token limits per level
            level_tokens = {
                'beginner': 1500,      # Enough for all sections
                'intermediate': 2000,   # More detailed
                'advanced': 2800,       # Deep technical
                'expert': 4000          # Most comprehensive
            }
            max_tokens = level_tokens.get(level.lower(), 1500)
            
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": prompts['system']},
                    {"role": "user", "content": prompts['user']}
                ],
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            markdown_content = response.choices[0].message.content
            return self._markdown_to_html(markdown_content)
            
        except Exception as e:
            logger.error(f"AI generation error: {e}", exc_info=True)
            return self._get_error_message(topic_name, str(e))
    
    def improve_explanation(self, current_explanation: str, level: str = None) -> str:
        """Improve existing explanation"""
        if not self.client:
            return f"{current_explanation}\n\n---\n💡 Configure GROQ_API_KEY for AI features."
        
        text_content = re.sub(r'<[^>]+>', ' ', current_explanation)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if len(text_content) < 20:
            raise Exception("Content too short to improve")
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """Improve this educational content.

Enhance:
- Clarity and readability
- Structure and organization
- Examples (add if missing)
- Code comments (if programming)

Maintain the SAME complexity level and structure."""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this content:\n\n{text_content}"
                    }
                ],
                temperature=0.7,
                max_tokens=2500,
                stream=False
            )
            
            return self._markdown_to_html(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Improvement error: {e}")
            raise
    
    def summarize_explanation(self, explanation: str) -> str:
        """Summarize to key points"""
        if not self.client:
            return "## Summary\n\nConfigure GROQ_API_KEY to enable summarization"
        
        text_content = re.sub(r'<[^>]+>', ' ', explanation)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": """Create a concise summary.

Structure:
## 🎯 Main Idea
One clear sentence

## 📌 Key Points
- Point 1
- Point 2
- Point 3
(3-5 points max)

Keep it SHORT and FOCUSED."""
                    },
                    {
                        "role": "user",
                        "content": f"Summarize:\n\n{text_content}"
                    }
                ],
                temperature=0.5,
                max_tokens=800,
                stream=False
            )
            
            return self._markdown_to_html(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            raise
    
    def generate_code(self, topic_name: str, language: str = 'python', level: str = 'beginner') -> str:
        """Generate code example based on level"""
        if not self.client:
            return self._get_code_template(topic_name, language)
        
        level_instructions = {
            'beginner': "SIMPLE code with a comment on EVERY LINE for complete beginners.",
            'intermediate': "PRACTICAL code with clear comments and best practices.",
            'advanced': "OPTIMIZED code with performance considerations and advanced patterns.",
            'expert': "PRODUCTION-GRADE code with error handling, logging, and type hints."
        }
        
        instruction = level_instructions.get(level.lower(), level_instructions['beginner'])
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": f"""Expert {language} programmer.

Generate {instruction}

Requirements:
- Clean, working code
- Appropriate comments for level
- Good variable names
- Example usage

Provide ONLY code with comments. No markdown formatting."""
                    },
                    {
                        "role": "user",
                        "content": f"Generate {language} code for: {topic_name}"
                    }
                ],
                temperature=0.7,
                max_tokens=1500,
                stream=False
            )
            
            code = response.choices[0].message.content
            code = re.sub(r'^```[\w]*\n|```$', '', code, flags=re.MULTILINE).strip()
            return code
        except Exception as e:
            logger.error(f"Code generation error: {e}")
            return self._get_code_template(topic_name, language, str(e))
    
    def _markdown_to_html(self, text: str) -> str:
        """Convert markdown to HTML with styling"""
        if not text:
            return ""
        
        try:
            extensions = ['extra', 'codehilite', 'tables', 'nl2br']
            html = markdown.markdown(text, extensions=extensions)
            
            # Add styling classes
            html = re.sub(r'<h1>(.*?)</h1>', r'<h1 class="text-3xl font-bold mt-6 mb-3 text-blue-900">\1</h1>', html)
            html = re.sub(r'<h2>(.*?)</h2>', r'<h2 class="text-2xl font-bold mt-5 mb-2 text-blue-800">\1</h2>', html)
            html = re.sub(r'<h3>(.*?)</h3>', r'<h3 class="text-xl font-semibold mt-4 mb-2 text-blue-700">\1</h3>', html)
            html = re.sub(r'<p>(.*?)</p>', r'<p class="mb-3 leading-relaxed text-gray-800">\1</p>', html)
            html = re.sub(r'<ul>', r'<ul class="list-disc pl-6 mb-3 space-y-1">', html)
            html = re.sub(r'<ol>', r'<ol class="list-decimal pl-6 mb-3 space-y-1">', html)
            html = re.sub(r'<code>(.*?)</code>', r'<code class="bg-gray-100 text-red-600 px-1.5 py-0.5 rounded font-mono text-sm">\1</code>', html)
            html = re.sub(r'<pre>', r'<pre class="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">', html)
            
            return html
        except Exception as e:
            logger.error(f"Markdown conversion error: {e}")
            return text.replace('\n', '<br/>')
    
    def _get_config_message(self, topic_name: str) -> str:
        """Configuration message"""
        return f"""<h2>{topic_name}</h2>
<div class="p-4 bg-yellow-50 border-l-4 border-yellow-500 rounded">
<h3 class="font-bold text-yellow-800">⚙️ AI Configuration Required</h3>
<p class="text-yellow-700 mt-2">Configure GROQ_API_KEY in settings to enable AI features.</p>
<p class="text-yellow-700 mt-1">Get free API key: <a href="https://console.groq.com" class="underline" target="_blank">console.groq.com</a></p>
</div>"""
    
    def _get_error_message(self, context: str, error: str) -> str:
        """Error message"""
        return f"""<div class="p-4 bg-red-50 border-l-4 border-red-500 rounded">
<h3 class="font-bold text-red-800">❌ AI Error</h3>
<p class="text-red-700 mt-2">Error: {error}</p>
</div>"""
    
    def _get_code_template(self, topic: str, language: str, error: str = None) -> str:
        """Code template when AI unavailable"""
        error_msg = f'Error: {error}' if error else 'Configure GROQ_API_KEY'
        
        templates = {
            'python': f'''# {topic}
"""
{error_msg}
"""

def example():
    """Example for {topic}"""
    pass
''',
            'javascript': f'''// {topic}
// {error_msg}

function example() {{
  // Your code here
}}
''',
        }
        return templates.get(language, templates['python'])


# Singleton instance
_ai_service = None

def get_ai_service():
    """Get AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


# Convenience functions
def generate_ai_explanation(topic_name: str, subject_area: str = "programming", level: str = "beginner") -> str:
    """Generate explanation with level"""
    return get_ai_service().generate_explanation(topic_name, subject_area, level)


def improve_explanation(current_explanation: str, level: str = None) -> str:
    """Improve explanation"""
    return get_ai_service().improve_explanation(current_explanation, level)


def summarize_explanation(explanation: str) -> str:
    """Summarize explanation"""
    return get_ai_service().summarize_explanation(explanation)


def generate_ai_code(topic_name: str, language: str = 'python', level: str = 'beginner') -> str:
    """Generate code with level"""
    return get_ai_service().generate_code(topic_name, language, level)