# FILE: courses/AI_SERVICE.md
# ============================================================================
# AI Service Integration for Course Generation
# ============================================================================
# Using free Groq API for fast, affordable LLM inference
# ============================================================================

## Overview

The AI Service module provides FREE AI-assisted content generation for course creation using the **Groq API** (currently supporting Mixtral-8x7b and Meta Llama).

**Key Features:**
- ✅ 100% FREE (no credit card required)
- ✅ Fast inference (~10 tokens/second)
- ✅ Rate limited (14,000 tokens/minute - sufficient for async)
- ✅ Never auto-publishes content (always in draft)
- ✅ Fully editable AI suggestions
- ✅ Tracked in audit log

---

## Setup

### 1. Get FREE Groq API Key

```bash
# Visit: https://console.groq.com/keys
# Create account (free forever)
# Generate API key
# Add to .env
```

### 2. Install Groq Python SDK

```bash
pip install groq
```

### 3. Configure in settings.py

```python
# settings.py
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# AI Settings
AI_SETTINGS = {
    'provider': 'groq',  # Future: support other providers
    'model': 'mixtral-8x7b-32768',  # Fast, free tier
    'max_tokens': 2048,
    'temperature': 0.7,  # Balanced creativity
    'rate_limit_per_day': {
        'generate_outline': 10,
        'generate_chapter': 20,
        'generate_topic': 50,
        'generate_quiz': 30,
    }
}
```

---

## API Implementation

### Service Class: `AIService`

```python
# courses/ai_service.py

from groq import Groq
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta
import json

class AIService:
    """AI content generation service using Groq"""
    
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.AI_SETTINGS['model']
    
    def generate_course_outline(self, topic: str, level: str = 'beginner') -> dict:
        """
        Generate structured course outline.
        
        Args:
            topic: Course topic (e.g., "Python Basics", "React for Beginners")
            level: beginner|intermediate|advanced
        
        Returns:
            {
                "title": "Python Basics Course",
                "description": "...",
                "estimated_hours": 20,
                "chapters": [
                    {
                        "title": "Introduction to Python",
                        "description": "...",
                        "estimated_minutes": 120,
                        "topics": [
                            {
                                "title": "What is Python?",
                                "key_points": ["..."]
                            }
                        ]
                    }
                ]
            }
        """
        
        # Check rate limit
        if not self._check_rate_limit(user_id, 'generate_outline'):
            raise RateLimitExceeded()
        
        prompt = f"""Generate a detailed course outline for: {topic}
        
Level: {level}
Difficulty: {level}

Return as JSON with this structure:
{{
    "title": "Course Title",
    "description": "Brief description",
    "estimated_hours": number,
    "chapters": [
        {{
            "title": "Chapter Title",
            "description": "Chapter description",
            "estimated_minutes": number,
            "topics": [
                {{"title": "Topic Title", "key_points": ["point1", "point2"]}}
            ]
        }}
    ]
}}

Generate 3-5 chapters with 3-4 topics each. Make it comprehensive but realistic."""
        
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.7,
        )
        
        # Parse response
        content = response.choices[0].message.content
        try:
            data = json.loads(content)
            return data
        except json.JSONDecodeError:
            # Extract JSON from response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            raise ValueError("Could not parse AI response")
    
    def generate_topic_content(self, topic_title: str, context: str) -> dict:
        """
        Generate detailed topic explanation with examples.
        
        Returns:
            {
                "content": "Markdown content with explanations",
                "key_concepts": ["concept1", "concept2"],
                "code_examples": [
                    {
                        "language": "python",
                        "title": "Basic Example",
                        "code": "print('hello')"
                    }
                ],
                "practice_tips": ["tip1", "tip2"]
            }
        """
        
        prompt = f"""Create comprehensive educational content for:
        
Topic: {topic_title}
Context: {context}

Include:
1. Clear explanation (use Markdown formatting)
2. At least 2 working code examples
3. Key concepts (as bullet points)
4. Common misconceptions
5. Practice tips

Return as JSON with keys: content, key_concepts, code_examples, practice_tips

Code examples format: {{"language": "python", "title": "...", "code": "..."}}
"""
        
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=3000,
        )
        
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        return json.loads(content[start:end])
    
    def generate_quiz(self, topic_title: str, difficulty: str, num_questions: int = 5) -> dict:
        """
        Generate practice quiz questions.
        
        Returns:
            {
                "questions": [
                    {
                        "question_text": "What is...?",
                        "type": "multiple_choice",
                        "choices": [
                            {"text": "Option 1", "is_correct": true},
                            {"text": "Option 2", "is_correct": false}
                        ],
                        "explanation": "This is correct because..."
                    }
                ]
            }
        """
        
        prompt = f"""Generate {num_questions} practice quiz questions for teaching:

Topic: {topic_title}
Difficulty: {difficulty}
Type: Multiple choice (4 options each)

Return as JSON: {{"questions": [...]}}

Each question:
- question_text: clear, specific question
- choices: array of {{"text": "option text", "is_correct": bool}}
- explanation: why the correct answer is right

Make questions test understanding, not memorization.
Exactly {num_questions} questions."""
        
        response = self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
        )
        
        content = response.choices[0].message.content
        start = content.find('{')
        end = content.rfind('}') + 1
        return json.loads(content[start:end])
    
    def _check_rate_limit(self, user_id: int, action: str) -> bool:
        """Check daily rate limits per user"""
        limit_key = f'ai_rate_limit:{user_id}:{action}'
        count = cache.get(limit_key, 0)
        
        max_allowed = settings.AI_SETTINGS['rate_limit_per_day'].get(action, 0)
        
        if count >= max_allowed:
            return False
        
        cache.set(limit_key, count + 1, 86400)  # 24 hours
        return True


class RateLimitExceeded(Exception):
    """Raised when AI rate limit exceeded"""
    pass
```

