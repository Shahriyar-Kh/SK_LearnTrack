// FILE: src/services/ai-history.service.js - FIXED VERSION
import api from './api';

export const aiHistoryService = {
  // Get all AI history
  getHistory: async (filters = {}) => {
    const params = new URLSearchParams(filters);
    // FIXED: Use /api/notes/ai-history/ instead of /notes/ai-history/
    const response = await api.get(`/api/notes/ai-history/?${params}`);
    return response.data;
  },

  // Get single history item
  getHistoryDetail: async (id) => {
    const response = await api.get(`/api/notes/ai-history/${id}/`);
    return response.data;
  },

  // Create history (usually done automatically by backend)
  createHistory: async (data) => {
    const response = await api.post('/api/notes/ai-history/', data);
    return response.data;
  },

  // Update history
  updateHistory: async (id, data) => {
    const response = await api.patch(`/api/notes/ai-history/${id}/`, data);
    return response.data;
  },

  // Delete history
  deleteHistory: async (id) => {
    const response = await api.delete(`/api/notes/ai-history/${id}/`);
    return response.data;
  },

  // Export to PDF
  exportPDF: async (id) => {
    const response = await api.post(`/api/notes/ai-history/${id}/export_pdf/`, {}, {
      responseType: 'blob',
      timeout: 30000  // 30 second timeout
    });
    return response.data;
  },

  // Export to Google Drive
  exportToDrive: async (id) => {
    const response = await api.post(`/api/notes/ai-history/${id}/export_to_drive/`);
    return response.data;
  },

  // Mark as saved permanently
  markSaved: async (id) => {
    const response = await api.post(`/api/notes/ai-history/${id}/mark_saved/`);
    return response.data;
  },

  // Cleanup old temporary records
  cleanupOld: async (days = 7) => {
    const response = await api.post('/api/notes/ai-history/cleanup_old/', { days });
    return response.data;
  },

  // Download file helper
  downloadFile: (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
  }
};

export default aiHistoryService;