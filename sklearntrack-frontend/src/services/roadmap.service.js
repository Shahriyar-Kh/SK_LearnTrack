// FILE: src/services/roadmap.service.js
// ============================================================================

import api from './api';
import { API_ENDPOINTS } from '@/utils/constants';

export const roadmapService = {
  // Get all roadmaps
  getRoadmaps: async () => {
    const response = await api.get(API_ENDPOINTS.ROADMAPS);
    return response.data;
  },

  // Get roadmap detail
  getRoadmapDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.ROADMAP_DETAIL(id));
    return response.data;
  },

  // Create roadmap
  createRoadmap: async (roadmapData) => {
    const response = await api.post(API_ENDPOINTS.ROADMAPS, roadmapData);
    return response.data;
  },

  // Update roadmap
  updateRoadmap: async (id, roadmapData) => {
    const response = await api.patch(API_ENDPOINTS.ROADMAP_DETAIL(id), roadmapData);
    return response.data;
  },

  // Delete roadmap
  deleteRoadmap: async (id) => {
    const response = await api.delete(API_ENDPOINTS.ROADMAP_DETAIL(id));
    return response.data;
  },

  // Milestones
  getMilestones: async () => {
    const response = await api.get(API_ENDPOINTS.MILESTONES);
    return response.data;
  },

  createMilestone: async (milestoneData) => {
    const response = await api.post(API_ENDPOINTS.MILESTONES, milestoneData);
    return response.data;
  },

  // Tasks
  getTasks: async () => {
    const response = await api.get(API_ENDPOINTS.TASKS);
    return response.data;
  },

  createTask: async (taskData) => {
    const response = await api.post(API_ENDPOINTS.TASKS, taskData);
    return response.data;
  },

  updateTask: async (id, taskData) => {
    const response = await api.patch(`${API_ENDPOINTS.TASKS}${id}/`, taskData);
    return response.data;
  },
};

