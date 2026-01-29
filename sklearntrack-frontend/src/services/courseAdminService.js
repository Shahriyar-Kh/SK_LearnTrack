// courseAdminService.js - Admin Course Management API Service
import api from './api'

export const courseAdminService = {
  // ============================================================================
  // COURSES
  // ============================================================================
  
  /**
   * Get all courses with optional filters
   * @param {Object} params - Query parameters (status, category, search, page)
   */
  async getCourses(params = {}) {
    const response = await api.get('/api/courses/admin/courses/', { params })
    return response.data
  },

  /**
   * Get single course with full structure
   * @param {number} courseId - Course ID
   */
  async getCourse(courseId) {
    const response = await api.get(`/api/courses/admin/courses/${courseId}/`)
    return response.data
  },

  /**
   * Create new course
   * @param {Object} courseData - Course metadata
   */
  async createCourse(courseData) {
    const response = await api.post('/api/courses/admin/courses/', courseData)
    return response.data
  },

  /**
   * Update course metadata
   * @param {number} courseId - Course ID
   * @param {Object} courseData - Updated data
   */
  async updateCourse(courseId, courseData) {
    const response = await api.patch(`/api/courses/admin/courses/${courseId}/`, courseData)
    return response.data
  },

  /**
   * Delete course (soft delete)
   * @param {number} courseId - Course ID
   */
  async deleteCourse(courseId) {
    await api.delete(`/api/courses/admin/courses/${courseId}/`)
  },

  /**
   * Publish course
   * @param {number} courseId - Course ID
   * @param {string} changeSummary - What changed
   */
  async publishCourse(courseId, changeSummary = 'Course published') {
    const response = await api.post(`/api/courses/admin/courses/${courseId}/publish/`, {
      change_summary: changeSummary
    })
    return response.data
  },

  /**
   * Unpublish course
   * @param {number} courseId - Course ID
   */
  async unpublishCourse(courseId) {
    const response = await api.post(`/api/courses/admin/courses/${courseId}/unpublish/`, {})
    return response.data
  },

  /**
   * Get preview (student view)
   * @param {number} courseId - Course ID
   */
  async previewCourse(courseId) {
    const response = await api.get(`/api/courses/admin/courses/${courseId}/preview/`)
    return response.data
  },

  /**
   * Duplicate course
   * @param {number} courseId - Course ID
   * @param {string} newTitle - Title for duplicate
   */
  async duplicateCourse(courseId, newTitle) {
    const response = await api.post(`/api/courses/admin/courses/${courseId}/duplicate/`, {
      title: newTitle
    })
    return response.data
  },

  /**
   * Get version history
   * @param {number} courseId - Course ID
   */
  async getVersionHistory(courseId) {
    const response = await api.get(`/api/courses/admin/courses/${courseId}/version-history/`)
    return response.data
  },

  /**
   * Get audit log
   * @param {number} courseId - Course ID
   */
  async getAuditLog(courseId) {
    const response = await api.get(`/api/courses/admin/courses/${courseId}/audit-log/`)
    return response.data
  },

  // ============================================================================
  // CHAPTERS
  // ============================================================================

  /**
   * Create chapter
   * @param {number} courseId - Course ID
   * @param {Object} chapterData - Chapter details
   */
  async createChapter(courseId, chapterData) {
    const response = await api.post(
      `/api/courses/admin/courses/${courseId}/chapters/`,
      chapterData
    )
    return response.data
  },

  /**
   * Update chapter
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {Object} chapterData - Updated data
   */
  async updateChapter(courseId, chapterId, chapterData) {
    const response = await api.patch(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/`,
      chapterData
    )
    return response.data
  },

  /**
   * Delete chapter
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   */
  async deleteChapter(courseId, chapterId) {
    await api.delete(`/api/courses/admin/courses/${courseId}/chapters/${chapterId}/`)
  },

  // ============================================================================
  // TOPICS
  // ============================================================================

  /**
   * Create topic
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {Object} topicData - Topic details
   */
  async createTopic(courseId, chapterId, topicData) {
    const response = await api.post(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/topics/`,
      topicData
    )
    return response.data
  },

  /**
   * Update topic
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {number} topicId - Topic ID
   * @param {Object} topicData - Updated data
   */
  async updateTopic(courseId, chapterId, topicId, topicData) {
    const response = await api.patch(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/topics/${topicId}/`,
      topicData
    )
    return response.data
  },

  /**
   * Delete topic
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {number} topicId - Topic ID
   */
  async deleteTopic(courseId, chapterId, topicId) {
    await api.delete(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/topics/${topicId}/`
    )
  },

  /**
   * Reorder topics
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {Array} ordering - Array of topic IDs in new order
   */
  async reorderTopics(courseId, chapterId, ordering) {
    const response = await api.post(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/reorder/`,
      { ordering }
    )
    return response.data
  },

  // ============================================================================
  // QUIZ
  // ============================================================================

  /**
   * Get or create quiz for topic
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {number} topicId - Topic ID
   */
  async getTopicQuiz(courseId, chapterId, topicId) {
    const response = await api.get(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/topics/${topicId}/quiz/`
    )
    return response.data
  },

  /**
   * Create or update quiz
   * @param {number} courseId - Course ID
   * @param {number} chapterId - Chapter ID
   * @param {number} topicId - Topic ID
   * @param {Object} quizData - Quiz details with questions
   */
  async saveQuiz(courseId, chapterId, topicId, quizData) {
    const response = await api.post(
      `/api/courses/admin/courses/${courseId}/chapters/${chapterId}/topics/${topicId}/quiz/`,
      quizData
    )
    return response.data
  },

  // ============================================================================
  // FILE UPLOADS
  // ============================================================================

  /**
   * Upload image/asset
   * @param {number} topicId - Topic ID
   * @param {File} file - File to upload
   * @param {string} assetType - 'image', 'pdf', 'code', etc
   */
  async uploadAsset(topicId, file, assetType = 'image') {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('asset_type', assetType)
    formData.append('title', file.name)

    const response = await api.post(
      `/courses/topics/${topicId}/assets/`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' }
      }
    )
    return response.data
  },

  /**
   * Delete asset
   * @param {number} assetId - Asset ID
   */
  async deleteAsset(assetId) {
    await api.delete(`/courses/assets/${assetId}/`)
  }
}
