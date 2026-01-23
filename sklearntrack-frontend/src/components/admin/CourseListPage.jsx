// CourseListPage.jsx - Beautiful Admin Course List with Search & Filters
import React, { useState, useEffect } from 'react'
import { Plus, Search, Filter, BookOpen, Clock, Eye, Copy, Trash2, Play } from 'lucide-react'
import { courseAdminService } from '../../services/courseAdminService'
import { toast } from 'react-hot-toast'

export function CourseListPage() {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')

  useEffect(() => {
    loadCourses()
  }, [statusFilter])

  const loadCourses = async () => {
    try {
      setLoading(true)
      const params = statusFilter !== 'all' ? { status: statusFilter } : {}
      if (search) params.search = search
      const data = await courseAdminService.getCourses(params)
      setCourses(Array.isArray(data) ? data : data.results || [])
    } catch (error) {
      toast.error('Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (courseId) => {
    if (!confirm('Are you sure? This will archive the course.')) return
    try {
      await courseAdminService.deleteCourse(courseId)
      setCourses(courses.filter(c => c.id !== courseId))
      toast.success('Course archived')
    } catch {
      toast.error('Failed to delete course')
    }
  }

  const handleDuplicate = async (course) => {
    try {
      const newTitle = prompt('New course name:', `${course.title} (Copy)`)
      if (!newTitle) return
      await courseAdminService.duplicateCourse(course.id, newTitle)
      toast.success('Course duplicated')
      loadCourses()
    } catch {
      toast.error('Failed to duplicate course')
    }
  }

  const getStatusBadge = (status) => {
    const styles = {
      draft: 'bg-gray-700 text-gray-100',
      published: 'bg-green-700 text-green-100',
      archived: 'bg-red-700 text-red-100'
    }
    return styles[status] || 'bg-gray-700 text-gray-100'
  }

  const getDifficultyColor = (difficulty) => {
    const colors = {
      beginner: 'text-green-400',
      intermediate: 'text-yellow-400',
      advanced: 'text-red-400'
    }
    return colors[difficulty] || 'text-gray-400'
  }

  return (
    <div className="min-h-screen bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* HEADER */}
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">My Courses</h1>
            <p className="text-gray-400">Create and manage your learning content</p>
          </div>
          <a
            href="/admin/courses/create"
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-all"
          >
            <Plus size={20} />
            Create Course
          </a>
        </div>

        {/* SEARCH & FILTERS */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="md:col-span-2 relative">
            <Search className="absolute left-3 top-3.5 text-gray-500" size={20} />
            <input
              type="text"
              placeholder="Search courses..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyUp={() => loadCourses()}
              className="w-full bg-gray-800 text-white pl-10 pr-4 py-3 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-gray-800 text-white px-4 py-3 rounded-lg border border-gray-700 focus:border-blue-500 focus:outline-none"
          >
            <option value="all">All Status</option>
            <option value="draft">Draft</option>
            <option value="published">Published</option>
            <option value="archived">Archived</option>
          </select>
        </div>

        {/* COURSES GRID */}
        {loading ? (
          <div className="flex justify-center items-center h-96">
            <div className="text-gray-400">Loading courses...</div>
          </div>
        ) : courses.length === 0 ? (
          <div className="text-center py-16">
            <BookOpen size={48} className="mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400 text-lg">No courses yet</p>
            <a
              href="/admin/courses/create"
              className="inline-flex items-center gap-2 mt-4 text-blue-400 hover:text-blue-300"
            >
              <Plus size={18} />
              Create your first course
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <div
                key={course.id}
                className="bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 overflow-hidden transition-all group"
              >
                {/* IMAGE */}
                <div className="h-40 bg-gradient-to-br from-blue-600 to-purple-600 relative overflow-hidden">
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-black/50 transition-opacity flex items-center justify-center gap-3">
                    <a
                      href={`/admin/courses/${course.id}`}
                      className="p-2 bg-white/10 hover:bg-white/20 rounded-lg"
                      title="Edit"
                    >
                      <Eye size={20} className="text-white" />
                    </a>
                    <button
                      onClick={() => handleDuplicate(course)}
                      className="p-2 bg-white/10 hover:bg-white/20 rounded-lg"
                      title="Duplicate"
                    >
                      <Copy size={20} className="text-white" />
                    </button>
                  </div>
                </div>

                {/* CONTENT */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-bold text-white text-lg flex-1 line-clamp-2">
                      {course.title}
                    </h3>
                    <span className={`px-2 py-1 rounded text-xs font-semibold whitespace-nowrap ml-2 ${getStatusBadge(course.status)}`}>
                      {course.status}
                    </span>
                  </div>

                  <p className="text-gray-400 text-sm mb-4 line-clamp-2">
                    {course.description}
                  </p>

                  {/* METADATA */}
                  <div className="flex flex-wrap gap-2 mb-4 text-xs">
                    <span className={`font-semibold ${getDifficultyColor(course.difficulty)}`}>
                      {course.difficulty}
                    </span>
                    <span className="text-gray-500">•</span>
                    <span className="text-gray-400">{course.category}</span>
                    <span className="text-gray-500">•</span>
                    <span className="flex items-center gap-1 text-gray-400">
                      <Clock size={14} /> {course.estimated_hours}h
                    </span>
                  </div>

                  {/* ACTIONS */}
                  <div className="flex gap-2">
                    <a
                      href={`/admin/courses/${course.id}`}
                      className="flex-1 flex items-center justify-center gap-1 bg-blue-600 hover:bg-blue-700 text-white py-2 rounded font-semibold transition-colors"
                    >
                      <Play size={16} />
                      Edit
                    </a>
                    <button
                      onClick={() => handleDelete(course.id)}
                      className="p-2 bg-gray-700 hover:bg-red-700 text-gray-300 hover:text-white rounded transition-colors"
                      title="Delete"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
