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
 
 // Standalone AI action (works without saved topic)
performStandaloneAIAction: async (actionData) => {
  try {
    const response = await api.post('/api/topics/ai-action-standalone/', actionData);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'AI action failed');
    }
    
    return response.data;
  } catch (error) {
    console.error('Standalone AI action error:', error);
    
    // Provide helpful error messages
    if (error.response?.status === 400) {
      throw new Error(error.response.data.error || 'Invalid request');
    } else if (error.response?.status === 500) {
      throw new Error('AI service error. Please try again.');
    } else if (error.message === 'Network Error') {
      throw new Error('Network error. Please check your connection.');
    }
    
    throw new Error(error.response?.data?.error || error.message || 'AI action failed');
  }
},

// Also update the existing performAIAction to be more robust:
performAIAction: async (topicId, actionData) => {
  try {
    // If no topicId, use standalone action
    if (!topicId) {
      return await noteService.performStandaloneAIAction(actionData);
    }
    
    const response = await api.post(`/api/topics/${topicId}/ai_action/`, actionData);
    
    if (!response.data.success) {
      throw new Error(response.data.error || 'AI action failed');
    }
    
    return response.data;
  } catch (error) {
    console.error('AI action error:', error);
    
    // Better error handling
    if (error.response?.status === 404) {
      // Topic not found, try standalone
      return await noteService.performStandaloneAIAction(actionData);
    } else if (error.response?.status === 400) {
      throw new Error(error.response.data.error || 'Invalid request');
    } else if (error.response?.status === 500) {
      throw new Error('AI service error. Please try again.');
    }
    
    throw new Error(error.response?.data?.error || error.message || 'AI action failed');
  }
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
// Update the runCode function
runCode: async ({ code, language, stdin = "", timeout = 15 }) => {
  try {
    const response = await api.post(
      "/api/notes/run_code/",
      { 
        code, 
        language, 
        stdin,
        timeout
      },
      { 
        timeout: (timeout + 5) * 1000, // Add buffer
        headers: {
          'Content-Type': 'application/json'
        }
      }
    );
    
    const data = response.data;
    
    // Handle input requirement
    if (data.requires_input) {
      return {
        success: false,
        output: '',
        error: data.error,
        requires_input: true
      };
    }
    
    return data;
  } catch (error) {
    console.error("Code execution error:", error);
    
    if (error.code === "ECONNABORTED") {
      return {
        success: false,
        output: '',
        error: "Execution timeout. The code took too long to run.",
        timeout: true
      };
    }
    
    if (error.response?.data?.error) {
      return {
        success: false,
        output: '',
        error: error.response.data.error,
        ...error.response.data
      };
    }
    
    if (error.message === "Network Error") {
      return {
        success: false,
        output: '',
        error: "Network error. Please check your internet connection."
      };
    }
    
    return {
      success: false,
      output: '',
      error: "Code execution failed. Please try again."
    };
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
  // ========================================================================
// STANDALONE AI TOOLS
// ========================================================================
aiToolExplain: async (data) => {
  const response = await api.post('/api/ai-tools/explain_topic/', data);
  return response.data;
},

aiToolImprove: async (data) => {
  const response = await api.post('/api/ai-tools/improve/', data);
  return response.data;
},

aiToolSummarize: async (data) => {
  const response = await api.post('/api/ai-tools/summarize/', data);
  return response.data;
},

aiToolGenerateCode: async (data) => {
  const response = await api.post('/api/ai-tools/generate_code/', data);
  return response.data;
},


// Get AI history
getAIHistory: async (featureType = null) => {
  const params = featureType ? { feature_type: featureType } : {};
  const response = await api.get('/api/ai-tools/history/', { params });
  return response.data;
},

// Delete AI history item
deleteAIHistory: async (historyId) => {
  const response = await api.delete(`/api/ai-tools/${historyId}/delete_history/`);
  return response.data;
},

// Save AI history as note
saveAIHistoryAsNote: async (historyId) => {
  const response = await api.post(`/api/ai-tools/${historyId}/save_as_note/`);
  return response.data;
},

// Export AI history as PDF
exportAIHistoryPDF: async (historyId) => {
  const response = await api.post(`/api/ai-tools/${historyId}/export_pdf/`, {}, {
    responseType: 'blob'
  });
  
  // Create download
  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `ai-content-${Date.now()}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
  
  return { success: true };
},

// Export AI history to Google Drive
exportAIHistoryToDrive: async (historyId) => {
  const response = await api.post(`/api/ai-tools/${historyId}/export_to_drive/`);
  return response.data;
},
};




export default noteService;
