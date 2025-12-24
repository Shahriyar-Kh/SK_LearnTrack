// FILE: src/components/notes/VersionHistory.jsx
// ============================================================================
// COPY THIS ENTIRE FILE TO: src/components/notes/VersionHistory.jsx

import { useState, useEffect } from 'react';
import { History, RotateCcw, Eye, X, Loader, Clock, FileText } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import api from '@/services/api';
import toast from 'react-hot-toast';

const VersionHistory = ({ noteId, onRestore, onClose }) => {
  const [versions, setVersions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedVersion, setSelectedVersion] = useState(null);
  const [showPreview, setShowPreview] = useState(false);
  const [restoring, setRestoring] = useState(false);

  useEffect(() => {
    if (noteId) {
      fetchVersions();
    }
  }, [noteId]);

  const fetchVersions = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/notes/${noteId}/versions/`);
      setVersions(response.data || []);
    } catch (error) {
      console.error('Error fetching versions:', error);
      toast.error('Failed to load version history');
    } finally {
      setLoading(false);
    }
  };

  const handlePreviewVersion = (version) => {
    setSelectedVersion(version);
    setShowPreview(true);
  };

  const handleRestoreVersion = async (version) => {
    if (!window.confirm(`Restore to version ${version.version_number}? Current content will be saved as a new version.`)) {
      return;
    }

    try {
      setRestoring(true);
      const response = await api.post(`/api/notes/${noteId}/restore_version/`, {
        version_id: version.id
      });
      
      toast.success(`Restored to version ${version.version_number}`);
      onRestore(version);
      onClose();
    } catch (error) {
      console.error('Error restoring version:', error);
      toast.error('Failed to restore version');
    } finally {
      setRestoring(false);
    }
  };

  const formatContent = (content) => {
    if (!content) return '';
    
    // Simple markdown to HTML for preview
    let formatted = content
      .replace(/^### (.*$)/gim, '<h3 class="text-lg font-bold mt-4 mb-2">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-xl font-bold mt-4 mb-2">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-2xl font-bold mt-4 mb-3">$1</h1>')
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/`(.+?)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-sm">$1</code>')
      .replace(/\n/g, '<br />');
    
    return formatted;
  };

  const getTimeDifference = (date) => {
    const now = new Date();
    const versionDate = new Date(date);
    const diffMs = now - versionDate;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
      return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 30) {
      return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
      return versionDate.toLocaleDateString();
    }
  };

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <Card className="max-w-5xl w-full max-h-[90vh] overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-2xl font-bold flex items-center gap-2">
              <History size={24} className="text-primary-600" />
              Version History
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X size={24} />
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <Loader size={48} className="animate-spin mx-auto text-primary-600 mb-4" />
              <p className="text-gray-600 dark:text-gray-400">Loading version history...</p>
            </div>
          ) : versions.length === 0 ? (
            <div className="text-center py-12">
              <History size={64} className="mx-auto text-gray-400 mb-4" />
              <h4 className="text-xl font-semibold mb-2">No Version History</h4>
              <p className="text-gray-600 dark:text-gray-400">
                Version history will be created as you make changes to your note.
              </p>
            </div>
          ) : (
            <>
              <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
                <p className="text-sm">
                  <strong>Total Versions:</strong> {versions.length} | 
                  <strong className="ml-2">Oldest:</strong> {new Date(versions[versions.length - 1]?.saved_at).toLocaleDateString()}
                </p>
              </div>

              <div className="space-y-3">
                {versions.map((version, index) => (
                  <div
                    key={version.id}
                    className={`border-2 dark:border-gray-700 rounded-lg p-4 transition-all ${
                      index === 0 ? 'border-primary-600 bg-primary-50 dark:bg-primary-900' : 'hover:border-primary-600'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className={`text-lg font-bold ${
                            index === 0 ? 'text-primary-600' : ''
                          }`}>
                            Version {version.version_number}
                          </span>
                          
                          {index === 0 && (
                            <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full font-medium">
                              Current
                            </span>
                          )}

                          <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                            <Clock size={14} />
                            <span>{getTimeDifference(version.saved_at)}</span>
                          </div>
                        </div>

                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          Saved on {new Date(version.saved_at).toLocaleString()}
                        </p>

                        {version.changes_summary && (
                          <p className="text-sm bg-gray-100 dark:bg-gray-800 p-2 rounded">
                            {version.changes_summary}
                          </p>
                        )}

                        {/* Content Preview */}
                        <div className="mt-3 text-sm text-gray-700 dark:text-gray-300">
                          <div className="flex items-center gap-2 mb-1">
                            <FileText size={14} />
                            <span className="font-medium">Content Preview:</span>
                          </div>
                          <div className="bg-white dark:bg-gray-900 p-3 rounded border dark:border-gray-700 max-h-32 overflow-hidden">
                            <p className="line-clamp-3">
                              {version.content.substring(0, 200)}...
                            </p>
                          </div>
                        </div>
                      </div>

                      <div className="flex flex-col gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => handlePreviewVersion(version)}
                          className="flex items-center gap-1"
                        >
                          <Eye size={14} />
                          Preview
                        </Button>
                        
                        {index !== 0 && (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleRestoreVersion(version)}
                            disabled={restoring}
                            className="flex items-center gap-1"
                          >
                            {restoring ? (
                              <Loader size={14} className="animate-spin" />
                            ) : (
                              <>
                                <RotateCcw size={14} />
                                Restore
                              </>
                            )}
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Info */}
          <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg">
            <h4 className="font-semibold mb-2 text-sm">About Version History</h4>
            <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
              <li>• Versions are automatically saved when you make changes</li>
              <li>• The system keeps your last 10 versions by default</li>
              <li>• Restoring a version will save your current content as a new version</li>
            </ul>
          </div>
        </Card>
      </div>

      {/* Preview Modal */}
      {showPreview && selectedVersion && (
        <div className="fixed inset-0 bg-black bg-opacity-70 flex items-center justify-center p-4 z-[60]">
          <Card className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold">
                Version {selectedVersion.version_number} Preview
              </h3>
              <button
                onClick={() => {
                  setShowPreview(false);
                  setSelectedVersion(null);
                }}
                className="text-gray-400 hover:text-gray-600"
              >
                <X size={24} />
              </button>
            </div>

            <div className="mb-4 p-3 bg-gray-100 dark:bg-gray-800 rounded">
              <p className="text-sm">
                <strong>Saved:</strong> {new Date(selectedVersion.saved_at).toLocaleString()}
              </p>
              {selectedVersion.changes_summary && (
                <p className="text-sm mt-1">
                  <strong>Changes:</strong> {selectedVersion.changes_summary}
                </p>
              )}
            </div>

            <div
              className="prose dark:prose-invert max-w-none p-4 border dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900"
              dangerouslySetInnerHTML={{ __html: formatContent(selectedVersion.content) }}
            />

            <div className="flex gap-2 mt-6">
              <Button
                onClick={() => {
                  setShowPreview(false);
                  handleRestoreVersion(selectedVersion);
                }}
                disabled={restoring}
                className="flex items-center gap-2"
              >
                {restoring ? (
                  <Loader size={16} className="animate-spin" />
                ) : (
                  <>
                    <RotateCcw size={16} />
                    Restore This Version
                  </>
                )}
              </Button>
              
              <Button
                variant="secondary"
                onClick={() => {
                  setShowPreview(false);
                  setSelectedVersion(null);
                }}
              >
                Close
              </Button>
            </div>
          </Card>
        </div>
      )}
    </>
  );
};

export default VersionHistory;