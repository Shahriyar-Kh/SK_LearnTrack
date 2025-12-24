// FILE: src/components/notes/CodeSnippetManager.jsx
// ============================================================================
// COPY THIS ENTIRE FILE TO: src/components/notes/CodeSnippetManager.jsx

import { useState, useEffect } from 'react';
import { Plus, Trash2, Copy, Check, X, Code, Loader } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import api from '@/services/api';
import toast from 'react-hot-toast';

const CodeSnippetManager = ({ noteId, snippets, onUpdate, onClose }) => {
  const [localSnippets, setLocalSnippets] = useState(snippets || []);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [copiedId, setCopiedId] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    language: 'python',
    code: '',
    description: '',
    tags: []
  });

  const languages = [
    'python', 'javascript', 'typescript', 'java', 'cpp', 'c',
    'csharp', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
    'sql', 'html', 'css', 'bash', 'powershell', 'json', 'yaml',
    'markdown', 'xml', 'other'
  ];

  useEffect(() => {
    if (noteId) {
      fetchSnippets();
    }
  }, [noteId]);

  const fetchSnippets = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/snippets/', {
        params: { note: noteId }
      });
      setLocalSnippets(response.data.results || []);
    } catch (error) {
      console.error('Error fetching snippets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
    setFormData(prev => ({ ...prev, tags }));
  };

  const resetForm = () => {
    setFormData({
      title: '',
      language: 'python',
      code: '',
      description: '',
      tags: []
    });
    setShowAddForm(false);
    setEditingId(null);
  };

  const handleSaveSnippet = async () => {
    if (!formData.title || !formData.code) {
      toast.error('Please fill in title and code');
      return;
    }

    try {
      setLoading(true);
      const payload = {
        ...formData,
        note: noteId
      };

      let response;
      if (editingId) {
        response = await api.patch(`/api/snippets/${editingId}/`, payload);
        setLocalSnippets(prev => 
          prev.map(s => s.id === editingId ? response.data : s)
        );
        toast.success('Snippet updated!');
      } else {
        response = await api.post('/api/snippets/', payload);
        setLocalSnippets(prev => [...prev, response.data]);
        toast.success('Snippet added!');
      }

      resetForm();
      onUpdate && onUpdate();
    } catch (error) {
      toast.error('Failed to save snippet');
    } finally {
      setLoading(false);
    }
  };

  const handleEditSnippet = (snippet) => {
    setFormData({
      title: snippet.title,
      language: snippet.language,
      code: snippet.code,
      description: snippet.description || '',
      tags: snippet.tags || []
    });
    setEditingId(snippet.id);
    setShowAddForm(true);
  };

  const handleDeleteSnippet = async (snippetId) => {
    if (!window.confirm('Delete this code snippet?')) return;

    try {
      setLoading(true);
      await api.delete(`/api/snippets/${snippetId}/`);
      setLocalSnippets(prev => prev.filter(s => s.id !== snippetId));
      toast.success('Snippet deleted');
      onUpdate && onUpdate();
    } catch (error) {
      toast.error('Failed to delete snippet');
    } finally {
      setLoading(false);
    }
  };

  const handleCopyCode = async (code, snippetId) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedId(snippetId);
      toast.success('Code copied to clipboard!');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      toast.error('Failed to copy code');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold flex items-center gap-2">
            <Code size={24} className="text-primary-600" />
            Code Snippets
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        {/* Add/Edit Form */}
        {showAddForm ? (
          <div className="mb-6 p-4 border-2 dark:border-gray-700 rounded-lg">
            <h4 className="font-semibold mb-4">
              {editingId ? 'Edit' : 'Add'} Code Snippet
            </h4>
            
            <div className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Title</label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="e.g., Binary Search Implementation"
                    className="input-field w-full"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Language</label>
                  <select
                    name="language"
                    value={formData.language}
                    onChange={handleInputChange}
                    className="input-field w-full"
                  >
                    {languages.map(lang => (
                      <option key={lang} value={lang}>
                        {lang.charAt(0).toUpperCase() + lang.slice(1)}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Code</label>
                <textarea
                  name="code"
                  value={formData.code}
                  onChange={handleInputChange}
                  placeholder="Paste your code here..."
                  className="input-field w-full min-h-[300px] font-mono text-sm"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  placeholder="Explain what this code does..."
                  className="input-field w-full min-h-[100px]"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">
                  Tags (comma-separated)
                </label>
                <input
                  type="text"
                  value={formData.tags.join(', ')}
                  onChange={handleTagsChange}
                  placeholder="algorithm, sorting, optimization"
                  className="input-field w-full"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <Button onClick={handleSaveSnippet} disabled={loading}>
                {loading ? (
                  <Loader size={16} className="animate-spin" />
                ) : (
                  editingId ? 'Update Snippet' : 'Add Snippet'
                )}
              </Button>
              <Button variant="secondary" onClick={resetForm}>
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <Button
            onClick={() => setShowAddForm(true)}
            className="flex items-center gap-2 mb-6"
          >
            <Plus size={20} />
            Add Code Snippet
          </Button>
        )}

        {/* Snippets List */}
        <div className="space-y-4">
          <h4 className="font-semibold text-lg">
            Saved Snippets ({localSnippets.length})
          </h4>
          
          {loading && localSnippets.length === 0 ? (
            <div className="text-center py-8">
              <Loader size={32} className="animate-spin mx-auto text-primary-600" />
            </div>
          ) : localSnippets.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No code snippets yet. Add your first snippet to get started.
            </div>
          ) : (
            <div className="space-y-4">
              {localSnippets.map(snippet => (
                <div
                  key={snippet.id}
                  className="border dark:border-gray-700 rounded-lg overflow-hidden"
                >
                  {/* Snippet Header */}
                  <div className="bg-gray-50 dark:bg-gray-800 p-4 flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h5 className="font-semibold">{snippet.title}</h5>
                        <span className="text-xs bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 px-2 py-1 rounded">
                          {snippet.language}
                        </span>
                      </div>
                      
                      {snippet.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {snippet.description}
                        </p>
                      )}

                      {snippet.tags && snippet.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {snippet.tags.map((tag, i) => (
                            <span
                              key={i}
                              className="text-xs bg-gray-200 dark:bg-gray-700 px-2 py-0.5 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex gap-2">
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleCopyCode(snippet.code, snippet.id)}
                        className="flex items-center gap-1"
                      >
                        {copiedId === snippet.id ? (
                          <>
                            <Check size={14} />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy size={14} />
                            Copy
                          </>
                        )}
                      </Button>
                      
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => handleEditSnippet(snippet)}
                      >
                        Edit
                      </Button>
                      
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => handleDeleteSnippet(snippet.id)}
                      >
                        <Trash2 size={14} />
                      </Button>
                    </div>
                  </div>

                  {/* Code Display */}
                  <div className="bg-gray-900 p-4 overflow-x-auto">
                    <pre className="text-sm text-gray-100">
                      <code>{snippet.code}</code>
                    </pre>
                  </div>

                  {/* Metadata */}
                  <div className="bg-gray-50 dark:bg-gray-800 px-4 py-2 text-xs text-gray-600 dark:text-gray-400">
                    Created: {new Date(snippet.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Tips */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
          <h4 className="font-semibold mb-2 text-sm">Tips</h4>
          <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
            <li>• Use descriptive titles to easily find snippets later</li>
            <li>• Add tags for better organization and searchability</li>
            <li>• Include descriptions to remember the context and purpose</li>
          </ul>
        </div>
      </Card>
    </div>
  );
};

export default CodeSnippetManager;