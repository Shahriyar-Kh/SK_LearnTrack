// src/services/profile.service.js

import api from './api';
import { API_ENDPOINTS } from '@/utils/constants';

export const profileService = {
  // Get profile
  getProfile: async () => {
    const response = await api.get(API_ENDPOINTS.PROFILE);
    return response.data;
  },

  // Update profile
  updateProfile: async (data) => {
    const response = await api.patch(API_ENDPOINTS.PROFILE, data);
    return response.data;
  },

  // Upload avatar
  uploadAvatar: async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await api.post(API_ENDPOINTS.PROFILE_AVATAR, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },

  // Update preferences
  updatePreferences: async (data) => {
    const response = await api.patch(API_ENDPOINTS.PROFILE_PREFERENCES, data);
    return response.data;
  },

  // Update notifications
  updateNotifications: async (data) => {
    const response = await api.patch(API_ENDPOINTS.PROFILE_NOTIFICATIONS, data);
    return response.data;
  },

  // Change password
  changePassword: async (data) => {
    const response = await api.post(API_ENDPOINTS.PROFILE_CHANGE_PASSWORD, data);
    return response.data;
  },

  // Get activity summary
  getActivitySummary: async () => {
    const response = await api.get(API_ENDPOINTS.PROFILE_ACTIVITY);
    return response.data;
  },
};