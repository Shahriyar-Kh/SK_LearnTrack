# FILE: REACT_COMPONENTS.md
# ============================================================================
# React Components Architecture for SK-LearnTrack
# ============================================================================
# Admin Course Builder + Student Learning Experience
# ============================================================================

## Project Structure

```
sklearntrack-frontend/src/
├── components/
│   ├── admin/
│   │   ├── CourseBuilder/
│   │   │   ├── CourseBuilder.jsx (main container)
│   │   │   ├── CourseMetadataPanel.jsx
│   │   │   ├── CourseStructureTree.jsx
│   │   │   ├── ContentEditor.jsx
│   │   │   ├── RichTextEditor.jsx
│   │   │   ├── CodeBlockEditor.jsx
│   │   │   ├── AssetManager.jsx
│   │   │   ├── QuizBuilder.jsx
│   │   │   ├── AIPanelSidebar.jsx
│   │   │   ├── PreviewPanel.jsx
│   │   │   └── ActionButtons.jsx
│   │   ├── CourseList.jsx
│   │   └── CourseCard.jsx
│   │
│   ├── student/
│   │   ├── CourseDetailPage.jsx (main learner layout)
│   │   ├── CourseSidebar.jsx (navigation + bookmarks)
│   │   ├── TopicViewer.jsx
│   │   ├── TopicContent.jsx
│   │   ├── CodeBlockViewer.jsx
│   │   ├── QuizCard.jsx
│   │   ├── QuizResultCard.jsx
│   │   ├── StudentNotesEditor.jsx
│   │   ├── ProgressBar.jsx
│   │   └── TopicNavigation.jsx
│   │
│   ├── common/
│   │   ├── MarkdownRenderer.jsx
│   │   ├── Button.jsx
│   │   ├── Input.jsx
│   │   ├── Card.jsx
│   │   ├── LoadingSpinner.jsx
│   │   ├── ErrorBoundary.jsx
│   │   └── Toast.jsx
│   │
│   └── layout/
│       ├── Navbar.jsx
│       ├── Footer.jsx
│       └── AdminLayout.jsx
│
├── pages/
│   ├── AdminCoursesPage.jsx
│   ├── AdminCourseBuilderPage.jsx
│   ├── CoursesPage.jsx
│   ├── CourseDetailPage.jsx
│   └── StudentDashboardPage.jsx
│
├── services/
│   ├── api.js
│   ├── courseService.js
│   ├── courseAdminService.js
│   └── authService.js
│
├── store/
│   ├── index.js
│   └── slices/
│       ├── authSlice.js
│       ├── courseSlice.js
│       ├── courseAdminSlice.js
│       └── studentProgressSlice.js
│
└── utils/
    ├── constants.js
    ├── formatters.js
    └── validators.js
```

---

## Admin Course Builder Components

### 1. **CourseBuilder.jsx** (Main Container)

```jsx
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { courseAdminService } from '../../services/courseAdminService'

export function CourseBuilder() {
    const { courseId } = useParams()
    const [course, setCourse] = useState(null)
    const [selectedElement, setSelectedElement] = useState(null) // chapter|topic
    const [loading, setLoading] = useState(true)
    
    useEffect(() => {
        if (courseId) {
            courseAdminService.getCourseDetail(courseId)
                .then(setCourse)
                .finally(() => setLoading(false))
        }
    }, [courseId])
    
    const handleSaveCourse = (metadata) => {
        courseAdminService.updateCourse(courseId, metadata)
            .then(updated => setCourse(updated))
    }
    
    const handlePublish = async () => {
        const response = await courseAdminService.publishCourse(courseId)
        setCourse(response)
        alert('Course published!')
    }
    
    if (loading) return <LoadingSpinner />
    if (!course) return <div>Course not found</div>
    
    return (
        <div className="grid grid-cols-4 gap-4 h-screen p-4">
            {/* Left: Course Metadata */}
            <div className="col-span-1 border rounded p-4 overflow-y-auto">
                <CourseMetadataPanel 
                    course={course} 
                    onSave={handleSaveCourse}
                />
            </div>
            
            {/* Center-Left: Structure Tree */}
            <div className="col-span-1 border rounded p-4 overflow-y-auto">
                <CourseStructureTree 
                    course={course}
                    onSelectElement={setSelectedElement}
                    selectedElement={selectedElement}
                />
            </div>
            
            {/* Center-Right: Content Editor */}
            <div className="col-span-1 border rounded p-4 overflow-y-auto">
                {selectedElement ? (
                    <ContentEditor 
                        element={selectedElement}
                        courseId={courseId}
                    />
                ) : (
                    <div className="text-gray-500 text-center">
                        Select a topic to edit
                    </div>
                )}
            </div>
            
            {/* Right: AI Panel + Preview */}
            <div className="col-span-1 border rounded p-4 overflow-y-auto space-y-4">
                <AIPanelSidebar courseId={courseId} />
                <PreviewPanel courseId={courseId} />
                <ActionButtons 
                    course={course}
                    onPublish={handlePublish}
                />
            </div>
        </div>
    )
}
```

