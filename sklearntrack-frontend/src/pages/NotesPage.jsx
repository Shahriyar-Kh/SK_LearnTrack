// FILE: src/pages/NotesPage.jsx
// ============================================================================

import { useEffect, useState } from 'react';
import { Plus, Search, FileText, Trash2, Edit } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import Card from '@/components/common/Card';
import Button from '@/components/common/Button';
import { noteService } from '@/services/note.service';
import toast from 'react-hot-toast';

const NotesPage = () => {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedNote, setSelectedNote] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    tags: [],
  });

  useEffect(() => {
    fetchNotes();
  }, []);

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

  const handleCreateNote = () => {
    setSelectedNote(null);
    setIsEditing(true);
    setFormData({ title: '', content: '', tags: [] });
  };

  const handleSaveNote = async () => {
    try {
      if (selectedNote) {
        await noteService.updateNote(selectedNote.id, formData);
        toast.success('Note updated!');
      } else {
        await noteService.createNote(formData);
        toast.success('Note created!');
      }
      setIsEditing(false);
      fetchNotes();
    } catch (error) {
      toast.error('Failed to save note');
    }
  };

  const handleDeleteNote = async (id) => {
    if (window.confirm('Delete this note?')) {
      try {
        await noteService.deleteNote(id);
        toast.success('Note deleted');
        fetchNotes();
      } catch (error) {
        toast.error('Failed to delete note');
      }
    }
  };

  const filteredNotes = notes.filter((note) =>
    note.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      
      <div className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Notes & Code Vault
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Organize your learning notes and code snippets
            </p>
          </div>
          <Button onClick={handleCreateNote}>
            <Plus size={20} className="mr-2" />
            New Note
          </Button>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Notes List */}
          <div className="lg:col-span-1">
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Search notes..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-field pl-10"
              />
            </div>

            <Card className="max-h-[calc(100vh-300px)] overflow-y-auto">
              {filteredNotes.length > 0 ? (
                <div className="space-y-2">
                  {filteredNotes.map((note) => (
                    <div
                      key={note.id}
                      onClick={() => {
                        setSelectedNote(note);
                        setFormData({
                          title: note.title,
                          content: note.content,
                          tags: note.tags,
                        });
                        setIsEditing(false);
                      }}
                      className={`p-3 rounded-lg cursor-pointer transition-colors ${
                        selectedNote?.id === note.id
                          ? 'bg-primary-50 dark:bg-primary-900'
                          : 'hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <FileText size={16} className="text-primary-600" />
                        <h4 className="font-medium truncate">{note.title}</h4>
                      </div>
                      <p className="text-xs text-gray-600 dark:text-gray-400">
                        {new Date(note.updated_at).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-600 dark:text-gray-400">
                    No notes yet
                  </p>
                </div>
              )}
            </Card>
          </div>

          {/* Note Editor/Viewer */}
          <div className="lg:col-span-2">
            <Card>
              {selectedNote || isEditing ? (
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-2xl font-bold">
                      {isEditing ? (selectedNote ? 'Edit Note' : 'New Note') : 'View Note'}
                    </h2>
                    <div className="flex gap-2">
                      {!isEditing && selectedNote && (
                        <>
                          <Button variant="secondary" onClick={() => setIsEditing(true)}>
                            <Edit size={16} />
                          </Button>
                          <Button variant="danger" onClick={() => handleDeleteNote(selectedNote.id)}>
                            <Trash2 size={16} />
                          </Button>
                        </>
                      )}
                    </div>
                  </div>

                  {isEditing ? (
                    <div className="space-y-4">
                      <input
                        type="text"
                        placeholder="Note title"
                        value={formData.title}
                        onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                        className="input-field text-xl font-semibold"
                      />
                      <textarea
                        placeholder="Write your note here..."
                        value={formData.content}
                        onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                        className="input-field min-h-[400px] font-mono"
                      />
                      <div className="flex gap-2">
                        <Button onClick={handleSaveNote}>Save Note</Button>
                        <Button variant="secondary" onClick={() => setIsEditing(false)}>
                          Cancel
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <h3 className="text-2xl font-semibold mb-4">{selectedNote.title}</h3>
                      <div className="prose dark:prose-invert max-w-none">
                        <pre className="whitespace-pre-wrap font-sans">{selectedNote.content}</pre>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-20">
                  <FileText size={64} className="mx-auto text-gray-400 mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No note selected</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Select a note from the list or create a new one
                  </p>
                  <Button onClick={handleCreateNote}>
                    <Plus size={20} className="mr-2" />
                    Create New Note
                  </Button>
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotesPage;

