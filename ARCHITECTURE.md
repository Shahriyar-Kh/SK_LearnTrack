# SK-LearnTrack: Advanced Course Management System Architecture

## Executive Summary
A scalable, production-ready eLearning platform designed for millions of concurrent users with enterprise-grade admin tooling, AI-assisted content creation, and beautiful student learning experience.

---

## 🏗️ SYSTEM ARCHITECTURE

### Core Design Principles
1. **Separation of Concerns**: Admin (creation) vs Student (consumption) completely isolated
2. **Draft-First Workflow**: All content starts as draft; publish is explicit & versioned
3. **Read Optimization**: Student APIs heavily cached; write operations isolated
4. **AI-First but Human-Controlled**: AI suggestions never auto-publish; always editable
5. **Audit Everything**: Full history of who changed what, when
6. **Mobile-First**: All UIs responsive; async operations for heavy lifting

### Technology Stack

**Backend:**
- Django 4.2+ (LTS)
- Django REST Framework
- Django Celery (async tasks)
- PostgreSQL (prod) / SQLite (dev)
- Groq API (free, fast LLM for course content generation)
- Pillow (image processing)
- Python-markdown (markdown rendering)

**Frontend:**
- React 18+
- Redux (state management)
- React Router v6
- Tailwind CSS
- React Markdown (markdown rendering)
- React DnD (drag-drop)
- CodeMirror (code editor)
- Axios (API client)

