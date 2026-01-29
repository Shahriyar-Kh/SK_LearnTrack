// CourseBuilder.jsx - 4-Column Course Builder with Drag-Drop Structure
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Save, Send, Eye, Copy, MoreVertical, Plus, AlertCircle } from 'lucide-react'
import { courseAdminService } from '../../services/courseAdminService'
import { toast } from 'react-hot-toast'
import { CourseMetadataPanel } from './panels/CourseMetadataPanel'
import { CourseStructureTree } from './panels/CourseStructureTree'
import { ContentEditor } from './panels/ContentEditor'
import { PreviewPanel } from './panels/PreviewPanel'

export function CourseBuilder() {
  const { courseId } = useParams()
  const [course, setCourse] = useState(null)
  const [selectedChapterId, setSelectedChapterId] = useState(null)
  const [selectedTopicId, setSelectedTopicId] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [publishing, setPublishing] = useState(false)
  const [showMenu, setShowMenu] = useState(false)

  useEffect(() => {
    loadCourse()
  }, [courseId])

  const loadCourse = async () => {
    try {
      setLoading(true)
      const data = await courseAdminService.getCourse(courseId)
      setCourse(data)
      // Auto-select first chapter/topic
      if (data.chapters?.length > 0) {
        setSelectedChapterId(data.chapters[0].id)
        if (data.chapters[0].topics?.length > 0) {
          setSelectedTopicId(data.chapters[0].topics[0].id)
        }
      }
    } catch (error) {
      toast.error('Failed to load course')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setSaving(true)
      await courseAdminService.updateCourse(courseId, {
        title: course.title,
        description: course.description,
        category: course.category,
        difficulty: course.difficulty,
        estimated_hours: course.estimated_hours,
        tags: course.tags,
        meta_title: course.meta_title,
        meta_description: course.meta_description
      })
      toast.success('Course saved successfully')
    } catch (error) {
      toast.error('Failed to save course')
    } finally {
      setSaving(false)
    }
  }

  const handlePublish = async () => {
    try {
      setPublishing(true)
      await courseAdminService.publishCourse(courseId, 'Course ready for students')
      setCourse({ ...course, status: 'published' })
      toast.success('Course published successfully!')
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to publish course')
    } finally {
      setPublishing(false)
    }
  }

  const handleDuplicate = async () => {
    const newTitle = prompt('New course name:', `${course.title} (Copy)`)
    if (!newTitle) return
    try {
      await courseAdminService.duplicateCourse(courseId, newTitle)
      toast.success('Course duplicated successfully')
    } catch {
      toast.error('Failed to duplicate course')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-400">Loading course...</p>
        </div>
      </div>
    )
  }

  if (!course) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-900">
        <div className="text-center">
          <AlertCircle size={48} className="text-red-500 mx-auto mb-4" />
          <p className="text-gray-400">Course not found</p>
        </div>
      </div>
    )
  }

  const selectedTopic = selectedChapterId && selectedTopicId
    ? course.chapters?.find(c => c.id === selectedChapterId)?.topics?.find(t => t.id === selectedTopicId)
    : null

  return (
    <div className="flex flex-col h-screen bg-gray-900">
      {/* HEADER */}
      <div className="bg-gray-950 border-b border-gray-800 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">{course.title}</h1>
            <p className="text-gray-400 text-sm">
              {course.status === 'published' ? '✅ Published' : '📝 Draft'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              <Save size={18} />
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={handlePublish}
              disabled={publishing || course.status === 'published'}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
              <Send size={18} />
              {publishing ? 'Publishing...' : 'Publish'}
            </button>
            <div className="relative">
              <button
                onClick={() => setShowMenu(!showMenu)}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
              >
                <MoreVertical size={18} />
              </button>
              {showMenu && (
                <div className="absolute right-0 mt-2 bg-gray-800 border border-gray-700 rounded-lg shadow-xl z-10">
                  <button
                    onClick={() => {
                      handleDuplicate()
                      setShowMenu(false)
                    }}
                    className="flex items-center gap-2 w-full px-4 py-2 text-gray-300 hover:bg-gray-700 text-sm"
                  >
                    <Copy size={16} />
                    Duplicate
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* 4-COLUMN LAYOUT */}
      <div className="flex flex-1 overflow-hidden gap-1 bg-gray-900 p-2">
        {/* COLUMN 1: METADATA (25%) */}
        <div className="w-1/4 bg-gray-800 rounded-lg border border-gray-700 overflow-auto">
          <CourseMetadataPanel 
            course={course} 
            onChange={setCourse}
          />
        </div>

        {/* COLUMN 2: STRUCTURE (25%) */}
        <div className="w-1/4 bg-gray-800 rounded-lg border border-gray-700 overflow-auto">
          <CourseStructureTree
            course={course}
            selectedChapterId={selectedChapterId}
            selectedTopicId={selectedTopicId}
            onSelectChapter={setSelectedChapterId}
            onSelectTopic={setSelectedTopicId}
            onCourseChange={setCourse}
          />
        </div>

        {/* COLUMN 3: CONTENT EDITOR (25%) */}
        <div className="w-1/4 bg-gray-800 rounded-lg border border-gray-700 overflow-auto">
          {selectedTopic ? (
            <ContentEditor
              topic={selectedTopic}
              courseId={courseId}
              chapterId={selectedChapterId}
              onTopicChange={(updatedTopic) => {
                setCourse({
                  ...course,
                  chapters: course.chapters.map(ch =>
                    ch.id === selectedChapterId
                      ? {
                          ...ch,
                          topics: ch.topics.map(t =>
                            t.id === selectedTopicId ? updatedTopic : t
                          )
                        }
                      : ch
                  )
                })
              }}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full p-4 text-gray-400">
              <Plus size={32} className="mb-2 opacity-50" />
              <p>Select a topic to edit</p>
            </div>
          )}
        </div>

        {/* COLUMN 4: PREVIEW (25%) */}
        <div className="w-1/4 bg-gray-800 rounded-lg border border-gray-700 overflow-auto">
          {selectedTopic ? (
            <PreviewPanel topic={selectedTopic} />
          ) : (
            <div className="flex flex-col items-center justify-center h-full p-4 text-gray-400">
              <Eye size={32} className="mb-2 opacity-50" />
              <p>Preview will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