### 2. **CourseMetadataPanel.jsx**

```jsx
import React, { useState } from 'react'
import { Input, Button } from '../common'

export function CourseMetadataPanel({ course, onSave }) {
    const [form, setForm] = useState(course)
    const [isSaving, setIsSaving] = useState(false)
    
    const handleChange = (field) => (e) => {
        setForm(prev => ({
            ...prev,
            [field]: e.target.value
        }))
    }
    
    const handleSave = async () => {
        setIsSaving(true)
        try {
            await onSave(form)
        } finally {
            setIsSaving(false)
        }
    }
    
    return (
        <div className="space-y-4">
            <h2 className="text-xl font-bold">Course Metadata</h2>
            
            <div>
                <label className="block text-sm font-medium mb-1">Title</label>
                <Input 
                    value={form.title}
                    onChange={handleChange('title')}
                    className="w-full"
                />
            </div>
            
            <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea 
                    value={form.description}
                    onChange={handleChange('description')}
                    rows={4}
                    className="w-full border rounded p-2"
                />
            </div>
            
            <div>
                <label className="block text-sm font-medium mb-1">Difficulty</label>
                <select value={form.difficulty} onChange={handleChange('difficulty')} className="w-full border rounded p-2">
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                </select>
            </div>
            
            <div>
                <label className="block text-sm font-medium mb-1">Category</label>
                <Input 
                    value={form.category}
                    onChange={handleChange('category')}
                    className="w-full"
                />
            </div>
            
            {/* SEO Section */}
            <div className="border-t pt-4">
                <h3 className="font-medium mb-3">SEO Settings</h3>
                <Input 
                    placeholder="SEO Title (< 60 chars)"
                    value={form.meta_title}
                    onChange={handleChange('meta_title')}
                    maxLength={60}
                    className="w-full mb-2"
                />
                <textarea 
                    placeholder="SEO Description (< 160 chars)"
                    value={form.meta_description}
                    onChange={handleChange('meta_description')}
                    maxLength={160}
                    rows={2}
                    className="w-full border rounded p-2"
                />
            </div>
            
            <Button 
                onClick={handleSave}
                disabled={isSaving}
                className="w-full"
            >
                {isSaving ? 'Saving...' : 'Save Metadata'}
            </Button>
        </div>
    )
}
```

### 3. **CourseStructureTree.jsx** (Drag-Drop)