**Deployment:**
- Backend: Render (with Celery worker)
- Frontend: Vercel
- Database: Render PostgreSQL
- Static/Media: AWS S3 or Render File System (for free tier, we'll use Render)

---

## 📊 DATABASE SCHEMA

### Core Entity Relationships

```
User (Django Auth)
├── Course (Admin creates)
│   ├── CourseChapter
│   │   ├── CourseTopic
│   │   │   ├── TopicAsset (images, code, diagrams)
│   │   │   ├── TopicQuiz
│   │   │   │   └── QuizQuestion
│   │   │   │       └── QuizChoice
│   │   │   └── SourceCode
│   │   └── ChapterQuiz
│   ├── CourseEnrollment (Student enrolls)
│   │   ├── TopicProgress (tracking where student is)
│   │   ├── QuizAttempt (quiz results)
│   │   └── StudentNote (personal notes)
│   └── CourseVersion (audit trail)
│
├── AuditLog (who did what when)
└── StudentBookmark (topics saved by students)
```

### Key Design Decisions

1. **Soft Deletes**: Archive courses without destroying data; preserve audit trail
2. **Versioning**: CourseVersion stores JSON snapshot of entire course structure
3. **Status Workflow**: DRAFT → READY → PUBLISHED → ARCHIVED
4. **Granular Progress**: Track at topic level, rollup to chapter/course
5. **Separated Quiz Models**: TopicQuiz (practice) vs CourseQuiz (certification)
6. **SEO URLs**: Each Topic has unique slug for direct access

---

## 🎯 API ARCHITECTURE

### Admin Endpoints (Protected by AdminRoute)

```
POST /api/admin/courses/
    Create new course (minimal, draft mode)
    Response: { id, title, slug, status: 'DRAFT', created_at }

PUT /api/admin/courses/{id}/
    Update course metadata
    Body: { title, description, category, thumbnail, meta_title, meta_description }

POST /api/admin/courses/{id}/chapters/
    Add chapter to course
    Body: { title, order_index, description }

PUT /api/admin/courses/{id}/chapters/{chapter_id}/
    Update chapter

DELETE /api/admin/courses/{id}/chapters/{chapter_id}/
    Delete chapter (soft delete)

POST /api/admin/courses/{id}/chapters/{chapter_id}/topics/
    Add topic to chapter
    Body: { title, description, content (markdown), order_index }

PUT /api/admin/courses/{id}/chapters/{chapter_id}/topics/{topic_id}/
    Update topic content

POST /api/admin/courses/{id}/chapters/{chapter_id}/topics/{topic_id}/assets/
    Upload topic asset (image, PDF, code)
    Multipart: { file, asset_type: 'IMAGE'|'CODE'|'DIAGRAM' }

POST /api/admin/courses/{id}/chapters/{chapter_id}/topics/{topic_id}/quiz/
    Create practice quiz for topic
    Body: { questions: [{question, choices, correct_choice, explanation}] }

PUT /api/admin/courses/{id}/structure/reorder/
    Reorder chapters/topics (drag-drop)
    Body: { chapters: [{id, order, topics: [{id, order}]}] }

GET /api/admin/courses/{id}/preview/
    Student-view preview of entire course (with mock progress)

POST /api/admin/courses/{id}/publish/
    Move course from DRAFT → PUBLISHED
    Includes validation & version snapshot

POST /api/admin/courses/{id}/unpublish/
    Move course back to DRAFT

POST /api/admin/courses/{id}/duplicate/
    Clone entire course structure

POST /api/admin/courses/{id}/export/
    Download full course as JSON or Markdown ZIP

POST /api/admin/courses/{id}/version-history/
    Get all versions with diff

GET /api/admin/courses/{id}/audit-log/
    Who did what when

POST /api/admin/ai/generate-outline/
    AI generates course outline
    Body: { topic: "Python Basics", level: "beginner" }
    Response: { chapters_outline: [...], estimated_duration: 120 }

POST /api/admin/ai/generate-chapter/
    AI generates chapter content
    Body: { course_id, chapter_title, description, depth: 'basic'|'advanced' }

POST /api/admin/ai/generate-topic/
    AI generates topic with explanation & examples
    Body: { chapter_id, topic_title, context }

POST /api/admin/ai/generate-quiz/
    AI generates quiz questions for topic
    Body: { topic_id, num_questions: 5, difficulty: 'medium' }
```

### Student Endpoints (Public, with Caching)

```
GET /api/courses/
    List all PUBLISHED courses
    Query: ?category=python&page=1&search=basics
    Cached: 1 hour

GET /api/courses/{slug}/
    Single course detail + chapter structure
    Cached: 1 hour
    Response includes: chapters, preview image, ratings, enrollment count

POST /api/courses/{id}/enroll/
    Student enrolls in course
    Creates CourseEnrollment record

GET /api/courses/{id}/structure/
    Hierarchical course structure (chapters + topics)
    Cached: 1 hour

GET /api/courses/{id}/topics/{topic_id}/
    Single topic detail with all assets, code examples
    Response: { title, content (HTML), assets[], code_snippets[], quiz }
    Cached: 24 hours

GET /api/courses/{id}/topics/{topic_id}/previous/
GET /api/courses/{id}/topics/{topic_id}/next/
    Navigation between topics

POST /api/courses/{id}/topics/{topic_id}/progress/
    Mark topic as completed
    Body: { status: 'IN_PROGRESS'|'COMPLETED', time_spent: 180 }

GET /api/courses/{id}/progress/
    Student's progress (completion %, current topic, bookmarks)

POST /api/courses/{id}/topics/{topic_id}/quiz-attempt/
    Submit quiz answers
    Body: { answers: { question_id: choice_id } }
    Response: { score, passed, explanation_per_question }

GET /api/courses/{id}/topics/{topic_id}/bookmarks/
POST /api/courses/{id}/topics/{topic_id}/bookmarks/
DELETE /api/courses/{id}/topics/{topic_id}/bookmarks/
    Manage topic bookmarks

POST /api/courses/{id}/topics/{topic_id}/notes/
GET /api/courses/{id}/topics/{topic_id}/notes/
    Student personal notes per topic

GET /api/me/dashboard/
    Student dashboard: enrolled courses, progress, recommended topics

GET /api/me/resume/
    Student's last topic across all courses
```

### SEO Considerations

```
GET /courses/{slug}/
    Renders as: <title>{course.meta_title}</title>
               <meta name="description" content="{course.meta_description}">
               <script type="application/ld+json">{schema_org_course}</script>

GET /courses/{slug}/chapters/{chapter_slug}/topics/{topic_slug}/
    Direct access to specific topic
    Dynamically builds breadcrumb navigation
```

---

## 🎨 FRONTEND ARCHITECTURE

### Admin Course Builder Component Tree

```
AdminDashboard
├── CourseList (table of all courses)
│   ├── CourseCard (status badge, actions)
│   └── CreateCourseButton
│
└── CourseBuilder (main editor)
    ├── CourseMetadataPanel (title, description, SEO settings)
    ├── CourseStructureTree (drag-drop)
    │   ├── ChapterNode (editable)
    │   │   └── TopicNode[] (editable, reorderable)
    │   └── Add ChapterButton
    │
    ├── ContentEditor (for selected topic)
    │   ├── RichTextEditor (markdown + formatting)
    │   ├── CodeBlockEditor (syntax highlighting)
    │   ├── AssetManager (upload images, diagrams)
    │   └── SourceCodeSnippets (manage example code)
    │
    ├── AIPanelSidebar
    │   ├── GenerateOutlineButton (for whole course)
    │   ├── GenerateChapterButton (for chapter)
    │   ├── GenerateTopicButton (for topic)
    │   ├── GenerateQuizButton (for topic)
    │   └── AIHistoryViewer (track AI suggestions)
    │
    ├── QuizBuilder (for topic)
    │   ├── QuestionEditor[]
    │   ├── ChoiceEditor[]
    │   └── ExplanationEditor[]
    │
    ├── PreviewPanel (right side, live preview)
    │   └── StudentViewPreview (simulated student UI)
    │
    └── ActionButtons
        ├── SaveDraft
        ├── Publish
        ├── Duplicate
        ├── Export (JSON/ZIP)
        └── VersionHistory
```

### Student Learning UI Component Tree

```
CourseDetailPage
├── SidebarLayout
│   ├── CourseSidebar
│   │   ├── CourseProgressBar
│   │   ├── ChapterList
│   │   │   └── TopicList (with checkmarks for completed)
│   │   │       ├── Bookmark button per topic
│   │   │       └── Duration indicator
│   │   ├── BookmarksSection (collapsible)
│   │   └── RelatedCoursesSection
│   │
│   └── MainContent
│       ├── TopicHeader (title, duration, difficulty)
│       ├── BreadcrumbNav
│       ├── TopicContentArea
│       │   ├── ExplanationSection (markdown rendered)
│       │   ├── CodeExamplesSection
│       │   │   └── CodeBlock (with copy, syntax highlighting)
│       │   ├── DiagramSection
│       │   └── HighlightableContent (select text to bookmark)
│       │
│       ├── PracticeSection
│       │   ├── QuizCard
│       │   │   ├── QuestionDisplay
│       │   │   ├── ChoiceButtons
│       │   │   └── Explanation (after answer)
│       │   └── QuizResultCard (score, retry button)
│       │
│       ├── RelatedTopicsSection (AI suggestions)
│       │
│       ├── StudentNotesSection
│       │   └── NoteEditor (markdown)
│       │
│       ├── BottomNav
│       │   ├── PreviousTopicButton
│       │   ├── ProgressIndicator (5/15 topics completed)
│       │   └── NextTopicButton
│       │
│       └── AskAIButton (floating) → Opens modal with topic context
```

---

## 🤖 AI INTEGRATION STRATEGY

### Free AI Source: Groq API
- **Why**: Fastest free inference API (currently supporting Mixtral, Meta Llama)
- **Rate Limits**: 14,000 tokens/minute (sufficient for async generation)
- **Cost**: $0/month for educational/open-source

### AI Workflow

```
Admin → Clicks "Generate Chapter Outline"
    ↓
Backend Celery Task (async)
    ↓
Groq API → Generate structured JSON
    {
        "chapters": [
            {
                "title": "Variables & Data Types",
                "description": "Understanding Python's type system",
                "estimated_minutes": 45,
                "key_concepts": ["str", "int", "float", "bool", "type()"],
                "topics": [
                    {
                        "title": "What is a Variable?",
                        "key_points": [...]
                    }
                ]
            }
        ]
    }
    ↓
Stored in AIDraft table (NOT in course yet)
    ↓
UI shows suggestion with "AI Generated" badge
    ↓
Admin reviews, edits, adjusts
    ↓
Admin clicks "Use This" → Moves to course structure
    ↓
Admin must explicitly hit "Publish" for course to go live
```

### AI Content Safeguards
1. **Editable by Default**: All AI output in draft state, fully editable
2. **Clearly Marked**: "✨ AI-Generated" badge visible in UI
3. **No Auto-Publish**: AI content NEVER published without manual review
4. **Versioning**: Every AI suggestion tracked in AuditLog
5. **Rate Limiting**: Per-admin limits on AI requests (free tier: 10 outlines/day)
6. **Quality Metrics**: Track which AI suggestions get accepted vs rejected

---

## ⚡ PERFORMANCE & CACHING STRATEGY

### Cache Layers

```
Level 1: Browser Cache (HTML5 LocalStorage)
  - Course structure (24 hours)
  - Student progress (5 minutes)
  - Topic content (7 days)

Level 2: Redis Cache (Backend)
  - Published course list (1 hour)
  - Single course structure (24 hours)
  - Topic content (7 days)
  - User progress aggregates (5 minutes)

Level 3: Database Query Optimization
  - Prefetch related: chapters, topics, assets
  - Select_related for foreign keys
  - Defer expensive fields (raw_content)
```

### Lazy Loading
- Topics load on-demand (not entire course)
- Assets (images) load progressively
- Quiz questions render one-by-one (not all at once)

### CDN Strategy
- Topic images → Vercel CDN (frontend)
- PDFs/uploads → Render static files or S3 (optional)
- JS/CSS → Auto-compressed by Vite

---

## 🔐 PERMISSIONS & AUTH

### Admin Permissions (Django Groups)
```python
CourseAdmin: Can create, edit, publish courses
Instructor: Can edit own courses only (future)
SupportStaff: View-only access

Permissions:
- can_create_course
- can_edit_course_{id}
- can_publish_course
- can_view_audit_log
- can_use_ai_tools
```

### Student Permissions
```python
Enrolled: Can view published course + its topics
NotEnrolled: Can view course list, course detail, but NOT topics

Permissions:
- can_view_course_{id}
- can_submit_quiz_{course_id}
```

---

## 📈 SCALABILITY ROADMAP

### Phase 1 (Current): MVP
- SQLite backend (dev), PostgreSQL (prod)
- Single Django instance on Render
- In-memory cache, no Redis

### Phase 2 (100K users)
- Add Redis for caching
- Load-balanced Django instances
- Database read replicas

### Phase 3 (1M users)
- CDN for static assets & topic images
- ElasticSearch for course search
- Microservice for AI generation
- Message queue (Celery + RabbitMQ) for background tasks

### Phase 4 (10M+ users)
- Topic content stored in document DB (MongoDB) for flexibility
- Full-text search on Elasticsearch
- Microservices: Auth, Courses, Analytics, Notifications
- GraphQL API option alongside REST

---

## 🧪 TESTING STRATEGY

### Unit Tests
- Model validation
- Serializer logic
- Permission checks

### Integration Tests
- Admin course creation flow
- Student enrollment & progress
- AI generation & storage
- Quiz submission & scoring

### E2E Tests
- Admin creates course → Publish → Student sees it
- Student takes quiz → Saves progress → Resumes later

### Performance Tests
- Course structure load time < 200ms
- Topic rendering < 500ms
- Quiz submission < 1s

---

## 📋 IMPLEMENTATION ROADMAP

### Week 1-2: Backend Models & API
1. Design & implement all models
2. Create serializers
3. Implement admin endpoints
4. Implement student endpoints
5. Write integration tests

### Week 2-3: Frontend Admin Builder
1. Course list & creation
2. Course structure editor (drag-drop)
3. Rich text editor integration
4. Quiz builder
5. Preview panel

### Week 3-4: AI Integration
1. Setup Groq API integration
2. Implement outline generation
3. Implement chapter/topic generation
4. Implement quiz generation
5. UI for AI suggestions

### Week 4-5: Frontend Student Experience
1. Course detail page
2. Topic viewer
3. Quiz taker
4. Progress tracking
5. Bookmarks & notes

### Week 5-6: Polish & Deploy
1. Caching layer
2. Performance optimization
3. SEO setup
4. Full test suite
5. Documentation & deployment guides

---

## 🎯 SUCCESS METRICS

- Admin can create full 10-chapter course in < 30 minutes
- Student can browse 50-topic course structure in < 2s
- Course structure changes cached/invalidated properly
- AI suggestions have > 80% acceptance rate
- Course publish process < 5s validation
- Student quiz submission < 1s response time
- Page load time < 3s (Core Web Vitals green)
- Uptime: 99.9%

---

## 📝 NEXT STEPS

1. Create backend models (models.py)
2. Create serializers (serializers.py)
3. Implement admin viewsets
4. Implement student viewsets
5. Create React components for admin
6. Create React components for student
7. Integrate Groq API
8. Deploy & test at scale

