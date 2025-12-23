# FILE: notes/migrations/0002_enhanced_notes.py
# ============================================================================
# Run this after updating models.py:
# python manage.py makemigrations notes
# python manage.py migrate notes

"""
This migration will be auto-generated when you run makemigrations.
The commands to create and apply it:

1. Create migration:
   python manage.py makemigrations notes

2. Apply migration:
   python manage.py migrate notes

3. If you need to create system templates, run:
   python manage.py shell
   
   Then in the shell:
   from notes.models import NoteTemplate
   
   # Create default templates
   NoteTemplate.objects.create(
       name='Lecture Notes',
       description='Standard template for lecture notes',
       is_system=True,
       template_content={
           'sections': [
               {'type': 'heading', 'content': 'Topic Overview'},
               {'type': 'paragraph', 'content': ''},
               {'type': 'heading', 'content': 'Key Concepts'},
               {'type': 'list', 'content': []},
               {'type': 'heading', 'content': 'Examples'},
               {'type': 'code', 'content': ''},
               {'type': 'heading', 'content': 'Summary'},
               {'type': 'paragraph', 'content': ''},
           ]
       }
   )
   
   NoteTemplate.objects.create(
       name='Code Documentation',
       description='Template for documenting code',
       is_system=True,
       template_content={
           'sections': [
               {'type': 'heading', 'content': 'Function/Class Name'},
               {'type': 'paragraph', 'content': 'Description:'},
               {'type': 'heading', 'content': 'Parameters'},
               {'type': 'list', 'content': []},
               {'type': 'heading', 'content': 'Returns'},
               {'type': 'paragraph', 'content': ''},
               {'type': 'heading', 'content': 'Example Usage'},
               {'type': 'code', 'content': ''},
           ]
       }
   )
"""

# After running migrations, install required packages:
# pip install reportlab  # For PDF generation
# pip install youtube-transcript-api  # For YouTube transcripts
# pip install bleach  # For HTML sanitization
# pip install celery redis  # Already installed for task scheduling