// FILE: src/services/note.service.js
// ============================================================================

import api from './api';
import { API_ENDPOINTS } from '@/utils/constants';

export const noteService = {
  // Get all notes
  getNotes: async (params = {}) => {
    const response = await api.get(API_ENDPOINTS.NOTES, { params });
    return response.data;
  },

  // Get note detail
  getNoteDetail: async (id) => {
    const response = await api.get(API_ENDPOINTS.NOTE_DETAIL(id));
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

  // Get note history
  getNoteHistory: async (id) => {
    const response = await api.get(API_ENDPOINTS.NOTE_HISTORY(id));
    return response.data;
  },

  // Code snippets
  getSnippets: async () => {
    const response = await api.get(API_ENDPOINTS.SNIPPETS);
    return response.data;
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