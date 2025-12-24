// FILE: src/components/notes/NoteEditor.jsx
// ============================================================================

import { useState } from 'react';
import { 
  Bold, Italic, Underline, List, ListOrdered, 
  Heading1, Heading2, Code, Quote, Link as LinkIcon
} from 'lucide-react';
import Button from '@/components/common/Button';

const NoteEditor = ({ formData, onChange }) => {
  const [showLinkInput, setShowLinkInput] = useState(false);
  const [linkUrl, setLinkUrl] = useState('');

  const handleTitleChange = (e) => {
    onChange({ ...formData, title: e.target.value });
  };

  const handleContentChange = (e) => {
    onChange({ ...formData, content: e.target.value });
  };

  const handleTagsChange = (e) => {
    const tags = e.target.value.split(',').map(tag => tag.trim()).filter(Boolean);
    onChange({ ...formData, tags });
  };

  const handleStatusChange = (e) => {
    onChange({ ...formData, status: e.target.value });
  };

  const insertFormatting = (prefix, suffix = '') => {
    const textarea = document.getElementById('note-content');
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = formData.content.substring(start, end);
    const newContent =
      formData.content.substring(0, start) +
      prefix +
      selectedText +
      suffix +
      formData.content.substring(end);
    
    onChange({ ...formData, content: newContent });
    
    // Reset cursor position
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + prefix.length,
        end + prefix.length
      );
    }, 0);
  };

  const insertHeading = (level) => {
    const prefix = '#'.repeat(level) + ' ';
    insertFormatting(prefix);
  };

  const insertLink = () => {
    if (linkUrl) {
      insertFormatting('[', `](${linkUrl})`);
      setShowLinkInput(false);
      setLinkUrl('');
    } else {
      setShowLinkInput(true);
    }
  };

  const toolbarButtons = [
    { icon: Heading1, action: () => insertHeading(1), title: 'Heading 1' },
    { icon: Heading2, action: () => insertHeading(2), title: 'Heading 2' },
    { icon: Bold, action: () => insertFormatting('**', '**'), title: 'Bold' },
    { icon: Italic, action: () => insertFormatting('*', '*'), title: 'Italic' },
    { icon: Underline, action: () => insertFormatting('<u>', '</u>'), title: 'Underline' },
    { icon: List, action: () => insertFormatting('- '), title: 'Bullet List' },
    { icon: ListOrdered, action: () => insertFormatting('1. '), title: 'Numbered List' },
    { icon: Code, action: () => insertFormatting('`', '`'), title: 'Inline Code' },
    { icon: Quote, action: () => insertFormatting('> '), title: 'Quote' },
    { icon: LinkIcon, action: insertLink, title: 'Insert Link' },
  ];

  return (
    <div className="space-y-4">
      {/* Title Input */}
      <div>
        <input
          type="text"
          placeholder="Enter note title..."
          value={formData.title}
          onChange={handleTitleChange}
          className="input-field text-2xl font-semibold w-full"
          required
        />
      </div>

      {/* Metadata Row */}
      <div className="grid md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium mb-2">Status</label>
          <select
            value={formData.status}
            onChange={handleStatusChange}
            className="input-field w-full"
          >
            <option value="draft">Draft</option>
            <option value="published">Published</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Tags (comma-separated)</label>
          <input
            type="text"
            placeholder="python, web-dev, tutorial"
            value={formData.tags.join(', ')}
            onChange={handleTagsChange}
            className="input-field w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Session Date</label>
          <input
            type="date"
            value={formData.session_date || ''}
            onChange={(e) => onChange({ ...formData, session_date: e.target.value })}
            className="input-field w-full"
          />
        </div>
      </div>

      {/* Formatting Toolbar */}
      <div className="border dark:border-gray-700 rounded-lg p-2 flex flex-wrap gap-1">
        {toolbarButtons.map((btn, idx) => (
          <button
            key={idx}
            type="button"
            onClick={btn.action}
            title={btn.title}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <btn.icon size={18} />
          </button>
        ))}

        {showLinkInput && (
          <div className="flex items-center gap-2 ml-2">
            <input
              type="url"
              placeholder="Enter URL..."
              value={linkUrl}
              onChange={(e) => setLinkUrl(e.target.value)}
              className="input-field text-sm py-1"
              autoFocus
            />
            <Button
              variant="secondary"
              onClick={insertLink}
              className="text-xs"
            >
              Insert
            </Button>
            <Button
              variant="secondary"
              onClick={() => {
                setShowLinkInput(false);
                setLinkUrl('');
              }}
              className="text-xs"
            >
              Cancel
            </Button>
          </div>
        )}
      </div>

      {/* Content Editor */}
      <div>
        <textarea
          id="note-content"
          placeholder="Write your notes here... (Markdown supported)"
          value={formData.content}
          onChange={handleContentChange}
          className="input-field min-h-[500px] font-mono text-sm w-full resize-y"
          required
        />
      </div>

      {/* Help Text */}
      <div className="text-sm text-gray-600 dark:text-gray-400">
        <p className="font-medium mb-1">Markdown Tips:</p>
        <ul className="list-disc list-inside space-y-1">
          <li># Heading 1, ## Heading 2</li>
          <li>**bold**, *italic*, `code`</li>
          <li>- Bullet list, 1. Numbered list</li>
          <li>&gt; Quote, [link](url)</li>
          <li>```language for code blocks</li>
        </ul>
      </div>
    </div>
  );
};

export default NoteEditor;