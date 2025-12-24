// FILE: src/pages/NotesPage.jsx
// ============================================================================

import { useEffect, useState } from 'react';
import { 
  Plus, Search, FileText, Trash2, Edit, Save, X, 
  Download, Upload, Youtube, Wand2, History, 
  BookOpen, Code, Link, FileCode, Clock, Tag
} from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import NoteEditor from '@/components/notes/NoteEditor';
import NoteList from '@/components/notes/NoteList';
import NoteViewer from '@/components/notes/NoteViewer';
import AIActionsPanel from '@/components/notes/AIActionsPanel';
import SourceManager from '@/components/notes/SourceManager';
import CodeSnippetManager from '@/components/notes/CodeSnippetManager';
import VersionHistory from '@/components/notes/VersionHistory';
import YouTubeImporter from '@/components/notes/YouTubeImporter';
import { noteService } from '@/services/note.service';
import toast from 'react-hot-toast';

const NotesPage = () => {
  const [notes, setNotes] = useState([]);
  const [filteredNotes, setFilteredNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  
  // Editor state
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    content_json: {},
    tags: [],
    status: 'draft',
    course: null,
    topic: null,
    subtopic: null,
  });

  // Panel visibility
  const [showAIPanel, setShowAIPanel] = useState(false);
  const [showSourceManager, setShowSourceManager] = useState(false);
  const [showCodeSnippets, setShowCodeSnippets] = useState(false);
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [showYouTubeImporter, setShowYouTubeImporter] = useState(false);

  useEffect(() => {
    fetchNotes();
  }, []);

  useEffect(() => {
    filterNotes();
  }, [notes, search, statusFilter]);

  const fetchNotes = async () => {
    try {
      const data = await noteService.getNotes();
      setNotes(data.results || []);
    } catch (error) {
      console.error('Error fetching notes:', error);
      toast.error('Failed to fetch notes');
    } finally {
      setLoading(false);
    }
  };

  const filterNotes = () => {
    let filtered = notes;

    // Search filter
    if (search) {
      filtered = filtered.filter((note) =>
        note.title.toLowerCase().includes(search.toLowerCase()) ||
        note.content.toLowerCase().includes(search.toLowerCase()) ||
        note.tags.some(tag => tag.toLowerCase().includes(search.toLowerCase()))
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((note) => note.status === statusFilter);
    }

    setFilteredNotes(filtered);
  };

  const handleCreateNote = () => {
    setSelectedNote(null);
    setIsEditing(true);
    setFormData({
      title: '',
      content: '',
      content_json: {},
      tags: [],
      status: 'draft',
      course: null,
      topic: null,
      subtopic: null,
    });
  };

  const handleSelectNote = async (note) => {
    try {
      const fullNote = await noteService.getNoteDetail(note.id);
      setSelectedNote(fullNote);
      setFormData({
        title: fullNote.title,
        content: fullNote.content,
        content_json: fullNote.content_json || {},
        tags: fullNote.tags || [],
        status: fullNote.status,
        course: fullNote.course,
        topic: fullNote.topic,
        subtopic: fullNote.subtopic,
      });
      setIsEditing(false);
    } catch (error) {
      toast.error('Failed to load note');
    }
  };

  const handleSaveNote = async () => {
    if (!formData.title.trim()) {
      toast.error('Please enter a note title');
      return;
    }

    try {
      if (selectedNote) {
        await noteService.updateNote(selectedNote.id, formData);
        toast.success('Note updated!');
      } else {
        const newNote = await noteService.createNote(formData);
        setSelectedNote(newNote);
        toast.success('Note created!');
      }
      setIsEditing(false);
      fetchNotes();
    } catch (error) {
      toast.error('Failed to save note');
    }
  };

  const handleDeleteNote = async (id) => {
    if (window.confirm('Delete this note? This action cannot be undone.')) {
      try {
        await noteService.deleteNote(id);
        toast.success('Note deleted');
        setSelectedNote(null);
        fetchNotes();
      } catch (error) {
        toast.error('Failed to delete note');
      }
    }
  };

  const handleDuplicateNote = async () => {
    if (!selectedNote) return;
    try {
      const duplicateData = {
        ...formData,
        title: `${formData.title} (Copy)`,
        status: 'draft',
      };
      const newNote = await noteService.createNote(duplicateData);
      toast.success('Note duplicated!');
      setSelectedNote(newNote);
      fetchNotes();
    } catch (error) {
      toast.error('Failed to duplicate note');
    }
  };

  const handleExportPDF = async () => {
    if (!selectedNote) return;
    try {
      await noteService.exportNoteToPDF(selectedNote.id);
      toast.success('PDF export started!');
    } catch (error) {
      toast.error('Failed to export PDF');
    }
  };

  const handleAIAction = async (action, content) => {
    try {
      const result = await noteService.performAIAction({
        action_type: action,
        content: content || formData.content,
        note_id: selectedNote?.id,
      });
      
      // Update content with AI result
      setFormData({
        ...formData,
        content: result.generated_content,
      });
      
      toast.success('AI action completed!');
    } catch (error) {
      toast.error('AI action failed');
    }
  };

  const handleYouTubeImport = async (videoData) => {
    try {
      const result = await noteService.importYouTube(videoData);
      toast.success('YouTube video imported!');
      
      if (result.note_id) {
        const newNote = await noteService.getNoteDetail(result.note_id);
        setSelectedNote(newNote);
        handleSelectNote(newNote);
      }
      
      setShowYouTubeImporter(false);
      fetchNotes();
    } catch (error) {
      toast.error('Failed to import YouTube video');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Advanced Note Vault
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Create, organize, and enhance your learning notes with AI
            </p>
          </div>
          
          <div className="flex gap-2">
            <Button
              variant="secondary"
              onClick={() => setShowYouTubeImporter(true)}
              className="flex items-center gap-2"
            >
              <Youtube size={20} />
              Import YouTube
            </Button>
            <Button onClick={handleCreateNote} className="flex items-center gap-2">
              <Plus size={20} />
              New Note
            </Button>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search notes by title, content, or tags..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field pl-10 w-full"
            />
          </div>
          
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input-field md:w-48"
          >
            <option value="all">All Notes</option>
            <option value="draft">Drafts</option>
            <option value="published">Published</option>
          </select>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Notes List - Left Sidebar */}
          <div className="lg:col-span-1">
            <NoteList
              notes={filteredNotes}
              selectedNote={selectedNote}
              onSelectNote={handleSelectNote}
              loading={loading}
            />
          </div>

          {/* Note Editor/Viewer - Main Area */}
          <div className="lg:col-span-3">
            {selectedNote || isEditing ? (
              <Card className="min-h-[600px]">
                {/* Toolbar */}
                <div className="flex items-center justify-between mb-6 pb-4 border-b dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <h2 className="text-2xl font-bold">
                      {isEditing ? (selectedNote ? 'Edit Note' : 'New Note') : 'View Note'}
                    </h2>
                    {selectedNote && !isEditing && (
                      <span className={`text-xs px-2 py-1 rounded-full ${
                        selectedNote.status === 'published'
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {selectedNote.status}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex gap-2">
                    {isEditing ? (
                      <>
                        <Button onClick={handleSaveNote} className="flex items-center gap-2">
                          <Save size={16} />
                          Save
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={() => {
                            setIsEditing(false);
                            if (selectedNote) {
                              handleSelectNote(selectedNote);
                            } else {
                              setSelectedNote(null);
                            }
                          }}
                          className="flex items-center gap-2"
                        >
                          <X size={16} />
                          Cancel
                        </Button>
                      </>
                    ) : (
                      <>
                        <Button
                          variant="secondary"
                          onClick={() => setIsEditing(true)}
                          className="flex items-center gap-2"
                        >
                          <Edit size={16} />
                          Edit
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={() => setShowAIPanel(!showAIPanel)}
                          className="flex items-center gap-2"
                        >
                          <Wand2 size={16} />
                          AI Tools
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={() => setShowSourceManager(!showSourceManager)}
                          className="flex items-center gap-2"
                        >
                          <Link size={16} />
                          Sources
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={() => setShowCodeSnippets(!showCodeSnippets)}
                          className="flex items-center gap-2"
                        >
                          <Code size={16} />
                          Code
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={() => setShowVersionHistory(!showVersionHistory)}
                          className="flex items-center gap-2"
                        >
                          <History size={16} />
                          History
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={handleExportPDF}
                          className="flex items-center gap-2"
                        >
                          <Download size={16} />
                          Export PDF
                        </Button>
                        <Button
                          variant="secondary"
                          onClick={handleDuplicateNote}
                          className="flex items-center gap-2"
                        >
                          <FileText size={16} />
                          Duplicate
                        </Button>
                        <Button
                          variant="danger"
                          onClick={() => handleDeleteNote(selectedNote.id)}
                          className="flex items-center gap-2"
                        >
                          <Trash2 size={16} />
                          Delete
                        </Button>
                      </>
                    )}
                  </div>
                </div>

                {/* Editor or Viewer */}
                {isEditing ? (
                  <NoteEditor
                    formData={formData}
                    onChange={setFormData}
                  />
                ) : (
                  <NoteViewer note={selectedNote} />
                )}

                {/* Side Panels */}
                {showAIPanel && !isEditing && (
                  <AIActionsPanel
                    noteContent={formData.content}
                    onAction={handleAIAction}
                    onClose={() => setShowAIPanel(false)}
                  />
                )}

                {showSourceManager && !isEditing && (
                  <SourceManager
                    noteId={selectedNote?.id}
                    sources={selectedNote?.sources || []}
                    onUpdate={fetchNotes}
                    onClose={() => setShowSourceManager(false)}
                  />
                )}

                {showCodeSnippets && !isEditing && (
                  <CodeSnippetManager
                    noteId={selectedNote?.id}
                    snippets={selectedNote?.code_snippets || []}
                    onUpdate={fetchNotes}
                    onClose={() => setShowCodeSnippets(false)}
                  />
                )}

                {showVersionHistory && !isEditing && (
                  <VersionHistory
                    noteId={selectedNote?.id}
                    onRestore={(version) => {
                      setFormData({
                        ...formData,
                        content: version.content,
                        content_json: version.content_json,
                      });
                      setIsEditing(true);
                      setShowVersionHistory(false);
                    }}
                    onClose={() => setShowVersionHistory(false)}
                  />
                )}
              </Card>
            ) : (
              <Card className="text-center py-20">
                <FileText size={64} className="mx-auto text-gray-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">No note selected</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-6">
                  Select a note from the list or create a new one
                </p>
                <Button onClick={handleCreateNote} className="flex items-center gap-2 mx-auto">
                  <Plus size={20} />
                  Create New Note
                </Button>
              </Card>
            )}
          </div>
        </div>
      </div>

      {/* YouTube Importer Modal */}
      {showYouTubeImporter && (
        <YouTubeImporter
          onImport={handleYouTubeImport}
          onClose={() => setShowYouTubeImporter(false)}
        />
      )}
    </div>
  );
};

export default NotesPage;