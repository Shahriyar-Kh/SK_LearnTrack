# FILE: notes/utils.py - Backward compatibility wrappers
# ============================================================================
"""
Legacy utility functions for backward compatibility.
New code should use the specialized services directly:
- notes.ai_service for AI operations
- notes.pdf_service for PDF exports
"""

# Import from specialized services
from .pdf_service import export_note_to_pdf, format_text_for_pdf
from .ai_service import (
    generate_ai_explanation,
    improve_explanation,
    summarize_explanation,
    generate_ai_code,
    get_ai_service
)

__all__ = [
    # PDF Export
    'export_note_to_pdf',
    'format_text_for_pdf',
    
    # AI Functions
    'generate_ai_explanation',
    'improve_explanation',
    'summarize_explanation',
    'generate_ai_code',
    'get_ai_service',
]