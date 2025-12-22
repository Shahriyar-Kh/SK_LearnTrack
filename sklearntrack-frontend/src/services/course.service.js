// FILE: src/services/course.service.js
// ============================================================================

import api from './api';
import { API_ENDPOINTS } from '@/utils/constants';

export const courseService = {
  // Get all courses
  getCourses: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.COURSES, { params });
    return response.data;
  },

  // Get course details
  getCourseDetail: async (slug) => {
    const response = await api.get(API_ENDPOINTS.COURSE_DETAIL(slug));
    return response.data;
  },

  // Enroll in course
  enrollCourse: async (slug) => {
    const response = await api.post(API_ENDPOINTS.COURSE_ENROLL(slug));
    return response.data;
  },

  // Get course progress
  getCourseProgress: async (slug) => {
    const response = await api.get(API_ENDPOINTS.COURSE_PROGRESS(slug));
    return response.data;
  },

  // Get user enrollments
  getEnrollments: async () => {
    const response = await api.get(API_ENDPOINTS.ENROLLMENTS);
    return response.data;
  },

  // Personal courses
  getPersonalCourses: async () => {
    const response = await api.get(API_ENDPOINTS.PERSONAL_COURSES);
    return response.data;
  },

  createPersonalCourse: async (courseData) => {
    const response = await api.post(API_ENDPOINTS.PERSONAL_COURSES, courseData);
    return response.data;
  },

  updatePersonalCourse: async (id, courseData) => {
    const response = await api.put(`${API_ENDPOINTS.PERSONAL_COURSES}${id}/`, courseData);
    return response.data;
  },

  deletePersonalCourse: async (id) => {
    const response = await api.delete(`${API_ENDPOINTS.PERSONAL_COURSES}${id}/`);
    return response.data;
  },
};