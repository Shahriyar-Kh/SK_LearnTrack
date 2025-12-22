// FILE: src/utils/constants.js
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  // Auth
  LOGIN: '/api/token/',
  REFRESH: '/api/token/refresh/',
  REGISTER: '/api/auth/register/',
  LOGOUT: '/api/auth/logout/',
  ME: '/api/auth/users/me/',
  UPDATE_PROFILE: '/api/auth/users/update_profile/',
  
  // Courses
  COURSES: '/api/courses/',
  COURSE_DETAIL: (slug) => `/api/courses/${slug}/`,
  COURSE_ENROLL: (slug) => `/api/courses/${slug}/enroll/`,
  COURSE_PROGRESS: (slug) => `/api/courses/${slug}/progress/`,
  ENROLLMENTS: '/api/courses/enrollments/',
  PERSONAL_COURSES: '/api/courses/personal/',
  
  // Notes
  NOTES: '/api/notes/',
  NOTE_DETAIL: (id) => `/api/notes/${id}/`,
  NOTE_HISTORY: (id) => `/api/notes/${id}/history/`,
  SNIPPETS: '/api/snippets/',
  SNIPPET_DETAIL: (id) => `/api/snippets/${id}/`,
  
  // Roadmaps
  ROADMAPS: '/api/roadmaps/',
  ROADMAP_DETAIL: (id) => `/api/roadmaps/${id}/`,
  MILESTONES: '/api/roadmaps/milestones/',
  TASKS: '/api/roadmaps/tasks/',
  
  // Analytics
  DASHBOARD: '/api/analytics/dashboard/',
  STUDY_HISTORY: '/api/analytics/study-history/',
  NOTIFICATIONS: '/api/analytics/notifications/',
  MARK_ALL_READ: '/api/analytics/notifications/mark_all_read/',
};

export const EDUCATION_LEVELS = [
  { value: 'high_school', label: 'High School' },
  { value: 'undergraduate', label: 'Undergraduate' },
  { value: 'graduate', label: 'Graduate' },
  { value: 'postgraduate', label: 'Postgraduate' },
  { value: 'professional', label: 'Professional' },
];

export const DIFFICULTY_LEVELS = [
  { value: 'beginner', label: 'Beginner', color: 'green' },
  { value: 'intermediate', label: 'Intermediate', color: 'yellow' },
  { value: 'advanced', label: 'Advanced', color: 'red' },
];

export const PRIORITY_LEVELS = [
  { value: 'low', label: 'Low', color: 'gray' },
  { value: 'medium', label: 'Medium', color: 'yellow' },
  { value: 'high', label: 'High', color: 'red' },
];