```jsx
import React, { useState } from 'react'
import { DndContext, DragEndEvent } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

function ChapterNode({ chapter, topics, onSelectTopic, selectedElement }) {
    const [isExpanded, setIsExpanded] = useState(true)
    const { attributes, listeners, setNodeRef, transform, transition } = useSortable({
        id: `chapter-${chapter.id}`
    })
    
    const style = {
        transform: CSS.Transform.toString(transform),
        transition
    }
    
    return (
        <div ref={setNodeRef} style={style} className="ml-2 border-l-2">
            <div 
                {...attributes}
                {...listeners}
                className="py-1 px-2 cursor-move hover:bg-gray-100 rounded flex items-center gap-2"
            >
                <button 
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="text-sm"
                >
                    {isExpanded ? '▼' : '▶'}
                </button>
                <span className="font-medium">{chapter.title}</span>
            </div>
            
            {isExpanded && (
                <div className="ml-4">
                    {topics.map(topic => (
                        <TopicNode 
                            key={topic.id}
                            topic={topic}
                            isSelected={selectedElement?.id === topic.id}
                            onSelect={onSelectTopic}
                        />
                    ))}
                </div>
            )}
        </div>
    )
}

function TopicNode({ topic, isSelected, onSelect }) {
    const { setNodeRef, transform, transition } = useSortable({
        id: `topic-${topic.id}`
    })
    
    const style = {
        transform: CSS.Transform.toString(transform),
        transition
    }
    
    return (
        <div
            ref={setNodeRef}
            style={style}
            onClick={() => onSelect(topic)}
            className={`py-1 px-2 cursor-pointer rounded text-sm ${
                isSelected 
                    ? 'bg-blue-200 border-l-4 border-blue-500' 
                    : 'hover:bg-gray-100'
            }`}
        >
            {topic.title}
        </div>
    )
}

export function CourseStructureTree({ course, onSelectElement, selectedElement }) {
    const [chapters, setChapters] = useState(course.chapters)
    
    const handleDragEnd = async (event) => {
        // Reorder logic here
        // Call API to save new order
    }
    
    return (
        <div>
            <h2 className="text-xl font-bold mb-4">Course Structure</h2>
            <DndContext onDragEnd={handleDragEnd}>
                <div className="space-y-1">
                    {chapters.map(chapter => (
                        <ChapterNode
                            key={chapter.id}
                            chapter={chapter}
                            topics={chapter.topics}
                            onSelectTopic={onSelectElement}
                            selectedElement={selectedElement}
                        />
                    ))}
                </div>
            </DndContext>
        </div>
    )
}
```

### 4. **ContentEditor.jsx** (Markdown + Assets)

```jsx
import React, { useState } from 'react'
import { RichTextEditor } from './RichTextEditor'
import { CodeBlockEditor } from './CodeBlockEditor'
import { AssetManager } from './AssetManager'
import { Button } from '../common'

export function ContentEditor({ element, courseId }) {
    const [topic, setTopic] = useState(element)
    const [isSaving, setIsSaving] = useState(false)
    
    const handleContentChange = (content) => {
        setTopic(prev => ({
            ...prev,
            content
        }))
    }
    
    const handleSave = async () => {
        setIsSaving(true)
        try {
            // API call to save topic
            await coursesAdminService.updateTopic(courseId, topic.chapter_id, topic.id, topic)
        } finally {
            setIsSaving(false)
        }
    }
    
    return (
        <div className="space-y-4">
            <h3 className="text-lg font-bold">{topic.title}</h3>
            
            {/* Markdown Editor */}
            <div>
                <label className="block text-sm font-medium mb-2">Content</label>
                <RichTextEditor 
                    value={topic.content}
                    onChange={handleContentChange}
                    height={300}
                />
            </div>
            
            {/* Estimated Duration */}
            <div>
                <label className="block text-sm font-medium mb-1">Estimated Minutes</label>
                <input 
                    type="number"
                    value={topic.estimated_minutes}
                    onChange={(e) => setTopic(prev => ({
                        ...prev,
                        estimated_minutes: parseInt(e.target.value)
                    }))}
                    className="w-full border rounded p-2"
                />
            </div>
            
            {/* Code Examples */}
            <div>
                <h4 className="font-medium mb-2">Code Examples</h4>
                <CodeBlockEditor topic={topic} onUpdate={setTopic} />
            </div>
            
            {/* Assets */}
            <div>
                <h4 className="font-medium mb-2">Assets</h4>
                <AssetManager topicId={topic.id} onUpload={(asset) => {
                    setTopic(prev => ({
                        ...prev,
                        assets: [...prev.assets, asset]
                    }))
                }} />
            </div>
            
            <Button 
                onClick={handleSave}
                disabled={isSaving}
                className="w-full bg-green-600"
            >
                {isSaving ? 'Saving...' : 'Save Topic'}
            </Button>
        </div>
    )
}
```

### 5. **AIPanelSidebar.jsx**

