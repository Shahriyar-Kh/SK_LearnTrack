// ContentEditor.jsx - Rich Markdown Content Editor
import React, { useState } from 'react'
import { courseAdminService } from '../../../services/courseAdminService'
import { toast } from 'react-hot-toast'
import { Clock, Zap, BookMarked } from 'lucide-react'

export function ContentEditor({ topic, courseId, chapterId, onTopicChange }) {
  const [content, setContent] = useState(topic.content || '')
  const [title, setTitle] = useState(topic.title || '')
  const [description, setDescription] = useState(topic.description || '')
  const [estimatedMinutes, setEstimatedMinutes] = useState(topic.estimated_minutes || 15)
  const [difficulty, setDifficulty] = useState(topic.difficulty || 'beginner')
  const [keyConcepts, setKeyConcepts] = useState(
    Array.isArray(topic.key_concepts) ? topic.key_concepts.join(', ') : ''
  )
  const [saving, setSaving] = useState(false)

  const handleSave = async () => {
    try {
      setSaving(true)
      const updatedTopic = await courseAdminService.updateTopic(
        courseId,
        chapterId,
        topic.id,
        {
          title,
          description,
          content,
          estimated_minutes: estimatedMinutes,
          difficulty,
          key_concepts: keyConcepts
            .split(',')
            .map(k => k.trim())
            .filter(k => k)
        }
      )
      onTopicChange(updatedTopic)
      toast.success('Topic saved')
    } catch {
      toast.error('Failed to save topic')
    } finally {
      setSaving(false)
    }
  }

  const insertMarkdown = (before, after = '') => {
    const textarea = document.getElementById('content-editor')
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const selectedText = content.substring(start, end)
    const newContent =
      content.substring(0, start) +
      before +
      selectedText +
      after +
      content.substring(end)
    setContent(newContent)
  }

  return (
    <div className="p-4 h-full flex flex-col">
      <h2 className="text-lg font-bold text-white mb-4">Topic Content</h2>

      {/* TITLE & METADATA */}
      <div className="space-y-3 mb-4">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-sm font-semibold"
          placeholder="Topic title"
        />

        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Brief description..."
          rows={2}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-xs resize-none"
        />

        {/* METADATA ROW */}
        <div className="grid grid-cols-3 gap-2">
          <div>
            <label className="text-xs text-gray-400">Minutes</label>
            <div className="flex items-center gap-1 bg-gray-700 px-2 py-1 rounded border border-gray-600">
              <Clock size={14} className="text-gray-400" />
              <input
                type="number"
                value={estimatedMinutes}
                onChange={(e) => setEstimatedMinutes(parseInt(e.target.value))}
                min="1"
                className="bg-transparent text-white text-xs w-8 focus:outline-none"
              />
            </div>
          </div>
          <div>
            <label className="text-xs text-gray-400">Difficulty</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 focus:outline-none text-xs"
            >
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-400">Concepts</label>
            <input
              type="text"
              value={keyConcepts}
              onChange={(e) => setKeyConcepts(e.target.value)}
              placeholder="comma,separated"
              className="w-full bg-gray-700 text-white px-2 py-1 rounded border border-gray-600 focus:outline-none text-xs"
            />
          </div>
        </div>
      </div>

      {/* MARKDOWN TOOLBAR */}
      <div className="flex flex-wrap gap-1 mb-3 pb-3 border-b border-gray-700">
        <button
          onClick={() => insertMarkdown('# ', '')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
        >
          H1
        </button>
        <button
          onClick={() => insertMarkdown('## ', '')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
        >
          H2
        </button>
        <button
          onClick={() => insertMarkdown('**', '**')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs font-bold"
        >
          B
        </button>
        <button
          onClick={() => insertMarkdown('*', '*')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs italic"
        >
          I
        </button>
        <button
          onClick={() => insertMarkdown('- ', '')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
        >
          List
        </button>
        <button
          onClick={() => insertMarkdown('```\n', '\n```')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
        >
          Code
        </button>
        <button
          onClick={() => insertMarkdown('> ', '')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
        >
          Quote
        </button>
        <button
          onClick={() => insertMarkdown('[', '](url)')}
          className="px-2 py-1 bg-gray-700 hover:bg-gray-600 text-white rounded text-xs"
        >
          Link
        </button>
      </div>

      {/* CONTENT EDITOR */}
      <textarea
        id="content-editor"
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write your content in Markdown...

# Main Topic
Introduce the topic here.

## Subtopic
Explain key concepts.

### Key Points
- Point 1
- Point 2
- Point 3

**Important:** Code blocks work too:
\`\`\`python
def hello():
    print('World')
\`\`\`"
        className="flex-1 bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none font-mono text-xs resize-none"
      />

      {/* SAVE BUTTON */}
      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-3 w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-semibold transition-colors disabled:opacity-50"
      >
        {saving ? 'Saving...' : 'Save Content'}
      </button>
    </div>
  )
}
