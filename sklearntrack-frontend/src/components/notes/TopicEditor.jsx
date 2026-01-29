import { useState, useEffect } from 'react';
import { 
  Save, X, Wand2, Code, Link, Plus, Trash2, 
  FileText, Loader, CheckCircle, Sparkles, Play, Terminal
} from 'lucide-react';
import ReactQuill from 'react-quill';
import 'react-quill/dist/quill.snow.css';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
import { noteService } from '@/services/note.service';

// InputModal Component - Add this at the top after imports
const InputModal = ({ open, value, onChange, onClose, onRun }) => {
  if (!open) return null;
  
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Provide Input</h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          This code requires input. Enter the values below (one per line):
        </p>
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Enter input values here..."
          className="w-full px-3 py-2 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 font-mono text-sm"
          rows={5}
          autoFocus
        />
        <div className="flex justify-end gap-2 mt-4">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
          >
            Cancel
          </button>
          <button
            onClick={onRun}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Run with Input
          </button>
        </div>
      </div>
    </div>
  );
};

const TopicEditor = ({ topic, onSave, onCancel, onAIAction }) => {
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);
  const [aiLoading, setAiLoading] = useState(null);
  const [error, setError] = useState(null);
  const [runningCode, setRunningCode] = useState(false);
  const [codeOutput, setCodeOutput] = useState('');
  const [codeError, setCodeError] = useState(null);
  const [showInputModal, setShowInputModal] = useState(false);
  const [stdinValue, setStdinValue] = useState('');
  const [autoDetectsInput, setAutoDetectsInput] = useState(false);
  const [learningLevel, setLearningLevel] = useState('beginner');

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
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'c', label: 'C' },
    { value: 'go', label: 'Go' },
    { value: 'other', label: 'Other' }
  ];

  // Monaco Editor language mapping
  const getMonacoLanguage = (lang) => {
    const mapping = {
      'cpp': 'cpp',
      'c': 'c',
      'python': 'python',
      'javascript': 'javascript',
      'java': 'java',
      'go': 'go',
      'other': 'plaintext'
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

  // Update the executeRun function
  const executeRun = async ({ stdin = '' } = {}) => {
    setRunningCode(true);
    setCodeOutput('');
    setCodeError(null);
    
    try {
      const payload = {
        code: formData.code.content,
        language: formData.code.language,
        stdin,
        timeout: 15
      };
      
      const result = await noteService.runCode(payload);
      
      if (result.success) {
        let outputText = result.output || '✅ No output';
        
        // Add execution info
        if (result.runtime_ms) {
          outputText += `\n\n⏱️ Runtime: ${result.runtime_ms}ms`;
        }
        if (result.exit_code !== undefined && result.exit_code !== null) {
          outputText += `\n📊 Exit Code: ${result.exit_code}`;
        }
        
        setCodeOutput(outputText);
      } else {
        // Check if it requires input
        if (result.requires_input) {
          setCodeError({ 
            message: 'This code requires input', 
            requires_input: true,
            hint: 'Please provide input using the stdin field.'
          });
        } else {
          setCodeError({ 
            message: result.error || 'Execution failed',
            formatted: result.formatted_error
          });
        }
      }
    } catch (e) {
      setCodeError({ 
        message: e.message || 'Run failed',
        details: 'Please check your connection and try again.'
      });
    } finally {
      setRunningCode(false);
    }
  };

  // Add this function inside TopicEditor component
  const needsInput = (code, lang) => {
    if (!code) return false;
    
    const patterns = {
      python: /\binput\s*\(/i,
      javascript: /\bprompt\s*\(/i,
      cpp: /\bcin\s*>>|\bstd::cin\b|\bgetline\s*\(/i,
      c: /\bscanf\s*\(|\bgets\s*\(|\bfgets\s*\(/i,
      java: /\bScanner\b|\bSystem\.in\b|\bBufferedReader\b/i,
      go: /\bfmt\.Scan|\bbufio\.NewReader/i,
    };
    
    const pattern = patterns[lang];
    return pattern ? pattern.test(code) : false;
  };

  // Update the handleRunCode function
  const handleRunCode = async () => {
    if (!formData.code.content.trim()) {
      setCodeError({ message: 'No code to run' });
      return;
    }

    const detected = needsInput(formData.code.content, formData.code.language);
    
    if (detected && !stdinValue.trim()) {
      // Show input modal
      setShowInputModal(true);
      return;
    }

    await executeRun({ stdin: stdinValue });
  };

// In TopicEditor.jsx - Update the handleAI function
const handleAI = async (action) => {
  setError(null);
  setAiLoading(action);
  
  try {
    let input = '';
    let requestData = {
      action_type: action,
      level: learningLevel,  // This should already be there
      subject_area: 'programming'  // Add this
    };
    
    // Determine input based on action type
    if (action === 'generate_code') {
      input = formData.name.trim();
      if (!input) {
        throw new Error('Please enter a topic name first');
      }
      requestData.topic_name = input;
      requestData.language = formData.code.language;
    } else if (action === 'generate_explanation') {
      input = formData.name.trim();
      if (!input) {
        throw new Error('Please enter a topic name first');
      }
      requestData.topic_name = input;
      
      // Auto-detect subject area from topic name
      const programmingKeywords = [
        'function', 'class', 'loop', 'array', 'variable', 'algorithm', 
        'code', 'programming', 'python', 'javascript', 'java', 'c++',
        'syntax', 'method', 'object', 'string', 'integer', 'boolean',
        'recursion', 'sorting', 'database', 'api', 'framework'
      ];
      const isProgramming = programmingKeywords.some(kw => 
        input.toLowerCase().includes(kw)
      );
      requestData.subject_area = isProgramming ? 'programming' : 'general';
      
    } else if (action === 'improve_explanation' || action === 'summarize_explanation') {
      input = formData.explanation.trim();
      if (!input || input.length < 20) {
        throw new Error('Please add some content to improve/summarize');
      }
      requestData.input_content = input;
    }
    
    // Use standalone AI action endpoint (no topic ID required)
    const result = await noteService.performStandaloneAIAction(requestData);
    
    // Update form with generated content
    if (action === 'generate_code') {
      setFormData(prev => ({
        ...prev,
        code: { 
          ...prev.code, 
          content: result.generated_content 
        }
      }));
      showToast(`Code generated successfully (${learningLevel} level)!`, 'success');
    } else {
      // For explanations (generate, improve, summarize)
      setFormData(prev => ({
        ...prev,
        explanation: result.generated_content
      }));
      
      const messages = {
        'generate_explanation': `Explanation generated successfully (${learningLevel} level)!`,
        'improve_explanation': 'Explanation improved successfully!',
        'summarize_explanation': 'Summary generated successfully!'
      };
      showToast(messages[action] || 'Content generated!', 'success');
    }
    
  } catch (error) {
    console.error('AI action failed:', error);
    const errorMessage = error.response?.data?.error || error.message || 'AI action failed';
    setError(errorMessage);
    showToast(errorMessage, 'error');
  } finally {
    setAiLoading(null);
  }
};
// Add this helper function for toast notifications
const showToast = (message, type = 'success') => {
  // You can use your existing toast system or add this simple one:
  const toastEvent = new CustomEvent('show-toast', {
    detail: { message, type }
  });
  window.dispatchEvent(toastEvent);
};

  const clearCodeOutput = () => {
    setCodeOutput('');
    setCodeError(null);
  };

  const renderCodeOutput = () => {
    if (!codeOutput && !codeError) return null;
    
    if (codeError) {
      return (
        <div className="mt-4 border border-red-300 dark:border-red-700 rounded-lg overflow-hidden">
          <div className="flex items-center justify-between bg-red-800 px-4 py-2">
            <div className="flex items-center gap-2">
              <Terminal size={16} className="text-red-200" />
              <span className="text-white text-sm font-medium">Execution Error</span>
            </div>
            <button
              onClick={() => setCodeError(null)}
              className="text-red-200 hover:text-white"
            >
              <X size={14} />
            </button>
          </div>
          <div className="bg-red-50 dark:bg-red-900/30 p-4">
            <div className="font-mono text-sm whitespace-pre-wrap overflow-x-auto">
              {typeof codeError === 'object' ? (
                <div className="space-y-2">
                  <div className="text-red-700 dark:text-red-300 font-semibold">
                    {codeError.message}
                  </div>
                  {codeError.formatted && (
                    <div className="border-l-4 border-red-500 pl-3">
                      <pre className="text-red-800 dark:text-red-200 text-xs leading-relaxed">
                        {codeError.formatted}
                      </pre>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-red-700 dark:text-red-300">
                  <pre className="whitespace-pre-wrap">{codeError}</pre>
                </div>
              )}
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="mt-4 border dark:border-gray-600 rounded-lg overflow-hidden">
        <div className="flex items-center justify-between bg-gray-800 px-4 py-2">
          <div className="flex items-center gap-2">
            <Terminal size={16} className="text-green-400" />
            <span className="text-white text-sm font-medium">Output</span>
          </div>
          <button
            onClick={clearCodeOutput}
            className="text-gray-400 hover:text-white"
          >
            <X size={14} />
          </button>
        </div>
        <div className="bg-gray-900 text-white p-4 font-mono text-sm">
          <div className="text-green-400">
            <div className="flex items-center gap-2 mb-1">
              <Terminal size={12} />
              <span className="font-medium">Output:</span>
            </div>
            <pre className="whitespace-pre-wrap">{codeOutput}</pre>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border dark:border-gray-700 p-6 space-y-6 max-h-[90vh] overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between pt-4 sticky top-0 z-10 bg-white dark:bg-gray-800 pb-4 border-b dark:border-gray-700">
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
      {/* Learning Level Selector - NEW */}
<div className="border dark:border-gray-700 rounded-lg p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
  <label className="flex text-sm font-medium mb-3 items-center gap-2">
    <span className="text-blue-700 dark:text-blue-300 text-base font-semibold">
      🎓 Learning Level
    </span>
    <span className="text-xs text-gray-600 dark:text-gray-400">
      (Choose your level for AI content generation)
    </span>
  </label>
  
  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
    {[
      { 
        value: 'beginner', 
        icon: '🌱', 
        label: 'Beginner', 
        desc: 'Simple & Easy', 
        color: 'green',
        detail: 'Perfect for those just starting out'
      },
      { 
        value: 'intermediate', 
        icon: '📚', 
        label: 'Intermediate', 
        desc: 'More Details', 
        color: 'blue',
        detail: 'Good depth for those who know basics'
      },
      { 
        value: 'advanced', 
        icon: '🚀', 
        label: 'Advanced', 
        desc: 'Deep Dive', 
        color: 'purple',
        detail: 'Technical details and optimization'
      },
      { 
        value: 'expert', 
        icon: '⭐', 
        label: 'Expert', 
        desc: 'Production', 
        color: 'red',
        detail: 'Architecture and mastery level'
      }
    ].map(level => (
      <button
        key={level.value}
        type="button"
        onClick={() => setLearningLevel(level.value)}
        className={`p-3 rounded-lg border-2 transition-all transform hover:scale-105 ${
          learningLevel === level.value
            ? `border-${level.color}-600 bg-${level.color}-100 dark:bg-${level.color}-900/40 shadow-md`
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 bg-white dark:bg-gray-800'
        }`}
      >
        <div className="text-2xl mb-1">{level.icon}</div>
        <div className="font-semibold text-sm">{level.label}</div>
        <div className="text-xs text-gray-600 dark:text-gray-400 mt-1">{level.desc}</div>
      </button>
    ))}
  </div>
  
  {/* Level Description - Shows info about selected level */}
  <div className="mt-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
    {learningLevel === 'beginner' && (
      <div className="flex items-start gap-2">
        <span className="text-2xl">🌱</span>
        <div>
          <p className="font-semibold text-green-700 dark:text-green-300">Beginner Level</p>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
            Simple explanations with basic examples. Easy to understand for those just starting out.
            Content is short, clear, and fun to learn!
          </p>
        </div>
      </div>
    )}
    {learningLevel === 'intermediate' && (
      <div className="flex items-start gap-2">
        <span className="text-2xl">📚</span>
        <div>
          <p className="font-semibold text-blue-700 dark:text-blue-300">Intermediate Level</p>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
            More detailed explanations with practical examples. Good for those who know programming basics
            and want deeper understanding.
          </p>
        </div>
      </div>
    )}
    {learningLevel === 'advanced' && (
      <div className="flex items-start gap-2">
        <span className="text-2xl">🚀</span>
        <div>
          <p className="font-semibold text-purple-700 dark:text-purple-300">Advanced Level</p>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
            Deep technical details, performance optimization, and edge cases. For experienced
            developers who want comprehensive knowledge.
          </p>
        </div>
      </div>
    )}
    {learningLevel === 'expert' && (
      <div className="flex items-start gap-2">
        <span className="text-2xl">⭐</span>
        <div>
          <p className="font-semibold text-red-700 dark:text-red-300">Expert Level</p>
          <p className="text-sm text-gray-700 dark:text-gray-300 mt-1">
            Production-grade knowledge with architecture, scalability, and industry best practices.
            For senior/principal engineers.
          </p>
        </div>
      </div>
    )}
  </div>
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
            disabled={aiLoading || !formData.name.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {aiLoading === 'generate_explanation' ? (
              <Loader className="w-4 h-4 animate-spin" />
            ) : (
              <Sparkles className="w-4 h-4" />
            )}
            <span>Generate ({learningLevel})</span>
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

      {/* Code Snippet Section with Monaco Editor and Run Button */}
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
            <button
              onClick={handleRunCode}
              disabled={runningCode || !formData.code.content}
              className="flex items-center gap-1 px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 disabled:opacity-50"
            >
              {runningCode ? (
                <Loader size={14} className="animate-spin" />
              ) : (
                <Play size={14} />
              )}
              Run Code
            </button>
          </div>
        </div>
        <div className="border dark:border-gray-600 rounded-lg overflow-hidden" style={{ height: '300px' }}>
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

        {/* Render Code Output or Error */}
        {renderCodeOutput()}

        {/* Running Code Loading State */}
        {runningCode && !codeOutput && !codeError && (
          <div className="mt-4 p-4 bg-gray-900 rounded-lg">
            <div className="flex items-center gap-3 text-green-400">
              <Loader size={16} className="animate-spin" />
              <span className="text-sm font-medium">Executing code...</span>
            </div>
          </div>
        )}
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
        <div className="prose prose-sm dark:prose-invert">
          <p className="text-sm text-yellow-800 dark:text-yellow-200">
            <strong>💡 Tip:</strong> Each topic is saved independently. Use the rich text editor for formatted explanations and the code editor for syntax-highlighted code examples. Use AI tools to quickly generate content. Add sources for proper citation in PDF exports.
          </p>
          <p className="text-sm text-yellow-800 dark:text-yellow-200 mt-2">
            <strong>🚀 Run Code:</strong> Click the "Run Code" button to execute your code snippets in a safe sandbox environment. View real-time output and debug your code directly in the editor.
          </p>
        </div>
      </div>

      {/* Input Modal */}
      <InputModal
        open={showInputModal}
        value={stdinValue}
        onChange={setStdinValue}
        onClose={() => setShowInputModal(false)}
        onRun={() => {
          setShowInputModal(false);
          executeRun({ stdin: stdinValue });
        }}
      />
    </div>
  );
};

export default TopicEditor;