---

## Admin API Endpoints

```
POST /api/admin/ai/generate-outline/
    Generate course outline
    Body: { "topic": "Python Basics", "level": "beginner" }
    Response: Complete course structure

POST /api/admin/ai/generate-chapter/
    Generate chapter content
    Body: { "course_id": 1, "chapter_title": "Variables", "depth": "basic" }

POST /api/admin/ai/generate-topic/
    Generate topic explanation
    Body: { "chapter_id": 1, "topic_title": "What is a Variable?" }

POST /api/admin/ai/generate-quiz/
    Generate quiz for topic
    Body: { "topic_id": 1, "num_questions": 5, "difficulty": "medium" }
```

---

## React Component Example

```jsx
// components/admin/AIPanel.jsx

import React, { useState } from 'react'
import { api } from '../../services/api'

export function AIPanel({ courseId, chapter }) {
    const [loading, setLoading] = useState(false)
    const [suggestion, setSuggestion] = useState(null)
    
    const generateChapterOutline = async () => {
        setLoading(true)
        try {
            const res = await api.post('/admin/ai/generate-chapter/', {
                course_id: courseId,
                chapter_title: chapter.title,
                depth: 'basic'
            })
            
            setSuggestion({
                type: 'chapter',
                data: res.data,
                timestamp: new Date()
            })
        } catch (err) {
            alert('Error: ' + err.message)
        } finally {
            setLoading(false)
        }
    }
    
    const acceptSuggestion = () => {
        // Move AI suggestion to actual course
        // Create topics from suggestion
        // Stays in DRAFT until admin publishes
    }
    
    return (
        <div className="ai-panel p-4 border rounded bg-gradient-to-r from-purple-50 to-pink-50">
            <h3 className="font-bold flex items-center gap-2">
                ✨ AI Assistant
            </h3>
            
            <button 
                onClick={generateChapterOutline}
                disabled={loading}
                className="btn btn-sm btn-primary"
            >
                {loading ? 'Generating...' : 'Generate Chapter Outline'}
            </button>
            
            {suggestion && (
                <div className="mt-4 p-3 bg-white rounded border-l-4 border-purple-500">
                    <p className="text-sm text-gray-600 mb-2">
                        Generated at {suggestion.timestamp.toLocaleTimeString()}
                    </p>
                    <div className="bg-gray-50 p-3 rounded text-sm max-h-40 overflow-y-auto">
                        <pre>{JSON.stringify(suggestion.data, null, 2)}</pre>
                    </div>
                    <div className="flex gap-2 mt-3">
                        <button className="btn btn-sm btn-success" onClick={acceptSuggestion}>
                            ✓ Use This
                        </button>
                        <button className="btn btn-sm btn-ghost" onClick={() => setSuggestion(null)}>
                            ✕ Discard
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}
```

---

## Important Guidelines

### ✅ DO:
- Always show "[AI Generated]" badge on AI-created content
- Keep ALL AI output in DRAFT until admin explicitly publishes
- Track AI suggestions in audit log (action='ai_generate')
- Show confidence scores / rate suggestions
- Allow full editing before use
- Respect rate limits

### ❌ DON'T:
- Auto-publish AI content
- Hide that content is AI-generated
- Use AI without user request
- Ignore rate limits
- Store sensitive data in AI requests

---

## Cost Tracking

Groq API is **FREE** for educational/non-commercial use.

Monitor usage:
```bash
# Check your usage at: https://console.groq.com/
# No cost, no throttling for free tier
```

For production scaling (1M+ users):
- Consider caching AI generations
- Use background queues (Celery)
- Implement smart caching layer
- Monitor token usage monthly

---

## Future Enhancements

1. **Voice Generation**: TTS for topic explanations (free Google TTS API)
2. **Image Generation**: Diagrams from text descriptions (free APIs)
3. **Translation**: Multi-language course support
4. **Real-time**: Streaming responses for instant feedback
5. **Multi-model**: Support multiple LLM providers

