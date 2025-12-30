import { useState } from 'react';
import { 
  ChevronDown, ChevronRight, Plus, Edit, Trash2, 
  FileText, Code, Link, Wand2, Save, X
} from 'lucide-react';

const NoteStructure = ({ note, onUpdate }) => {
  const [expandedChapters, setExpandedChapters] = useState(new Set());
  const [editingItem, setEditingItem] = useState(null);
  const [editValue, setEditValue] = useState('');

  const toggleChapter = (chapterId) => {
    const newExpanded = new Set(expandedChapters);
    if (newExpanded.has(chapterId)) {
      newExpanded.delete(chapterId);
    } else {
      newExpanded.add(chapterId);
    }
    setExpandedChapters(newExpanded);
  };

  const startEdit = (type, id, currentValue) => {
    setEditingItem({ type, id });
    setEditValue(currentValue);
  };

  const cancelEdit = () => {
    setEditingItem(null);
    setEditValue('');
  };

  const saveEdit = async () => {
    if (!editValue.trim()) {
      cancelEdit();
      return;
    }
    
    // Call the update handler with the correct structure
    if (editingItem.type === 'chapter') {
      await onUpdate('chapter', { id: editingItem.id, title: editValue });
    } else if (editingItem.type === 'topic') {
      await onUpdate('topic', { id: editingItem.id, name: editValue });
    }
    cancelEdit();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      saveEdit();
    } else if (e.key === 'Escape') {
      cancelEdit();
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Note Structure</h3>
        <button 
          onClick={() => onUpdate('add-chapter')}
          className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm transition-all duration-200 transform hover:scale-105 shadow-sm hover:shadow-md"
        >
          <Plus size={16} />
          Add Chapter
        </button>
      </div>

      <div className="space-y-1">
        {note.chapters?.map((chapter, index) => (
          <div 
            key={chapter.id}
            className="animate-fadeIn"
            style={{
              animation: `fadeIn 0.3s ease-out ${index * 0.1}s both`
            }}
          >
            {/* Chapter Row */}
            <div className="group flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-all duration-200 hover:shadow-sm">
              <button
                onClick={() => toggleChapter(chapter.id)}
                className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-transform duration-200 hover:scale-110"
              >
                {expandedChapters.has(chapter.id) ? (
                  <ChevronDown size={16} />
                ) : (
                  <ChevronRight size={16} />
                )}
              </button>

              <FileText size={16} className="text-blue-600" />

              {editingItem?.type === 'chapter' && editingItem?.id === chapter.id ? (
                <div className="flex-1 flex items-center gap-2">
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    className="flex-1 px-2 py-1 text-sm border dark:border-gray-600 rounded bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500"
                    autoFocus
                  />
                  <button
                    onClick={saveEdit}
                    className="p-1 text-green-600 hover:bg-green-50 rounded transition"
                    title="Save"
                  >
                    <Save size={14} />
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="p-1 text-gray-600 hover:bg-gray-100 rounded transition"
                    title="Cancel"
                  >
                    <X size={14} />
                  </button>
                </div>
              ) : (
                <>
                  <span className="flex-1 font-medium text-sm">
                    {chapter.title}
                  </span>
                  <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        startEdit('chapter', chapter.id, chapter.title);
                      }}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                      title="Edit Chapter"
                    >
                      <Edit size={14} />
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        onUpdate('delete-chapter', chapter.id);
                      }}
                      className="p-1 hover:bg-red-100 text-red-600 rounded transition"
                      title="Delete Chapter"
                    >
                      <Trash2 size={14} />
                    </button>
                    <button 
                      onClick={(e) => {
                        e.stopPropagation();
                        onUpdate('add-topic', chapter.id);
                      }}
                      className="p-1 hover:bg-blue-100 text-blue-600 rounded transition"
                      title="Add Topic"
                    >
                      <Plus size={14} />
                    </button>
                  </div>
                </>
              )}

              <span className="text-xs text-gray-500 dark:text-gray-400">
                {chapter.topics?.length || 0} topics
              </span>
            </div>

            {/* Topics (when expanded) */}
            {expandedChapters.has(chapter.id) && (
              <div className="ml-8 mt-1 space-y-1 transition-all duration-300">
                {chapter.topics?.map((topic, topicIndex) => (
                  <div
                    key={topic.id}
                    className="group flex items-center gap-2 p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg cursor-pointer transition-all duration-200 transform hover:translate-x-1"
                    onClick={() => onUpdate('select-topic', topic.id)}
                    style={{
                      animation: `fadeIn 0.2s ease-out ${topicIndex * 0.05}s both`
                    }}
                  >
                    <div className="w-6" />

                    {editingItem?.type === 'topic' && editingItem?.id === topic.id ? (
                      <div className="flex-1 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                        <input
                          type="text"
                          value={editValue}
                          onChange={(e) => setEditValue(e.target.value)}
                          onKeyDown={handleKeyPress}
                          className="flex-1 px-2 py-1 text-sm border dark:border-gray-600 rounded bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500"
                          autoFocus
                        />
                        <button
                          onClick={saveEdit}
                          className="p-1 text-green-600 hover:bg-green-50 rounded transition"
                          title="Save"
                        >
                          <Save size={14} />
                        </button>
                        <button
                          onClick={cancelEdit}
                          className="p-1 text-gray-600 hover:bg-gray-100 rounded transition"
                          title="Cancel"
                        >
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <>
                        <span className="flex-1 text-sm">{topic.name}</span>

                        {/* Topic indicators */}
                        <div className="flex items-center gap-1">
                          {topic.has_explanation && (
                            <span className="p-1 bg-green-100 text-green-700 rounded" title="Has explanation">
                              <FileText size={12} />
                            </span>
                          )}
                          {topic.has_code && (
                            <span className="p-1 bg-purple-100 text-purple-700 rounded" title="Has code">
                              <Code size={12} />
                            </span>
                          )}
                          {topic.has_source && (
                            <span className="p-1 bg-blue-100 text-blue-700 rounded" title="Has source">
                              <Link size={12} />
                            </span>
                          )}
                        </div>

                        <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              startEdit('topic', topic.id, topic.name);
                            }}
                            className="p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition"
                            title="Edit Topic"
                          >
                            <Edit size={14} />
                          </button>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              onUpdate('ai-topic', topic.id);
                            }}
                            className="p-1 hover:bg-purple-100 text-purple-600 rounded transition" 
                            title="AI Actions"
                          >
                            <Wand2 size={14} />
                          </button>
                          <button 
                            onClick={(e) => {
                              e.stopPropagation();
                              onUpdate('delete-topic', topic.id);
                            }}
                            className="p-1 hover:bg-red-100 text-red-600 rounded transition"
                            title="Delete Topic"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                ))}

                {/* Add Topic Button */}
                <button 
                  onClick={() => onUpdate('add-topic', chapter.id)}
                  className="ml-6 flex items-center gap-2 px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg w-full transition-all duration-200 transform hover:scale-[1.02]"
                >
                  <Plus size={14} />
                  Add Topic
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {(!note.chapters || note.chapters.length === 0) && (
        <div className="text-center py-8 text-gray-500">
          <FileText size={48} className="mx-auto mb-3 opacity-50" />
          <p className="text-sm">No chapters yet. Add your first chapter to get started.</p>
        </div>
      )}
    </div>
  );
};

export default NoteStructure;