// CourseMetadataPanel.jsx - Course Metadata & SEO Settings
import React from 'react'

export function CourseMetadataPanel({ course, onChange }) {
  const handleChange = (field, value) => {
    onChange({
      ...course,
      [field]: value
    })
  }

  const handleTagChange = (tags) => {
    handleChange('tags', tags.split(',').map(t => t.trim()).filter(t => t))
  }

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold text-white mb-6">Course Details</h2>

      {/* TITLE */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          Title
        </label>
        <input
          type="text"
          value={course.title || ''}
          onChange={(e) => handleChange('title', e.target.value)}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
        />
      </div>

      {/* DESCRIPTION */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          Description
        </label>
        <textarea
          value={course.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          rows={4}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
        />
      </div>

      {/* CATEGORY */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          Category
        </label>
        <select
          value={course.category || ''}
          onChange={(e) => handleChange('category', e.target.value)}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
        >
          <option value="">Select category</option>
          <option value="programming">Programming</option>
          <option value="data-science">Data Science</option>
          <option value="web-dev">Web Development</option>
          <option value="mobile">Mobile Development</option>
          <option value="devops">DevOps</option>
          <option value="ai-ml">AI & Machine Learning</option>
          <option value="other">Other</option>
        </select>
      </div>

      {/* DIFFICULTY */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          Difficulty
        </label>
        <select
          value={course.difficulty || ''}
          onChange={(e) => handleChange('difficulty', e.target.value)}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
        >
          <option value="beginner">Beginner</option>
          <option value="intermediate">Intermediate</option>
          <option value="advanced">Advanced</option>
        </select>
      </div>

      {/* ESTIMATED HOURS */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          Estimated Hours
        </label>
        <input
          type="number"
          value={course.estimated_hours || ''}
          onChange={(e) => handleChange('estimated_hours', parseInt(e.target.value))}
          min="1"
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
        />
      </div>

      {/* TAGS */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-300 mb-2">
          Tags (comma separated)
        </label>
        <input
          type="text"
          value={Array.isArray(course.tags) ? course.tags.join(', ') : ''}
          onChange={(e) => handleTagChange(e.target.value)}
          className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
          placeholder="python, backend, django, rest-api"
        />
      </div>

      {/* SEO SECTION */}
      <div className="pt-6 border-t border-gray-700">
        <h3 className="text-sm font-bold text-gray-300 mb-4">SEO Settings</h3>

        {/* META TITLE */}
        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Meta Title
          </label>
          <input
            type="text"
            value={course.meta_title || ''}
            onChange={(e) => handleChange('meta_title', e.target.value)}
            maxLength={60}
            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-sm"
          />
          <p className="text-xs text-gray-500 mt-1">
            {course.meta_title?.length || 0}/60 characters
          </p>
        </div>

        {/* META DESCRIPTION */}
        <div className="mb-4">
          <label className="block text-sm font-semibold text-gray-300 mb-2">
            Meta Description
          </label>
          <textarea
            value={course.meta_description || ''}
            onChange={(e) => handleChange('meta_description', e.target.value)}
            maxLength={160}
            rows={3}
            className="w-full bg-gray-700 text-white px-3 py-2 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-sm resize-none"
          />
          <p className="text-xs text-gray-500 mt-1">
            {course.meta_description?.length || 0}/160 characters
          </p>
        </div>
      </div>

      {/* STATUS */}
      <div className="mt-6 p-3 bg-blue-900/30 border border-blue-700/50 rounded">
        <p className="text-xs text-gray-300">
          <strong>Status:</strong> {course.status === 'published' ? '✅ Published' : '📝 Draft'}
        </p>
      </div>
    </div>
  )
}