```jsx
import React, { useState } from 'react'
import { api } from '../../services/api'
import { Button } from '../common'

export function AIPanelSidebar({ courseId }) {
    const [aiSuggestion, setAiSuggestion] = useState(null)
    const [loading, setLoading] = useState(false)
    
    const generateOutline = async () => {
        setLoading(true)
        try {
            const res = await api.post('/admin/ai/generate-outline/', {
                topic: 'Course Topic Here',
                level: 'beginner'
            })
            setAiSuggestion({
                type: 'outline',
                data: res.data,
                timestamp: new Date()
            })
        } finally {
            setLoading(false)
        }
    }
    
    const acceptSuggestion = async () => {
        // Logic to create course from AI suggestion
        alert('Accepted! Chapters added to draft.')
        setAiSuggestion(null)
    }
    
    return (
        <div className="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded border-l-4 border-purple-500">
            <h3 className="font-bold mb-3 flex items-center gap-2">
                ✨ AI Assistant
            </h3>
            
            <div className="space-y-2">
                <Button 
                    onClick={generateOutline}
                    disabled={loading}
                    className="w-full bg-purple-600"
                >
                    {loading ? 'Generating...' : '📊 Generate Outline'}
                </Button>
                
                <Button className="w-full bg-purple-600">📝 Generate Topic</Button>
                <Button className="w-full bg-purple-600">❓ Generate Quiz</Button>
            </div>
            
            {aiSuggestion && (
                <div className="mt-4 p-3 bg-white rounded border border-purple-300">
                    <p className="text-xs text-gray-600 mb-2">
                        Generated {aiSuggestion.timestamp.toLocaleTimeString()}
                    </p>
                    <div className="bg-gray-50 p-2 rounded text-xs max-h-32 overflow-y-auto">
                        <pre>{JSON.stringify(aiSuggestion.data, null, 2)}</pre>
                    </div>
                    <div className="flex gap-2 mt-3">
                        <Button 
                            onClick={acceptSuggestion}
                            className="flex-1 bg-green-600 text-sm"
                        >
                            ✓ Use
                        </Button>
                        <Button 
                            onClick={() => setAiSuggestion(null)}
                            className="flex-1 bg-gray-400 text-sm"
                        >
                            ✕ Discard
                        </Button>
                    </div>
                </div>
            )}
        </div>
    )
}
```

---

## Student Learning Components

### 1. **CourseDetailPage.jsx** (Main Learner UI)

```jsx
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { courseService } from '../../services/courseService'
import { CourseSidebar } from './CourseSidebar'
import { TopicViewer } from './TopicViewer'
import { LoadingSpinner } from '../common'

export function CourseDetailPage() {
    const { courseSlug, topicSlug } = useParams()
    const [course, setCourse] = useState(null)
    const [currentTopic, setCurrentTopic] = useState(null)
    const [enrollment, setEnrollment] = useState(null)
    const [loading, setLoading] = useState(true)
    
    useEffect(() => {
        const loadCourse = async () => {
            const courseData = await courseService.getCourseBySlug(courseSlug)
            setCourse(courseData)
            
            const enrollmentData = await courseService.enroll(courseData.id)
            setEnrollment(enrollmentData)
            
            if (topicSlug) {
                const topic = courseData.chapters
                    .flatMap(ch => ch.topics)
                    .find(t => t.slug === topicSlug)
                setCurrentTopic(topic)
            } else {
                // Load last accessed or first topic
                setCurrentTopic(courseData.chapters[0]?.topics[0])
            }
            
            setLoading(false)
        }
        
        loadCourse()
    }, [courseSlug, topicSlug])
    
    if (loading) return <LoadingSpinner />
    if (!course) return <div>Course not found</div>
    
    return (
        <div className="grid grid-cols-4 gap-4 min-h-screen bg-gray-50">
            {/* Sidebar */}
            <div className="col-span-1 bg-white border-r">
                <CourseSidebar 
                    course={course}
                    currentTopic={currentTopic}
                    enrollment={enrollment}
                    onSelectTopic={setCurrentTopic}
                />
            </div>
            
            {/* Main Content */}
            <div className="col-span-3">
                {currentTopic ? (
                    <TopicViewer 
                        topic={currentTopic}
                        course={course}
                        enrollment={enrollment}
                    />
                ) : (
                    <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">Select a topic to begin</p>
                    </div>
                )}
            </div>
        </div>
    )
}
```

### 2. **TopicViewer.jsx**

