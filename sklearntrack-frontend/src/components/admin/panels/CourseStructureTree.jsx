// CourseStructureTree.jsx - Drag-Drop Course Structure Editor
import React, { useState } from 'react'
import { Plus, ChevronDown, ChevronRight, Trash2, Edit2 } from 'lucide-react'
import { courseAdminService } from '../../../services/courseAdminService'
import { toast } from 'react-hot-toast'

export function CourseStructureTree({
  course,
  selectedChapterId,
  selectedTopicId,
  onSelectChapter,
  onSelectTopic,
  onCourseChange
}) {
  const [expandedChapters, setExpandedChapters] = useState(
    new Set(course.chapters?.map(c => c.id) || [])
  )
  const [newChapterTitle, setNewChapterTitle] = useState('')
  const [newTopicTitle, setNewTopicTitle] = useState('')
  const [newTopicChapterId, setNewTopicChapterId] = useState(null)

  const toggleChapter = (chapterId) => {
    const newExpanded = new Set(expandedChapters)
    if (newExpanded.has(chapterId)) {
      newExpanded.delete(chapterId)
    } else {
      newExpanded.add(chapterId)
    }
    setExpandedChapters(newExpanded)
  }

  const addChapter = async () => {
    if (!newChapterTitle.trim()) return
    try {
      const chapter = await courseAdminService.createChapter(course.id, {
        title: newChapterTitle,
        description: '',
        order_index: (course.chapters?.length || 0) + 1
      })
      onCourseChange({
        ...course,
        chapters: [...(course.chapters || []), chapter]
      })
      setNewChapterTitle('')
      setExpandedChapters(new Set([...expandedChapters, chapter.id]))
      toast.success('Chapter added')
    } catch {
      toast.error('Failed to add chapter')
    }
  }

  const addTopic = async (chapterId) => {
    if (!newTopicTitle.trim()) return
    try {
      const topic = await courseAdminService.createTopic(course.id, chapterId, {
        title: newTopicTitle,
        description: '',
        content: '',
        estimated_minutes: 15,
        difficulty: 'beginner',
        key_concepts: [],
        order_index: course.chapters
          ?.find(c => c.id === chapterId)?.topics?.length || 1
      })
      onCourseChange({
        ...course,
        chapters: course.chapters.map(c =>
          c.id === chapterId
            ? { ...c, topics: [...(c.topics || []), topic] }
            : c
        )
      })
      setNewTopicTitle('')
      setNewTopicChapterId(null)
      onSelectTopic(topic.id)
      toast.success('Topic added')
    } catch {
      toast.error('Failed to add topic')
    }
  }

  const deleteChapter = async (chapterId) => {
    if (!confirm('Delete this chapter? All topics will be removed.')) return
    try {
      await courseAdminService.deleteChapter(course.id, chapterId)
      onCourseChange({
        ...course,
        chapters: course.chapters.filter(c => c.id !== chapterId)
      })
      toast.success('Chapter deleted')
    } catch {
      toast.error('Failed to delete chapter')
    }
  }

  const deleteTopic = async (chapterId, topicId) => {
    if (!confirm('Delete this topic?')) return
    try {
      await courseAdminService.deleteTopic(course.id, chapterId, topicId)
      onCourseChange({
        ...course,
        chapters: course.chapters.map(c =>
          c.id === chapterId
            ? { ...c, topics: c.topics.filter(t => t.id !== topicId) }
            : c
        )
      })
      if (selectedTopicId === topicId) {
        onSelectTopic(null)
      }
      toast.success('Topic deleted')
    } catch {
      toast.error('Failed to delete topic')
    }
  }

  return (
    <div className="p-4">
      <h2 className="text-lg font-bold text-white mb-4">Structure</h2>

      {/* ADD CHAPTER */}
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={newChapterTitle}
          onChange={(e) => setNewChapterTitle(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addChapter()}
          placeholder="New chapter..."
          className="flex-1 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
        />
        <button
          onClick={addChapter}
          className="p-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
        >
          <Plus size={16} />
        </button>
      </div>

      {/* CHAPTERS & TOPICS */}
      <div className="space-y-2">
        {course.chapters?.map((chapter) => (
          <div key={chapter.id}>
            {/* CHAPTER */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => toggleChapter(chapter.id)}
                className="p-1 hover:bg-gray-700 rounded transition-colors"
              >
                {expandedChapters.has(chapter.id) ? (
                  <ChevronDown size={16} className="text-gray-400" />
                ) : (
                  <ChevronRight size={16} className="text-gray-400" />
                )}
              </button>
              <div
                onClick={() => onSelectChapter(chapter.id)}
                className={`flex-1 px-3 py-2 rounded cursor-pointer transition-colors text-sm ${
                  selectedChapterId === chapter.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:bg-gray-700'
                }`}
              >
                <span className="font-semibold">📚 {chapter.title}</span>
              </div>
              <button
                onClick={() => deleteChapter(chapter.id)}
                className="p-1 text-gray-500 hover:text-red-400 transition-colors"
              >
                <Trash2 size={14} />
              </button>
            </div>

            {/* TOPICS */}
            {expandedChapters.has(chapter.id) && (
              <div className="ml-6 mt-2 space-y-2 border-l-2 border-gray-700 pl-2">
                {chapter.topics?.map((topic) => (
                  <div
                    key={topic.id}
                    onClick={() => {
                      onSelectChapter(chapter.id)
                      onSelectTopic(topic.id)
                    }}
                    className={`flex items-center gap-2 px-3 py-2 rounded cursor-pointer transition-colors text-sm ${
                      selectedTopicId === topic.id
                        ? 'bg-blue-600 text-white'
                        : 'text-gray-300 hover:bg-gray-700'
                    }`}
                  >
                    <span className="flex-1 line-clamp-1">📄 {topic.title}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        deleteTopic(chapter.id, topic.id)
                      }}
                      className="p-1 text-gray-500 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                ))}

                {/* ADD TOPIC */}
                {newTopicChapterId === chapter.id ? (
                  <div className="flex gap-2 ml-2">
                    <input
                      type="text"
                      value={newTopicTitle}
                      onChange={(e) => setNewTopicTitle(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && addTopic(chapter.id)}
                      autoFocus
                      placeholder="New topic..."
                      className="flex-1 bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-xs"
                    />
                    <button
                      onClick={() => addTopic(chapter.id)}
                      className="p-1 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                    >
                      <Plus size={14} />
                    </button>
                  </div>
                ) : (
                  <button
                    onClick={() => {
                      setNewTopicChapterId(chapter.id)
                      setNewTopicTitle('')
                    }}
                    className="flex items-center gap-2 w-full px-3 py-2 text-gray-400 hover:text-blue-400 text-sm transition-colors"
                  >
                    <Plus size={14} />
                    Add topic
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* EMPTY STATE */}
      {!course.chapters || course.chapters.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p className="text-sm">No chapters yet</p>
          <p className="text-xs">Add one to get started</p>
        </div>
      )}
    </div>
  )
}
