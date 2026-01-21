// FILE: src/services/dashboard.service.js
// ============================================================================

import api from './api';

export const dashboardService = {
  /**
   * Get dashboard overview data
   * Mix of real and dummy data
   */
  getOverview: async () => {
    try {
      const response = await api.get('/api/dashboard/overview/');
      return response.data;
    } catch (error) {
      console.error('Dashboard overview error:', error);
      throw error;
    }
  },

  /**
   * Get recent notes (real data)
   */
  getRecentNotes: async () => {
    try {
      const response = await api.get('/api/dashboard/recent-notes/');
      return response.data;
    } catch (error) {
      console.error('Recent notes error:', error);
      throw error;
    }
  },

  /**
   * Get quick actions available to user
   */
  getQuickActions: async () => {
    try {
      const response = await api.get('/api/dashboard/quick-actions/');
      return response.data;
    } catch (error) {
      console.error('Quick actions error:', error);
      throw error;
    }
  },

  /**
   * Get today's plan/tasks
   * Currently dummy data - will be real when roadmaps module is ready
   */
  getTodayPlan: async () => {
    try {
      const response = await api.get('/api/dashboard/today-plan/');
      return response.data;
    } catch (error) {
      console.error('Today plan error:', error);
      throw error;
    }
  },

  /**
   * Update task completion status
   */
  updateTask: async (taskId, completed) => {
    try {
      const response = await api.post('/api/dashboard/today-plan/', {
        task_id: taskId,
        completed: completed
      });
      return response.data;
    } catch (error) {
      console.error('Update task error:', error);
      throw error;
    }
  },

  /**
   * Get active courses (DUMMY for now)
   * Replace with real API when courses module is ready
   */
  getActiveCourses: () => {
    // DUMMY DATA - Mark for replacement
    return Promise.resolve({
      success: true,
      is_dummy: true,
      data: [
        {
          id: 1,
          title: 'Machine Learning Fundamentals',
          progress: 65,
          nextLesson: 'Neural Networks Basics',
          color: 'blue'
        },
        {
          id: 2,
          title: 'Web Development Bootcamp',
          progress: 82,
          nextLesson: 'React Hooks',
          color: 'purple'
        },
        {
          id: 3,
          title: 'Data Structures & Algorithms',
          progress: 45,
          nextLesson: 'Binary Trees',
          color: 'green'
        },
      ]
    });
  },
};