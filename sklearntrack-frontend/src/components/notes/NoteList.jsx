// FILE: src/components/notes/NoteList.jsx
// ============================================================================

import { FileText, Clock, Tag } from 'lucide-react';
import Card from '@/components/common/Card';
import Skeleton from 'react-loading-skeleton';
import 'react-loading-skeleton/dist/skeleton.css';

const NoteList = ({ notes, selectedNote, onSelectNote, loading }) => {
  if (loading) {
    return (
      <Card className="max-h-[calc(100vh-300px)] overflow-y-auto">
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="p-3">
              <Skeleton height={20} className="mb-2" />
              <Skeleton height={15} width="60%" />
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (notes.length === 0) {
    return (
      <Card className="text-center py-12">
        <FileText size={48} className="mx-auto text-gray-400 mb-4" />
        <p className="text-gray-600 dark:text-gray-400">No notes found</p>
      </Card>
    );
  }

  return (
    <Card className="max-h-[calc(100vh-300px)] overflow-y-auto">
      <div className="space-y-2">
        {notes.map((note) => (
          <div
            key={note.id}
            onClick={() => onSelectNote(note)}
            className={`p-3 rounded-lg cursor-pointer transition-all ${
              selectedNote?.id === note.id
                ? 'bg-primary-50 dark:bg-primary-900 border-l-4 border-primary-600'
                : 'hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
          >
            <div className="flex items-start gap-2 mb-2">
              <FileText
                size={16}
                className={`mt-1 ${
                  selectedNote?.id === note.id ? 'text-primary-600' : 'text-gray-400'
                }`}
              />
              <div className="flex-1 min-w-0">
                <h4 className="font-medium truncate">{note.title}</h4>
                <div className="flex items-center gap-2 mt-1 text-xs text-gray-600 dark:text-gray-400">
                  <Clock size={12} />
                  <span>{new Date(note.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>

            {note.tags && note.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {note.tags.slice(0, 2).map((tag, i) => (
                  <span
                    key={i}
                    className="text-xs bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded"
                  >
                    {tag}
                  </span>
                ))}
                {note.tags.length > 2 && (
                  <span className="text-xs text-gray-500">+{note.tags.length - 2}</span>
                )}
              </div>
            )}

            <div className="flex items-center gap-2 mt-2 text-xs">
              <span
                className={`px-2 py-0.5 rounded-full ${
                  note.status === 'published'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {note.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default NoteList;