// FILE: src/services/note.service.js
// ============================================================================

import api from './api';
import { API_ENDPOINTS } from '@/utils/constants';

export const noteService = {
  // ========================================================================
  // NOTES
  // ========================================================================
  
  // Get all notes with optional filters
  getNotes: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.NOTES, { params });
    return response.data;
  },

  // Get note detail with full structure
  getNoteDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.NOTE_DETAIL(id));
    return response.data;
  },

  // Get note structure (chapters + topics)
  getNoteStructure: async (id) => {
    const response = await api.get(`${API_ENDPOINTS.NOTE_DETAIL(id)}structure/`);
    return response.data;
  },

  // Create note
  createNote: async (noteData) => {
    const response = await api.post(API_ENDPOINTS.NOTES, noteData);
    return response.data;
  },

  // Update note
  updateNote: async (id, noteData) => {
    const response = await api.patch(API_ENDPOINTS.NOTE_DETAIL(id), noteData);
    return response.data;
  },

  // Delete note
  deleteNote: async (id) => {
    const response = await api.delete(API_ENDPOINTS.NOTE_DETAIL(id));
    return response.data;
  },

 // Export note to PDF - FIXED VERSION
exportNotePDF: async (id, noteTitle) => {
  try {
    const response = await api.post(`/api/notes/${id}/export_pdf/`, {}, {
      responseType: 'blob',
      timeout: 30000
    });

    // Check if it's a PDF by checking the content type or data type
    const contentType = response.headers['content-type'];
    const isPDF = contentType && contentType.includes('application/pdf');
    
    // Check if response status is successful (200-299)
    const isSuccess = response.status >= 200 && response.status < 300;
    
    if (!isSuccess || !isPDF) {
      // Try to parse as error JSON
      const errorText = await response.data.text();
      try {
        const errorData = JSON.parse(errorText);
        throw new Error(errorData.error || errorData.message || 'Failed to export PDF');
      } catch {
        throw new Error(`Server returned ${response.status}: ${errorText.substring(0, 100)}`);
      }
    }

    // Create filename
    const safeTitle = (noteTitle || 'note').replace(/[^a-zA-Z0-9]/g, '_');
    const date = new Date().toISOString().split('T')[0];
    const filename = `${safeTitle}_${date}.pdf`;

    // Create blob and download
    const blob = new Blob([response.data], { type: 'application/pdf' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    
    // Cleanup
    setTimeout(() => {
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    }, 100);

    return { success: true, filename };

  } catch (error) {
    console.error('PDF export error:', error);
    
    // Check if it's a timeout error
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      throw new Error('PDF generation is taking too long. Please try again.');
    }
    
    // Check if it's a network error vs server error
    if (error.message === 'Network Error' || !error.response) {
      throw new Error('Network error. Please check your connection.');
    }
    
    // Try to get error message from response
    if (error.response && error.response.data) {
      try {
        // If it's a blob, convert to text
        if (error.response.data instanceof Blob) {
          const errorText = await error.response.data.text();
          const errorData = JSON.parse(errorText);
          throw new Error(errorData.error || errorData.message || 'Failed to export PDF');
        }
        // If it's already an object
        else if (typeof error.response.data === 'object') {
          throw new Error(error.response.data.error || error.response.data.message || 'Failed to export PDF');
        }
      } catch (e) {
        // If we can't parse as JSON, use the original error
        throw new Error(error.message || 'Failed to export PDF');
      }
    }
    
    throw error;
  }
},
  // ========================================================================
  // CHAPTERS
  // ========================================================================

  // Get all chapters for a note
  getChapters: async (noteId) => {
    const response = await api.get('/api/chapters/', {
      params: { note_id: noteId }
    });
    return response.data;
  },

  // Create chapter
  createChapter: async (chapterData) => {
    const response = await api.post('/api/chapters/', chapterData);
    return response.data;
  },

  // Update chapter
  updateChapter: async (id, chapterData) => {
    const response = await api.patch(`/api/chapters/${id}/`, chapterData);
    return response.data;
  },

  // Delete chapter
  deleteChapter: async (id) => {
    const response = await api.delete(`/api/chapters/${id}/`);
    return response.data;
  },

  // Reorder chapter
  reorderChapter: async (id, order) => {
    const response = await api.post(`/api/chapters/${id}/reorder/`, { order });
    return response.data;
  },

  // ========================================================================
  // TOPICS
  // ========================================================================

  // Get all topics
  getTopics: async (params = {}) => {
    const response = await api.get('/api/topics/', { params });
    return response.data;
  },

  // Get topic detail
  getTopicDetail: async (id) => {
    const response = await api.get(`/api/topics/${id}/`);
    return response.data;
  },

  // Create topic
  createTopic: async (topicData) => {
    const response = await api.post('/api/topics/', topicData);
    return response.data;
  },

  // Update topic
  updateTopic: async (id, topicData) => {
    const response = await api.patch(`/api/topics/${id}/`, topicData);
    return response.data;
  },

  // Delete topic
  deleteTopic: async (id) => {
    const response = await api.delete(`/api/topics/${id}/`);
    return response.data;
  },

  // Reorder topic
  reorderTopic: async (id, order) => {
    const response = await api.post(`/api/topics/${id}/reorder/`, { order });
    return response.data;
  },

  // AI action on topic
  performAIAction: async (topicId, actionData) => {
    const response = await api.post(`/api/topics/${topicId}/ai_action/`, actionData);
    return response.data;
  },

  // ========================================================================
  // VERSION HISTORY
  // ========================================================================

  // Get note history
  getNoteHistory: async (id) => {
    const response = await api.get(API_ENDPOINTS.NOTE_HISTORY(id));
    return response.data;
  },

  // Restore note version
  restoreVersion: async (id, versionId) => {
    const response = await api.post(API_ENDPOINTS.NOTE_RESTORE_VERSION(id), {
      version_id: versionId
    });
    return response.data;
  },

  // ========================================================================
  // CODE SNIPPETS (if you have separate snippets)
  // ========================================================================

  getSnippets: async () => {
    const response = await api.get(API_ENDPOINTS.SNIPPETS);
    return response.data;
  },
    // Run code execution
  runCode: async (codeData) => {
    try {
      const response = await api.post('/api/notes/run_code/', codeData);
      return response.data;
    } catch (error) {
      console.error('Error running code:', error);
      throw error;
    }
  },

  createSnippet: async (snippetData) => {
    const response = await api.post(API_ENDPOINTS.SNIPPETS, snippetData);
    return response.data;
  },

  updateSnippet: async (id, snippetData) => {
    const response = await api.patch(API_ENDPOINTS.SNIPPET_DETAIL(id), snippetData);
    return response.data;
  },

  deleteSnippet: async (id) => {
    const response = await api.delete(API_ENDPOINTS.SNIPPET_DETAIL(id));
    return response.data;
  },
};


export default noteService;