```jsx
import React, { useState, useEffect } from 'react'
import { MarkdownRenderer } from '../common/MarkdownRenderer'
import { QuizCard } from './QuizCard'
import { StudentNotesEditor } from './StudentNotesEditor'
import { TopicNavigation } from './TopicNavigation'
import { ProgressBar } from './ProgressBar'

export function TopicViewer({ topic, course, enrollment }) {
    const [studentNote, setStudentNote] = useState(null)
    const [quizResults, setQuizResults] = useState(null)
    const [bookmark, setBookmark] = useState(false)
    
    const handleBookmark = async () => {
        // API call
        setBookmark(!bookmark)
    }
    
    const handleQuizSubmit = async (answers) => {
        const results = await courseService.submitQuiz(topic.id, answers)
        setQuizResults(results)
    }
    
    return (
        <div className="p-6 max-w-3xl">
            {/* Header */}
            <div className="mb-6 pb-4 border-b">
                <div className="flex items-start justify-between">
                    <div>
                        <h1 className="text-3xl font-bold mb-2">{topic.title}</h1>
                        <p className="text-gray-600">
                            {topic.estimated_minutes} min read • 
                            Difficulty: {topic.difficulty}
                        </p>
                    </div>
                    <button 
                        onClick={handleBookmark}
                        className={`text-2xl ${bookmark ? 'text-yellow-500' : 'text-gray-300'}`}
                    >
                        ⭐
                    </button>
                </div>
            </div>
            
            {/* Content */}
            <div className="prose max-w-none mb-8">
                <MarkdownRenderer content={topic.content} />
            </div>
            
            {/* Code Examples */}
            {topic.code_snippets && topic.code_snippets.length > 0 && (
                <div className="mb-8">
                    <h2 className="text-xl font-bold mb-4">Code Examples</h2>
                    {topic.code_snippets.map(snippet => (
                        <CodeBlockViewer key={snippet.id} snippet={snippet} />
                    ))}
                </div>
            )}
            
            {/* Quiz */}
            {topic.quiz && (
                <div className="mb-8">
                    <h2 className="text-xl font-bold mb-4">Practice Quiz</h2>
                    {quizResults ? (
                        <div>
                            <QuizResultCard results={quizResults} />
                            <button onClick={() => setQuizResults(null)} className="btn btn-primary mt-4">
                                Retake Quiz
                            </button>
                        </div>
                    ) : (
                        <QuizCard quiz={topic.quiz} onSubmit={handleQuizSubmit} />
                    )}
                </div>
            )}
            
            {/* Notes */}
            <StudentNotesEditor topicId={topic.id} />
            
            {/* Navigation */}
            <TopicNavigation 
                course={course}
                currentTopic={topic}
            />
        </div>
    )
}
```

---

## State Management (Redux)

```jsx
// store/slices/courseAdminSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

const courseAdminSlice = createSlice({
    name: 'courseAdmin',
    initialState: {
        currentCourse: null,
        courses: [],
        selectedElement: null,
        loading: false,
        error: null
    },
    extraReducers: (builder) => {
        builder
            .addCase(fetchCourse.fulfilled, (state, action) => {
                state.currentCourse = action.payload
                state.loading = false
            })
            .addCase(updateCourse.fulfilled, (state, action) => {
                state.currentCourse = action.payload
            })
    }
})

export default courseAdminSlice.reducer
```

---

## API Service Example

```jsx
// services/courseAdminService.js
import { api } from './api'

export const courseAdminService = {
    getCourseDetail: (courseId) =>
        api.get(`/admin/courses/${courseId}/`).then(r => r.data),
    
    updateCourse: (courseId, data) =>
        api.put(`/admin/courses/${courseId}/`, data).then(r => r.data),
    
    publishCourse: (courseId) =>
        api.post(`/admin/courses/${courseId}/publish/`).then(r => r.data),
    
    generateOutline: (topic, level) =>
        api.post(`/admin/ai/generate-outline/`, { topic, level }).then(r => r.data),
    
    // ... more methods
}
```

---

## Next Steps

1. **Install Dependencies**:
   ```bash
   npm install @dnd-kit/core @dnd-kit/sortable axios react-markdown
   ```

2. **Create Base Components** (Button, Input, Card, etc.)

3. **Implement Rich Text Editor** (using Markdown + syntax highlighting)

4. **Build Course Builder UI** with all sub-components

5. **Build Student Learning UI** with engagement tracking

6. **Connect to Backend APIs** via services

7. **Test and Deploy to Vercel**

