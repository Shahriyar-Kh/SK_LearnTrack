// FILE: src/components/notes/NoteViewer.jsx
// ============================================================================

import { Tag, Calendar, BookOpen } from 'lucide-react';

const NoteViewer = ({ note }) => {
  // Simple markdown to HTML converter
  const formatContent = (content) => {
    if (!content) return '';
    
    let formatted = content
      // Headers
      .replace(/^### (.*$)/gim, '<h3 class="text-xl font-bold mt-6 mb-3">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-bold mt-6 mb-3">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold mt-6 mb-4">$1</h1>')
      // Bold, Italic
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Code
      .replace(/`(.+?)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm">$1</code>')
      // Links
      .replace(/\[([^\]]+)\]\(([^\)]+)\)/g, '<a href="$2" class="text-primary-600 hover:underline" target="_blank">$1</a>')
      // Line breaks
      .replace(/\n/g, '<br />');
    
    return formatted;
  };

  return (
    <div>
      {/* Note Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-4">{note.title}</h1>
        
        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
          {note.created_at && (
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span>Created: {new Date(note.created_at).toLocaleDateString()}</span>
            </div>
          )}
          
          {note.updated_at && (
            <div className="flex items-center gap-2">
              <Calendar size={16} />
              <span>Updated: {new Date(note.updated_at).toLocaleDateString()}</span>
            </div>
          )}
          
          {note.course && (
            <div className="flex items-center gap-2">
              <BookOpen size={16} />
              <span>Course: {note.course.title}</span>
            </div>
          )}
        </div>

        {note.tags && note.tags.length > 0 && (
          <div className="flex flex-wrap items-center gap-2 mt-4">
            <Tag size={16} className="text-gray-400" />
            {note.tags.map((tag, i) => (
              <span
                key={i}
                className="text-xs bg-primary-100 text-primary-800 px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Note Content */}
      <div
        className="prose dark:prose-invert max-w-none"
        dangerouslySetInnerHTML={{ __html: formatContent(note.content) }}
      />

      {/* Table of Contents */}
      {note.toc && note.toc.length > 0 && (
        <div className="mt-8 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
          <h3 className="font-bold mb-3">Table of Contents</h3>
          <ul className="space-y-2">
            {note.toc.map((item, i) => (
              <li key={i} style={{ marginLeft: `${(item.level - 1) * 20}px` }}>
                <a href={`#${item.slug}`} className="text-primary-600 hover:underline">
                  {item.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default NoteViewer;
