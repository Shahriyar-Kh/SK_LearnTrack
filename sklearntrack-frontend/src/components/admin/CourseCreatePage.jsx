// CourseCreatePage.jsx - Create New Course Page
import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { courseAdminService } from '../../services/courseAdminService'
import { toast } from 'react-hot-toast'
import { ArrowLeft } from 'lucide-react'

export function CourseCreatePage() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'programming',
    difficulty: 'beginner',
    estimated_hours: 10,
    tags: '',
    meta_title: '',
    meta_description: ''
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: name === 'estimated_hours' ? parseInt(value) : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.title.trim()) {
      toast.error('Course title is required')
      return
    }

    try {
      setLoading(true)
      const tags = formData.tags
        .split(',')
        .map(t => t.trim())
        .filter(t => t)
      
      const course = await courseAdminService.createCourse({
        ...formData,
        tags
      })
      
      toast.success('Course created successfully!')
      navigate(`/admin/courses/${course.id}`)
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create course')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-2xl mx-auto">
        {/* HEADER */}
        <button
          onClick={() => navigate('/admin/courses')}
          className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-8"
        >
          <ArrowLeft size={18} />
          Back to Courses
        </button>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Create New Course</h1>
          <p className="text-gray-400">Set up your course basics</p>
        </div>

        {/* FORM */}
        <form onSubmit={handleSubmit} className="bg-gray-800 rounded-lg border border-gray-700 p-8 space-y-6">
          {/* TITLE */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Course Title *
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              placeholder="e.g., Advanced Python Backend Development"
              className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none text-lg"
            />
          </div>

          {/* DESCRIPTION */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Describe what students will learn in this course..."
              rows={4}
              className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
            />
          </div>

          {/* GRID: CATEGORY, DIFFICULTY, HOURS */}
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Category
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleChange}
                className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="programming">Programming</option>
                <option value="data-science">Data Science</option>
                <option value="web-dev">Web Development</option>
                <option value="mobile">Mobile Development</option>
                <option value="devops">DevOps</option>
                <option value="ai-ml">AI & Machine Learning</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Difficulty
              </label>
              <select
                name="difficulty"
                value={formData.difficulty}
                onChange={handleChange}
                className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-300 mb-2">
                Estimated Hours
              </label>
              <input
                type="number"
                name="estimated_hours"
                value={formData.estimated_hours}
                onChange={handleChange}
                min="1"
                className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          {/* TAGS */}
          <div>
            <label className="block text-sm font-semibold text-gray-300 mb-2">
              Tags (comma separated)
            </label>
            <input
              type="text"
              name="tags"
              value={formData.tags}
              onChange={handleChange}
              placeholder="python, backend, django, api"
              className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
            />
          </div>

          {/* SEO SECTION */}
          <div className="pt-6 border-t border-gray-700">
            <h3 className="text-lg font-bold text-white mb-4">SEO Settings</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Meta Title
                </label>
                <input
                  type="text"
                  name="meta_title"
                  value={formData.meta_title}
                  onChange={handleChange}
                  maxLength={60}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.meta_title.length}/60 characters
                </p>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-300 mb-2">
                  Meta Description
                </label>
                <textarea
                  name="meta_description"
                  value={formData.meta_description}
                  onChange={handleChange}
                  maxLength={160}
                  rows={3}
                  className="w-full bg-gray-700 text-white px-4 py-3 rounded border border-gray-600 focus:border-blue-500 focus:outline-none resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">
                  {formData.meta_description.length}/160 characters
                </p>
              </div>
            </div>
          </div>

          {/* BUTTONS */}
          <div className="flex gap-4 pt-6 border-t border-gray-700">
            <button
              type="button"
              onClick={() => navigate('/admin/courses')}
              className="flex-1 px-6 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition-colors disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
