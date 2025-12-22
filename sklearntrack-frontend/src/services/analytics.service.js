// FILE: src/services/analytics.service.js
// ============================================================================

import api from './api';
import { API_ENDPOINTS } from '@/utils/constants';

export const analyticsService = {
  // Get dashboard analytics
  getDashboard: async () => {
    const response = await api.get(API_ENDPOINTS.DASHBOARD);
    return response.data;
  },

  // Get study history
  getStudyHistory: async (days = 30) => {
    const response = await api.get(API_ENDPOINTS.STUDY_HISTORY, {
      params: { days },
    });
    return response.data;
  },

  // Get notifications
  getNotifications: async () => {
    const response = await api.get(API_ENDPOINTS.NOTIFICATIONS);
    return response.data;
  },

  // Mark all notifications as read
  markAllAsRead: async () => {
    const response = await api.post(API_ENDPOINTS.MARK_ALL_READ);
    return response.data;
  },
};

