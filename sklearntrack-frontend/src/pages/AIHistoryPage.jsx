import { useState, useEffect } from 'react';
import {
  FileText, Download, Trash2, Search, Filter, 
  Save, Cloud, Clock, Code, Sparkles, Loader,
  CheckCircle, AlertCircle, Edit2, X
} from 'lucide-react';
import { aiHistoryService } from '@/services/ai-history.service';
import Navbar from '@/components/layout/Navbar';

const AIHistoryPage = () => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedItem, setSelectedItem] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, [filterType, filterStatus]);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const filters = {};
      if (filterType !== 'all') filters.action_type = filterType;
      if (filterStatus !== 'all') filters.status = filterStatus;
      
      const data = await aiHistoryService.getHistory(filters);
      setHistory(data.results || data || []);
    } catch (error) {
      console.error('Error fetching history:', error);
      showToast('Failed to load history', 'error');
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleExportPDF = async (item) => {
    try {
      const blob = await aiHistoryService.exportPDF(item.id);
      const filename = `${item.title.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      aiHistoryService.downloadFile(blob, filename);
      showToast('PDF downloaded successfully!');
    } catch (error) {
      console.error('PDF export error:', error);
      showToast('Failed to export PDF', 'error');
    }
  };

  const handleExportDrive = async (item) => {
    try {
      const result = await aiHistoryService.exportToDrive(item.id);
      if (result.success) {
        showToast(`Exported to Google Drive: ${result.folder}`);
        fetchHistory(); // Refresh to show drive status
      } else {
        showToast(result.error || 'Failed to export to Drive', 'error');
      }
    } catch (error) {
      console.error('Drive export error:', error);
      if (error.response?.data?.needs_auth) {
        showToast('Please authenticate with Google Drive first', 'error');
      } else {
        showToast('Failed to export to Drive', 'error');
      }
    }
  };

  const handleMarkSaved = async (item) => {
    try {
      await aiHistoryService.markSaved(item.id);
      showToast('Marked as saved!');
      fetchHistory();
    } catch (error) {
      console.error('Mark saved error:', error);
      showToast('Failed to mark as saved', 'error');
    }
  };

  const handleDelete = async (item) => {
    if (!confirm(`Delete "${item.title}"? This cannot be undone.`)) return;
    
    try {
      await aiHistoryService.deleteHistory(item.id);
      showToast('History deleted successfully');
      fetchHistory();
    } catch (error) {
      console.error('Delete error:', error);
      showToast('Failed to delete history', 'error');
    }
  };

  const handleUpdate = async (item, updates) => {
    try {
      await aiHistoryService.updateHistory(item.id, updates);
      showToast('History updated successfully');
      setEditingItem(null);
      fetchHistory();
    } catch (error) {
      console.error('Update error:', error);
      showToast('Failed to update history', 'error');
    }
  };

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'generate_code':
        return <Code size={18} className="text-purple-600" />;
      case 'generate_explanation':
        return <FileText size={18} className="text-blue-600" />;
      case 'improve_explanation':
        return <Sparkles size={18} className="text-green-600" />;
      case 'summarize_explanation':
        return <FileText size={18} className="text-orange-600" />;
      default:
        return <FileText size={18} />;
    }
  };

  const filteredHistory = history.filter(item =>
    item.title.toLowerCase().includes(search.toLowerCase()) ||
    item.prompt.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />

      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 z-50">
          <div className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg ${
            toast.type === 'success' ? 'bg-green-50 border-l-4 border-green-500' :
            toast.type === 'error' ? 'bg-red-50 border-l-4 border-red-500' :
            'bg-blue-50 border-l-4 border-blue-500'
          }`}>
            {toast.type === 'success' && <CheckCircle className="text-green-600" size={20} />}
            {toast.type === 'error' && <AlertCircle className="text-red-600" size={20} />}
            <span className={`text-sm font-medium ${
              toast.type === 'success' ? 'text-green-800' :
              toast.type === 'error' ? 'text-red-800' :
              'text-blue-800'
            }`}>
              {toast.message}
            </span>
            <button onClick={() => setToast(null)} className="ml-2 text-gray-400 hover:text-gray-600">
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">🤖 AI History</h1>
              <p className="text-gray-600 dark:text-gray-400">
                View and manage all your AI-generated content
              </p>
            </div>
            <button
              onClick={() => aiHistoryService.cleanupOld().then(() => {
                showToast('Old records cleaned up');
                fetchHistory();
              })}
              className="px-4 py-2 text-sm bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              <Trash2 size={16} className="inline mr-2" />
              Cleanup Old
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-4 flex-wrap">
            <div className="flex-1 relative min-w-[200px]">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search history..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
              />
            </div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
            >
              <option value="all">All Types</option>
              <option value="generate_explanation">Explanations</option>
              <option value="improve_explanation">Improvements</option>
              <option value="summarize_explanation">Summaries</option>
              <option value="generate_code">Code</option>
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
            >
              <option value="all">All Status</option>
              <option value="temporary">Temporary</option>
              <option value="saved">Saved</option>
            </select>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="text-center py-12">
            <Loader size={48} className="animate-spin mx-auto text-blue-600" />
            <p className="text-gray-600 mt-4">Loading history...</p>
          </div>
        ) : filteredHistory.length === 0 ? (
          <div className="text-center py-12">
            <FileText size={64} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold mb-2">No AI history found</h3>
            <p className="text-gray-600">Start using AI features to see your history here</p>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {filteredHistory.map((item) => (
              <div
                key={item.id}
                className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-4 hover:shadow-lg transition"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {getActionIcon(item.action_type)}
                    <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
                      {item.action_type_display}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    {item.status === 'saved' && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                        Saved
                      </span>
                    )}
                    {item.drive_file_id && (
                      <Cloud size={14} className="text-blue-600" title="In Google Drive" />
                    )}
                  </div>
                </div>

                <h3 className="font-semibold text-lg mb-2 truncate" title={item.title}>
                  {item.title}
                </h3>

                <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 mb-3">
                  {item.prompt}
                </p>

                <div className="flex items-center gap-2 text-xs text-gray-500 mb-4">
                  <Clock size={12} />
                  <span>{new Date(item.created_at).toLocaleDateString()}</span>
                  {item.language && (
                    <>
                      <span>•</span>
                      <span className="uppercase">{item.language}</span>
                    </>
                  )}
                </div>

                <div className="flex gap-2 flex-wrap">
                  <button
                    onClick={() => {
                      setSelectedItem(item);
                      setShowDetailModal(true);
                    }}
                    className="flex-1 px-3 py-1.5 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                  >
                    View
                  </button>
                  <button
                    onClick={() => handleExportPDF(item)}
                    className="px-3 py-1.5 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    title="Export PDF"
                  >
                    <Download size={14} />
                  </button>
                  <button
                    onClick={() => handleExportDrive(item)}
                    className="px-3 py-1.5 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
                    title="Export to Drive"
                  >
                    <Cloud size={14} />
                  </button>
                  {item.status === 'temporary' && (
                    <button
                      onClick={() => handleMarkSaved(item)}
                      className="px-3 py-1.5 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200"
                      title="Save Permanently"
                    >
                      <Save size={14} />
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(item)}
                    className="px-3 py-1.5 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
                    title="Delete"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b dark:border-gray-700 p-6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                {getActionIcon(selectedItem.action_type)}
                <div>
                  <h2 className="text-2xl font-bold">{selectedItem.title}</h2>
                  <p className="text-sm text-gray-600">{selectedItem.action_type_display}</p>
                </div>
              </div>
              <button
                onClick={() => setShowDetailModal(false)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              >
                <X size={24} />
              </button>
            </div>

            <div className="p-6 space-y-6">
              {/* Prompt */}
              <div>
                <h3 className="text-lg font-semibold mb-2">Prompt:</h3>
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  <p className="whitespace-pre-wrap">{selectedItem.prompt}</p>
                </div>
              </div>

              {/* Generated Content */}
              <div>
                <h3 className="text-lg font-semibold mb-2">Generated Content:</h3>
                <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                  {selectedItem.action_type === 'generate_code' ? (
                    <pre className="text-sm font-mono overflow-x-auto">
                      <code>{selectedItem.generated_content}</code>
                    </pre>
                  ) : (
                    <div 
                      className="prose dark:prose-invert max-w-none"
                      dangerouslySetInnerHTML={{ __html: selectedItem.generated_content }}
                    />
                  )}
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4 border-t">
                <button
                  onClick={() => handleExportPDF(selectedItem)}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  <Download size={18} />
                  Export PDF
                </button>
                <button
                  onClick={() => handleExportDrive(selectedItem)}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  <Cloud size={18} />
                  Save to Drive
                </button>
                {selectedItem.status === 'temporary' && (
                  <button
                    onClick={() => handleMarkSaved(selectedItem)}
                    className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
                  >
                    <Save size={18} />
                    Save Permanently
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIHistoryPage;