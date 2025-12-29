import { useState, useEffect } from 'react';
import { 
  Save, X, Wand2, Code, Link, Plus, Trash2, 
  FileText, Loader, CheckCircle, Sparkles
} from 'lucide-react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import Editor from '@monaco-editor/react';

const TopicEditor = ({ topic, onSave, onCancel, onAIAction }) => {
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [aiLoading, setAiLoading] = useState(null);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    name: topic?.name || '',
    explanation: topic?.explanation?.content || '',
    code: {
      language: topic?.code_snippet?.language || 'python',
      content: topic?.code_snippet?.code || ''
    },
    source: {
      title: topic?.source?.title || '',
      url: topic?.source?.url || ''
    }
  });

  // Update form data when topic changes
  useEffect(() => {
    if (topic) {
      setFormData({
        name: topic.name || '',
        explanation: topic.explanation?.content || '',
        code: {
          language: topic.code_snippet?.language || 'python',
          content: topic.code_snippet?.code || ''
        },
        source: {
          title: topic.source?.title || '',
          url: topic.source?.url || ''
        }
      });
    }
  }, [topic]);

  const languages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
    { value: 'csharp', label: 'C#' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
    { value: 'sql', label: 'SQL' },
    { value: 'html', label: 'HTML' },
    { value: 'css', label: 'CSS' },
    { value: 'bash', label: 'Bash' },
    { value: 'json', label: 'JSON' },
    { value: 'other', label: 'Other' }
  ];

  // Monaco Editor language mapping
  const getMonacoLanguage = (lang) => {
    const mapping = {
      'cpp': 'cpp',
      'c': 'c',
      'csharp': 'csharp',
      'python': 'python',
      'javascript': 'javascript',
      'typescript': 'typescript',
      'java': 'java',
      'go': 'go',
      'rust': 'rust',
      'sql': 'sql',
      'html': 'html',
      'css': 'css',
      'bash': 'shell',
      'json': 'json'
    };
    return mapping[lang] || 'plaintext';
  };

  // React Quill modules configuration
  const quillModules = {
    toolbar: [
      [{ 'header': [1, 2, 3, false] }],
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      [{ 'script': 'sub'}, { 'script': 'super' }],
      [{ 'indent': '-1'}, { 'indent': '+1' }],
      ['blockquote', 'code-block'],
      ['link'],
      [{ 'color': [] }, { 'background': [] }],
      ['clean']
    ],
  };

  const quillFormats = [
    'header', 'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'script', 'indent', 'blockquote',
    'code-block', 'link', 'color', 'background'
  ];

  const handleSave = async () => {
    setError(null);
    
    if (!formData.name.trim()) {
      setError('Please enter a topic name');
      return;
    }

    setLoading(true);
    try {
      await onSave({
        name: formData.name,
        explanation_content: formData.explanation,
        code_language: formData.code.language,
        code_content: formData.code.content,
        source_title: formData.source.title,
        source_url: formData.source.url
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Save failed:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to save topic';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleAI = async (action) => {
    setError(null);
    setAiLoading(action);
    try {
      let input = '';
      if (action === 'generate_code') {
        input = formData.name;
      } else {
        input = formData.explanation || formData.name;
      }

      const result = await onAIAction(action, input, formData.code.language);
      
      if (action === 'generate_code') {
        setFormData(prev => ({
          ...prev,
          code: { ...prev.code, content: result }
        }));
      } else {
        setFormData(prev => ({
          ...prev,
          explanation: result
        }));
      }
    } catch (error) {
      console.error('AI action failed:', error);
      const errorMessage = error.response?.data?.error || error.message || 'AI action failed';
      setError(errorMessage);
    } finally {
      setAiLoading(null);
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-6 space-y-6 max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between sticky top-0 bg-white dark:bg-gray-800 pb-4 border-b dark:border-gray-700">
        <h3 className="text-xl font-bold flex items-center gap-2">
          <FileText size={24} className="text-blue-600" />
          {topic?.id ? 'Edit Topic' : 'New Topic'}
        </h3>
        <div className="flex items-center gap-2">
          {saved && (
            <span className="flex items-center gap-1 text-green-600 text-sm">
              <CheckCircle size={16} />
              Saved!
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={loading || !formData.name}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? <Loader size={16} className="animate-spin" /> : <Save size={16} />}
            Save Topic
          </button>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            <X size={20} />
          </button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Topic Name */}
      <div>
        <label className="block text-sm font-medium mb-2">Topic Name *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          placeholder="e.g., Binary Search Algorithm"
          className="w-full px-4 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Explanation Section with Rich Text Editor */}
      <div className="border dark:border-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-medium flex items-center gap-2">
            <FileText size={16} />
            Explanation
          </label>
          <div className="flex gap-2">
            <button
              onClick={() => handleAI('generate_explanation')}
              disabled={aiLoading}
              className="flex items-center gap-1 px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50"
            >
              {aiLoading === 'generate_explanation' ? (
                <Loader size={14} className="animate-spin" />
              ) : (
                <Sparkles size={14} />
              )}
              Generate
            </button>
            <button
              onClick={() => handleAI('improve_explanation')}
              disabled={aiLoading || !formData.explanation}
              className="flex items-center gap-1 px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 disabled:opacity-50"
            >
              {aiLoading === 'improve_explanation' ? (
                <Loader size={14} className="animate-spin" />
              ) : (
                <Wand2 size={14} />
              )}
              Improve
            </button>
            <button
              onClick={() => handleAI('summarize_explanation')}
              disabled={aiLoading || !formData.explanation}
              className="flex items-center gap-1 px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50"
            >
              {aiLoading === 'summarize_explanation' ? (
                <Loader size={14} className="animate-spin" />
              ) : (
                <FileText size={14} />
              )}
              Summarize
            </button>
          </div>
        </div>
        <div className="min-h-[250px]">
          <ReactQuill
            theme="snow"
            value={formData.explanation}
            onChange={(value) => setFormData(prev => ({ ...prev, explanation: value }))}
            modules={quillModules}
            formats={quillFormats}
            placeholder="Explain this topic in detail... Use the toolbar to format text (bold, headings, lists, etc.)"
            className="bg-white dark:bg-gray-900"
            style={{ minHeight: '200px' }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Use the toolbar above to format your text with headings, bold, italic, lists, and more.
        </p>
      </div>

      {/* Code Snippet Section with Monaco Editor */}
      <div className="border dark:border-gray-700 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <label className="text-sm font-medium flex items-center gap-2">
            <Code size={16} />
            Code Example (Optional)
          </label>
          <div className="flex items-center gap-2">
            <select
              value={formData.code.language}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                code: { ...prev.code, language: e.target.value }
              }))}
              className="px-3 py-1 text-sm border dark:border-gray-600 rounded bg-white dark:bg-gray-900"
            >
              {languages.map(lang => (
                <option key={lang.value} value={lang.value}>
                  {lang.label}
                </option>
              ))}
            </select>
            <button
              onClick={() => handleAI('generate_code')}
              disabled={aiLoading}
              className="flex items-center gap-1 px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded hover:bg-purple-200 disabled:opacity-50"
            >
              {aiLoading === 'generate_code' ? (
                <Loader size={14} className="animate-spin" />
              ) : (
                <Code size={14} />
              )}
              Generate Code
            </button>
          </div>
        </div>
        <div className="border dark:border-gray-600 rounded-lg overflow-hidden" style={{ height: '400px' }}>
          <Editor
            height="100%"
            language={getMonacoLanguage(formData.code.language)}
            value={formData.code.content}
            onChange={(value) => setFormData(prev => ({
              ...prev,
              code: { ...prev.code, content: value || '' }
            }))}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
              tabSize: 2,
              wordWrap: 'on',
              formatOnPaste: true,
              formatOnType: true,
            }}
          />
        </div>
      </div>

      {/* Source/Reference Section */}
      <div className="border dark:border-gray-700 rounded-lg p-4">
        <label className="text-sm font-medium flex items-center gap-2 mb-3">
          <Link size={16} />
          Source/Reference (Optional)
        </label>
        
        <div className="space-y-3">
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              Source Title
            </label>
            <input
              type="text"
              value={formData.source.title}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                source: { ...prev.source, title: e.target.value }
              }))}
              placeholder="e.g., MDN Web Docs"
              className="w-full px-3 py-2 text-sm border dark:border-gray-600 rounded bg-white dark:bg-gray-900"
            />
          </div>
          
          <div>
            <label className="block text-xs text-gray-600 dark:text-gray-400 mb-1">
              Source URL
            </label>
            <input
              type="url"
              value={formData.source.url}
              onChange={(e) => setFormData(prev => ({
                ...prev,
                source: { ...prev.source, url: e.target.value }
              }))}
              placeholder="https://..."
              className="w-full px-3 py-2 text-sm border dark:border-gray-600 rounded bg-white dark:bg-gray-900"
            />
          </div>
        </div>
      </div>

      {/* Help Text */}
      <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
        <p className="text-sm text-yellow-800 dark:text-yellow-200">
          <strong>💡 Tip:</strong> Each topic is saved independently. Use the rich text editor for formatted explanations and the code editor for syntax-highlighted code examples. Use AI tools to quickly generate content. Add sources for proper citation in PDF exports.
        </p>
      </div>
    </div>
  );
};

export default TopicEditor;