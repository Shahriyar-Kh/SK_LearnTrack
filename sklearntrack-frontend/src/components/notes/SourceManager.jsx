// FILE: src/components/notes/SourceManager.jsx
// ============================================================================

import { useState, useEffect } from 'react';
import { Plus, Trash2, ExternalLink, Loader, X, Search } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import api from '@/services/api';
import toast from 'react-hot-toast';

const SourceManager = ({ noteId, sources, onUpdate, onClose }) => {
  const [localSources, setLocalSources] = useState(sources || []);
  const [loading, setLoading] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    source_type: 'url',
    title: '',
    url: '',
    author: '',
    date: '',
    metadata: {}
  });

  const sourceTypes = [
    { value: 'youtube', label: 'YouTube Video' },
    { value: 'url', label: 'Website/URL' },
    { value: 'pdf', label: 'PDF Document' },
    { value: 'article', label: 'Article' },
    { value: 'book', label: 'Book' },
    { value: 'other', label: 'Other' }
  ];

  useEffect(() => {
    if (noteId) {
      fetchSources();
    }
  }, [noteId]);

  const fetchSources = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/notes/${noteId}/`);
      setLocalSources(response.data.sources || []);
    } catch (error) {
      console.error('Error fetching sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAutoFetch = async () => {
    if (!formData.url) {
      toast.error('Please enter a URL first');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/api/sources/auto_fetch/', {
        url: formData.url,
        source_type: formData.source_type
      });
      
      setFormData(prev => ({
        ...prev,
        title: response.data.title || prev.title,
        author: response.data.author || prev.author,
        date: response.data.date || prev.date
      }));
      
      toast.success('Metadata fetched successfully!');
    } catch (error) {
      toast.error('Failed to fetch metadata');
    } finally {
      setLoading(false);
    }
  };

  const handleAddSource = async () => {
    if (!formData.title || !formData.url) {
      toast.error('Please fill in title and URL');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/api/sources/', formData);
      
      // Add source to note if noteId exists
      if (noteId) {
        await api.patch(`/api/notes/${noteId}/`, {
          sources: [...localSources.map(s => s.id), response.data.id]
        });
      }
      
      setLocalSources(prev => [...prev, response.data]);
      setShowAddForm(false);
      setFormData({
        source_type: 'url',
        title: '',
        url: '',
        author: '',
        date: '',
        metadata: {}
      });
      
      toast.success('Source added successfully!');
      onUpdate && onUpdate();
    } catch (error) {
      toast.error('Failed to add source');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSource = async (sourceId) => {
    if (!window.confirm('Delete this source?')) return;

    try {
      setLoading(true);
      await api.delete(`/api/sources/${sourceId}/`);
      setLocalSources(prev => prev.filter(s => s.id !== sourceId));
      toast.success('Source deleted');
      onUpdate && onUpdate();
    } catch (error) {
      toast.error('Failed to delete source');
    } finally {
      setLoading(false);
    }
  };

  const formatSourceReference = (source) => {
    let reference = `[${source.reference_number}] `;
    
    if (source.author) {
      reference += `${source.author}, `;
    }
    
    reference += `"${source.title}"`;
    
    if (source.source_type === 'youtube') {
      reference += ' [Video]';
    } else if (source.source_type === 'url') {
      reference += ' [Online]';
    }
    
    if (source.date) {
      reference += `, ${new Date(source.date).getFullYear()}`;
    }
    
    return reference;
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold">Source Manager</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        {/* Add Source Form */}
        {showAddForm ? (
          <div className="mb-6 p-4 border-2 dark:border-gray-700 rounded-lg">
            <h4 className="font-semibold mb-4">Add New Source</h4>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Source Type</label>
                <select
                  name="source_type"
                  value={formData.source_type}
                  onChange={handleInputChange}
                  className="input-field w-full"
                >
                  {sourceTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">URL</label>
                <div className="flex gap-2">
                  <input
                    type="url"
                    name="url"
                    value={formData.url}
                    onChange={handleInputChange}
                    placeholder="https://..."
                    className="input-field flex-1"
                    required
                  />
                  <Button
                    variant="secondary"
                    onClick={handleAutoFetch}
                    disabled={loading}
                    className="flex items-center gap-2"
                  >
                    <Search size={16} />
                    Auto-fetch
                  </Button>
                </div>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium mb-2">Title</label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleInputChange}
                  placeholder="Source title"
                  className="input-field w-full"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Author</label>
                <input
                  type="text"
                  name="author"
                  value={formData.author}
                  onChange={handleInputChange}
                  placeholder="Author name"
                  className="input-field w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Date</label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleInputChange}
                  className="input-field w-full"
                />
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <Button onClick={handleAddSource} disabled={loading}>
                {loading ? <Loader size={16} className="animate-spin" /> : 'Add Source'}
              </Button>
              <Button
                variant="secondary"
                onClick={() => {
                  setShowAddForm(false);
                  setFormData({
                    source_type: 'url',
                    title: '',
                    url: '',
                    author: '',
                    date: '',
                    metadata: {}
                  });
                }}
              >
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
            Add Source
          </Button>
        )}

        {/* Sources List */}
        <div className="space-y-4">
          <h4 className="font-semibold text-lg">References ({localSources.length})</h4>
          
          {loading && localSources.length === 0 ? (
            <div className="text-center py-8">
              <Loader size={32} className="animate-spin mx-auto text-primary-600" />
            </div>
          ) : localSources.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No sources added yet. Add your first source to start building references.
            </div>
          ) : (
            <div className="space-y-3">
              {localSources.map(source => (
                <div
                  key={source.id}
                  className="p-4 border dark:border-gray-700 rounded-lg hover:border-primary-600 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="text-xs font-mono bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 px-2 py-1 rounded">
                          [{source.reference_number}]
                        </span>
                        <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
                          {sourceTypes.find(t => t.value === source.source_type)?.label}
                        </span>
                      </div>
                      
                      <h5 className="font-semibold mb-1">{source.title}</h5>
                      
                      <div className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                        {source.author && <p>Author: {source.author}</p>}
                        {source.date && (
                          <p>Date: {new Date(source.date).toLocaleDateString()}</p>
                        )}
                        {source.url && (
                          <a
                            href={source.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-primary-600 hover:underline"
                          >
                            <ExternalLink size={14} />
                            {source.url.substring(0, 50)}...
                          </a>
                        )}
                      </div>

                      <div className="mt-3 p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm font-mono">
                        {formatSourceReference(source)}
                      </div>
                    </div>

                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => handleDeleteSource(source.id)}
                      className="flex items-center gap-1"
                    >
                      <Trash2 size={14} />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* IEEE Citation Guide */}
        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
          <h4 className="font-semibold mb-2">IEEE Citation Format</h4>
          <p className="text-sm text-gray-700 dark:text-gray-300">
            Sources are automatically formatted in IEEE style. Use reference numbers [1], [2], etc. 
            in your notes to cite these sources.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default SourceManager;