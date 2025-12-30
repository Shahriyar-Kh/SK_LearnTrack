import { useState, useEffect } from 'react';
import { 
  Plus, FileText, Download, Trash2, Search, X, Loader, 
  AlertCircle, CheckCircle2, Info, Edit, Save
} from 'lucide-react';
import { noteService } from '@/services/note.service';
import NoteStructure from '@/components/notes/NoteStructure';
import TopicEditor from '@/components/notes/TopicEditor';

const NotesPage = () => {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Modals
  const [showNewNoteModal, setShowNewNoteModal] = useState(false);
  const [showNewChapterModal, setShowNewChapterModal] = useState(false);
  const [showTopicEditor, setShowTopicEditor] = useState(false);
  const [exporting, setExporting] = useState(false);
  
  // Delete confirmation
  const [deleteConfirm, setDeleteConfirm] = useState(null);
  
  // Toast notifications
  const [toast, setToast] = useState(null);
  
  // Note title editing
  const [editingNoteTitle, setEditingNoteTitle] = useState(false);
  const [noteTitleValue, setNoteTitleValue] = useState('');

  useEffect(() => {
    fetchNotes();
  }, [statusFilter]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchNotes = async () => {
    try {
      setLoading(true);
      const params = statusFilter !== 'all' ? { status: statusFilter } : {};
      const data = await noteService.getNotes(params);
      setNotes(data.results || data || []);
    } catch (error) {
      console.error('Error fetching notes:', error);
      showToast('Failed to load notes', 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchNoteDetail = async (noteId) => {
    try {
      const data = await noteService.getNoteStructure(noteId);
      setSelectedNote(data);
      setNoteTitleValue(data.title);
    } catch (error) {
      console.error('Error fetching note detail:', error);
      showToast('Failed to load note details', 'error');
    }
  };

  const handleCreateNote = async (title) => {
    try {
      const newNote = await noteService.createNote({ 
        title, 
        status: 'draft' 
      });
      setNotes([newNote, ...notes]);
      setSelectedNote(newNote);
      setNoteTitleValue(newNote.title);
      setShowNewNoteModal(false);
      showToast('Note created successfully!');
    } catch (error) {
      console.error('Error creating note:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to create note';
      showToast(errorMessage, 'error');
    }
  };

  const handleUpdateNoteTitle = async () => {
    if (!selectedNote || !noteTitleValue.trim()) {
      setEditingNoteTitle(false);
      setNoteTitleValue(selectedNote?.title || '');
      return;
    }
    
    if (noteTitleValue === selectedNote.title) {
      setEditingNoteTitle(false);
      return;
    }
    
    try {
      await noteService.updateNote(selectedNote.id, { title: noteTitleValue });
      setSelectedNote({ ...selectedNote, title: noteTitleValue });
      await fetchNotes(); // Refresh the list
      setEditingNoteTitle(false);
      showToast('Note title updated successfully!');
    } catch (error) {
      console.error('Error updating note title:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to update note title';
      showToast(errorMessage, 'error');
      setNoteTitleValue(selectedNote.title);
      setEditingNoteTitle(false);
    }
  };

  const handleCreateChapter = async (title) => {
    if (!selectedNote) return;
    
    try {
      await noteService.createChapter({ 
        note_id: selectedNote.id, 
        title 
      });
      await fetchNoteDetail(selectedNote.id);
      setShowNewChapterModal(false);
      showToast('Chapter created successfully!');
    } catch (error) {
      console.error('Error creating chapter:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to create chapter';
      showToast(errorMessage, 'error');
    }
  };

  const handleUpdateChapter = async (chapterId, newTitle) => {
    try {
      await noteService.updateChapter(chapterId, { title: newTitle });
      await fetchNoteDetail(selectedNote.id);
      showToast('Chapter updated successfully!');
    } catch (error) {
      console.error('Error updating chapter:', error);
      showToast('Failed to update chapter', 'error');
    }
  };

  const handleDeleteChapter = async (chapterId) => {
    setDeleteConfirm({
      type: 'chapter',
      id: chapterId,
      message: 'Are you sure you want to delete this chapter and all its topics?'
    });
  };

  const confirmDelete = async () => {
    if (!deleteConfirm) return;
    
    try {
      if (deleteConfirm.type === 'note') {
        await noteService.deleteNote(deleteConfirm.id);
        setSelectedNote(null);
        setNoteTitleValue('');
        await fetchNotes();
        showToast('Note deleted successfully!');
      } else if (deleteConfirm.type === 'chapter') {
        await noteService.deleteChapter(deleteConfirm.id);
        if (selectedNote) {
          await fetchNoteDetail(selectedNote.id);
        }
        showToast('Chapter deleted successfully!');
      } else if (deleteConfirm.type === 'topic') {
        await noteService.deleteTopic(deleteConfirm.id);
        if (selectedNote) {
          await fetchNoteDetail(selectedNote.id);
        }
        showToast('Topic deleted successfully!');
      }
    } catch (error) {
      console.error('Error deleting:', error);
      const errorMessage = error.response?.data?.error || 'Failed to delete';
      showToast(errorMessage, 'error');
    } finally {
      setDeleteConfirm(null);
    }
  };

  const handleStructureUpdate = async (action, data) => {
    switch (action) {
      case 'add-chapter':
        setShowNewChapterModal(true);
        break;
      case 'delete-chapter':
        handleDeleteChapter(data);
        break;
      case 'chapter':
        await handleUpdateChapter(data.id, data.title);
        break;
      case 'add-topic':
        setSelectedTopic({ chapter_id: data });
        setShowTopicEditor(true);
        break;
      case 'select-topic':
        await fetchTopicDetail(data);
        break;
      case 'delete-topic':
        setDeleteConfirm({
          type: 'topic',
          id: data,
          message: 'Are you sure you want to delete this topic?'
        });
        break;
      case 'topic':
        await handleUpdateTopic(data.id, { name: data.name });
        break;
      case 'ai-topic':
        await fetchTopicDetail(data);
        break;
    }
  };

  const fetchTopicDetail = async (topicId) => {
    try {
      const data = await noteService.getTopicDetail(topicId);
      setSelectedTopic(data);
      setShowTopicEditor(true);
    } catch (error) {
      console.error('Error fetching topic:', error);
      showToast('Failed to load topic', 'error');
    }
  };

  const handleSaveTopic = async (topicData) => {
    try {
      if (selectedTopic?.id) {
        await noteService.updateTopic(selectedTopic.id, topicData);
        showToast('Topic updated successfully!');
      } else {
        await noteService.createTopic({
          ...topicData,
          chapter_id: selectedTopic.chapter_id
        });
        showToast('Topic created successfully!');
      }
      
      await fetchNoteDetail(selectedNote.id);
      setShowTopicEditor(false);
      setSelectedTopic(null);
    } catch (error) {
      console.error('Error saving topic:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to save topic';
      throw new Error(errorMessage);
    }
  };

  const handleUpdateTopic = async (topicId, topicData) => {
    try {
      await noteService.updateTopic(topicId, topicData);
      await fetchNoteDetail(selectedNote.id);
      showToast('Topic updated successfully!');
    } catch (error) {
      console.error('Error updating topic:', error);
      showToast('Failed to update topic', 'error');
    }
  };

  const handleAIAction = async (action, input, language) => {
    try {
      if (!selectedTopic?.id) {
        throw new Error('Please save the topic first before using AI features');
      }
      
      const data = await noteService.performAIAction(selectedTopic.id, {
        action_type: action,
        input_content: input,
        language: language
      });
      
      // Show success message based on action
      const actionMessages = {
        'generate_explanation': 'Explanation generated successfully!',
        'improve_explanation': 'Explanation improved successfully!',
        'summarize_explanation': 'Summary generated successfully!',
        'generate_code': 'Code generated successfully!'
      };
      showToast(actionMessages[action] || 'AI action completed!', 'info');
      
      return data.generated_content;
    } catch (error) {
      console.error('AI action error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'AI action failed';
      throw new Error(errorMessage);
    }
  };

  const handleExportPDF = async () => {
    if (!selectedNote) return;
    
    try {
      setExporting(true);
      await noteService.exportNotePDF(selectedNote.id);
      showToast('PDF exported successfully!');
    } catch (error) {
      console.error('PDF export error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to export PDF';
      showToast(errorMessage, 'error');
    } finally {
      setExporting(false);
    }
  };

  const handleDeleteNote = () => {
    if (!selectedNote) return;
    setDeleteConfirm({
      type: 'note',
      id: selectedNote.id,
      message: `Are you sure you want to delete "${selectedNote.title}" and all its content?`
    });
  };

  const filteredNotes = notes.filter(note => {
    const matchesSearch = note.title.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'all' || note.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideInRight {
          from { opacity: 0; transform: translateX(20px); }
          to { opacity: 1; transform: translateX(0); }
        }
        @keyframes slideDown {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Toast Notifications */}
      {toast && (
        <div 
          className="fixed top-4 right-4 z-50 animate-slideDown"
          style={{ animation: 'slideDown 0.3s ease-out' }}
        >
          <div className={`flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg ${
            toast.type === 'success' ? 'bg-green-50 border-l-4 border-green-500' :
            toast.type === 'error' ? 'bg-red-50 border-l-4 border-red-500' :
            'bg-blue-50 border-l-4 border-blue-500'
          }`}>
            {toast.type === 'success' && <CheckCircle2 className="text-green-600" size={20} />}
            {toast.type === 'error' && <AlertCircle className="text-red-600" size={20} />}
            {toast.type === 'info' && <Info className="text-blue-600" size={20} />}
            <span className={`text-sm font-medium ${
              toast.type === 'success' ? 'text-green-800' :
              toast.type === 'error' ? 'text-red-800' :
              'text-blue-800'
            }`}>
              {toast.message}
            </span>
            <button 
              onClick={() => setToast(null)}
              className="ml-2 text-gray-400 hover:text-gray-600"
            >
              <X size={16} />
            </button>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full animate-fadeIn">
            <div className="flex items-start gap-4 mb-4">
              <div className="p-3 bg-red-100 rounded-full">
                <AlertCircle className="text-red-600" size={24} />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold mb-2">Confirm Deletion</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {deleteConfirm.message}
                </p>
              </div>
            </div>
            
            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setDeleteConfirm(null)}
                className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 transition"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b dark:border-gray-700">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                📚 Study Notes
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Organize your learning with structured chapters and topics
              </p>
            </div>
            <button
              onClick={() => setShowNewNoteModal(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all duration-200 transform hover:scale-105 shadow-md hover:shadow-lg"
            >
              <Plus size={20} />
              New Note
            </button>
          </div>

          {/* Filters */}
          <div className="flex gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search notes..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
            >
              <option value="all">All Notes</option>
              <option value="draft">Drafts</option>
              <option value="published">Published</option>
            </select>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Notes List */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-4 max-h-[calc(100vh-300px)] overflow-y-auto">
              <h3 className="font-semibold mb-4">Your Notes ({filteredNotes.length})</h3>
              
              {loading ? (
                <div className="text-center py-8">
                  <Loader size={32} className="animate-spin mx-auto text-blue-600" />
                </div>
              ) : filteredNotes.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <FileText size={48} className="mx-auto mb-3 opacity-50" />
                  <p className="text-sm">No notes found</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {filteredNotes.map((note, index) => (
                    <div
                      key={note.id}
                      onClick={() => fetchNoteDetail(note.id)}
                      className={`p-3 rounded-lg cursor-pointer transition-all duration-300 transform hover:scale-[1.02] ${
                        selectedNote?.id === note.id
                          ? 'bg-blue-50 dark:bg-blue-900 border-l-4 border-blue-600 shadow-md'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700 hover:shadow-sm'
                      }`}
                      style={{ animation: `fadeIn 0.3s ease-out ${index * 0.05}s both` }}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium truncate">{note.title}</h4>
                          <div className="flex items-center gap-2 mt-1 text-xs text-gray-600 dark:text-gray-400">
                            <span>{note.chapter_count || 0} chapters</span>
                            <span>•</span>
                            <span>{note.total_topics || 0} topics</span>
                          </div>
                        </div>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          note.status === 'published'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {note.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {selectedNote ? (
              <div className="space-y-6" style={{ animation: 'slideInRight 0.4s ease-out' }}>
                {/* Note Header with Editable Title */}
                <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-6">
                  <div className="flex items-center justify-between mb-4">
                    {editingNoteTitle ? (
                      <div className="flex-1 flex items-center gap-2">
                        <input
                          type="text"
                          value={noteTitleValue}
                          onChange={(e) => setNoteTitleValue(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handleUpdateNoteTitle();
                            if (e.key === 'Escape') {
                              setEditingNoteTitle(false);
                              setNoteTitleValue(selectedNote.title);
                            }
                          }}
                          className="flex-1 px-3 py-2 text-2xl font-bold border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500"
                          autoFocus
                        />
                        <button
                          onClick={handleUpdateNoteTitle}
                          className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition"
                          title="Save"
                        >
                          <Save size={20} />
                        </button>
                        <button
                          onClick={() => {
                            setEditingNoteTitle(false);
                            setNoteTitleValue(selectedNote.title);
                          }}
                          className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                          title="Cancel"
                        >
                          <X size={20} />
                        </button>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 group">
                        <h2 className="text-2xl font-bold">{selectedNote.title}</h2>
                        <button
                          onClick={() => setEditingNoteTitle(true)}
                          className="p-2 opacity-0 group-hover:opacity-100 text-gray-600 hover:bg-gray-100 rounded-lg transition"
                          title="Edit title"
                        >
                          <Edit size={18} />
                        </button>
                      </div>
                    )}
                    <div className="flex gap-2">
                      <button
                        onClick={handleExportPDF}
                        disabled={exporting}
                        className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-all duration-200 transform hover:scale-105 shadow-md hover:shadow-lg"
                      >
                        {exporting ? (
                          <Loader size={16} className="animate-spin" />
                        ) : (
                          <Download size={16} />
                        )}
                        Export PDF
                      </button>
                      <button
                        onClick={handleDeleteNote}
                        className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-all duration-200 transform hover:scale-110"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  </div>

                  <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <span>{selectedNote.chapters?.length || 0} chapters</span>
                    <span>•</span>
                    <span>
                      {selectedNote.chapters?.reduce((sum, ch) => sum + (ch.topics?.length || 0), 0) || 0} topics
                    </span>
                    <span>•</span>
                    <span>Updated {new Date(selectedNote.updated_at).toLocaleDateString()}</span>
                  </div>
                </div>

                {/* Note Structure */}
                <NoteStructure
                  note={selectedNote}
                  onUpdate={handleStructureUpdate}
                />
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-20 text-center">
                <FileText size={64} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">No note selected</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Select a note from the list or create a new one
                </p>
                <button
                  onClick={() => setShowNewNoteModal(true)}
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 mx-auto"
                >
                  <Plus size={20} />
                  Create New Note
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Modals */}
      {showNewNoteModal && (
        <Modal
          title="Create New Note"
          onClose={() => setShowNewNoteModal(false)}
          onSubmit={handleCreateNote}
          placeholder="Enter note title..."
        />
      )}

      {showNewChapterModal && (
        <Modal
          title="Create New Chapter"
          onClose={() => setShowNewChapterModal(false)}
          onSubmit={handleCreateChapter}
          placeholder="Enter chapter title..."
        />
      )}

      {showTopicEditor && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <TopicEditor
              topic={selectedTopic?.id ? selectedTopic : null}
              onSave={handleSaveTopic}
              onCancel={() => {
                setShowTopicEditor(false);
                setSelectedTopic(null);
              }}
              onAIAction={handleAIAction}
            />
          </div>
        </div>
      )}
    </div>
  );
};

// Simple Modal Component
const Modal = ({ title, onClose, onSubmit, placeholder }) => {
  const [value, setValue] = useState('');

  const handleSubmit = () => {
    if (value.trim()) {
      onSubmit(value.trim());
      setValue('');
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full animate-fadeIn">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold">{title}</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>
        
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder={placeholder}
          className="w-full px-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 mb-4"
          autoFocus
        />
        
        <div className="flex gap-2">
          <button
            onClick={handleSubmit}
            disabled={!value.trim()}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Create
          </button>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300"
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default NotesPage;