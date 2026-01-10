// FILE: src/utils/constants.js
// ============================================================================

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export const API_ENDPOINTS = {
  // Auth
  LOGIN: 'token/',
  REFRESH: 'token/refresh/',
  REGISTER: 'auth/register/',
  LOGOUT: 'auth/logout/',
  ME: 'auth/users/me/',
  UPDATE_PROFILE: 'auth/users/update_profile/',

  // Courses
  COURSES: 'courses/',
  COURSE_DETAIL: (slug) => `courses/${slug}/`,
  COURSE_ENROLL: (slug) => `courses/${slug}/enroll/`,
  COURSE_PROGRESS: (slug) => `courses/${slug}/progress/`,
  ENROLLMENTS: 'courses/enrollments/',
  PERSONAL_COURSES: 'courses/personal/',

  // Notes
  NOTES: 'notes/',
  NOTE_DETAIL: (id) => `notes/${id}/`,
  NOTE_HISTORY: (id) => `notes/${id}/versions/`,
  NOTE_RESTORE_VERSION: (id) => `notes/${id}/restore_version/`,
  NOTE_DUPLICATE: (id) => `notes/${id}/duplicate/`,
  NOTE_AI_ACTION: 'notes/ai_action/',
  NOTE_APPROVE_AI: 'notes/approve_ai_content/',
  NOTE_IMPORT_YOUTUBE: 'notes/import_youtube/',
  NOTE_EXPORT_PDF: (id) => `notes/${id}/export_pdf/`,
  NOTE_DAILY: 'notes/daily_notes/',

  // Code Snippets
  SNIPPETS: 'snippets/',
  SNIPPET_DETAIL: (id) => `snippets/${id}/`,

  // Sources
  SOURCES: 'sources/',
  SOURCE_DETAIL: (id) => `sources/${id}/`,
  SOURCE_AUTO_FETCH: 'sources/auto_fetch/',

  // Templates
  TEMPLATES: 'templates/',
  TEMPLATE_DETAIL: (id) => `templates/${id}/`,
  TEMPLATE_USE: (id) => `templates/${id}/use_template/`,

  // Reports
  REPORTS: 'reports/',
  REPORT_DETAIL: (id) => `reports/${id}/`,
  REPORT_GENERATE_TODAY: 'reports/generate_today/',

  // Shares
  SHARES: 'shares/',
  SHARE_DETAIL: (id) => `shares/${id}/`,
  SHARE_CREATE_PUBLIC: 'shares/create_public_share/',

  // Roadmaps
  ROADMAPS: 'roadmaps/',
  ROADMAP_DETAIL: (id) => `roadmaps/${id}/`,
  MILESTONES: 'roadmaps/milestones/',
  TASKS: 'roadmaps/tasks/',

  // Analytics
  DASHBOARD: 'analytics/dashboard/',
  STUDY_HISTORY: 'analytics/study-history/',
  NOTIFICATIONS: 'analytics/notifications/',
  MARK_ALL_READ: 'analytics/notifications/mark_all_read/',
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
