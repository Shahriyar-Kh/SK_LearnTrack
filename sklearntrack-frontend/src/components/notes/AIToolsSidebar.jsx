import { useState } from 'react';
import { Sparkles, Wand2, FileText, Code, X, Loader, History, Save, Download, Upload } from 'lucide-react';
import ReactQuill from 'react-quill';
import Editor from '@monaco-editor/react';
import 'react-quill/dist/quill.snow.css';

const AIToolsSidebar = ({ isOpen, onClose, noteService }) => {
  const [activeTab, setActiveTab] = useState('explain');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  
  // Form states
  const [explainInput, setExplainInput] = useState('');
  const [improveInput, setImproveInput] = useState('');
  const [summarizeInput, setSummarizeInput] = useState('');
  const [codeInput, setCodeInput] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('python');

  const tools = [
    { id: 'explain', label: 'Explain Topic', icon: Sparkles },
    { id: 'improve', label: 'Improve', icon: Wand2 },
    { id: 'summarize', label: 'Summarize', icon: FileText },
    { id: 'code', label: 'Generate Code', icon: Code }
  ];

  const handleExplain = async () => {
    if (!explainInput.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await noteService.aiToolExplain({
        title: explainInput,
        save_to_history: true
      });
      
      setResult({
        type: 'explain',
        content: response.generated_content,
        title: response.title,
        historyId: response.history_id
      });
    } catch (error) {
      console.error('AI Explain error:', error);
      setResult({
        type: 'error',
        content: error.message || 'Failed to generate explanation'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleImprove = async () => {
    if (!improveInput.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await noteService.aiToolImprove({
        title: 'Improved Content',
        input_content: improveInput,
        save_to_history: true
      });
      
      setResult({
        type: 'improve',
        content: response.generated_content,
        title: response.title,
        historyId: response.history_id
      });
    } catch (error) {
      console.error('AI Improve error:', error);
      setResult({
        type: 'error',
        content: error.message || 'Failed to improve content'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!summarizeInput.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await noteService.aiToolSummarize({
        title: 'Summary',
        input_content: summarizeInput,
        save_to_history: true
      });
      
      setResult({
        type: 'summarize',
        content: response.generated_content,
        title: response.title,
        historyId: response.history_id
      });
    } catch (error) {
      console.error('AI Summarize error:', error);
      setResult({
        type: 'error',
        content: error.message || 'Failed to summarize content'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateCode = async () => {
    if (!codeInput.trim()) return;
    
    setLoading(true);
    setResult(null);
    
    try {
      const response = await noteService.aiToolGenerateCode({
        title: codeInput,
        language: codeLanguage,
        save_to_history: true
      });
      
      setResult({
        type: 'code',
        content: response.generated_content,
        title: response.title,
        language: response.language,
        historyId: response.history_id
      });
    } catch (error) {
      console.error('AI Generate Code error:', error);
      setResult({
        type: 'error',
        content: error.message || 'Failed to generate code'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const data = await noteService.getAIHistory();
      setHistory(data);
      setShowHistory(true);
    } catch (error) {
      console.error('Load history error:', error);
    }
  };

  const saveAsNote = async (historyId) => {
    try {
      await noteService.saveAIHistoryAsNote(historyId);
      alert('Saved as note successfully!');
    } catch (error) {
      console.error('Save as note error:', error);
      alert('Failed to save as note');
    }
  };

  const exportPDF = async (historyId) => {
    try {
      await noteService.exportAIHistoryPDF(historyId);
    } catch (error) {
      console.error('Export PDF error:', error);
      alert('Failed to export PDF');
    }
  };

  const exportToDrive = async (historyId) => {
    try {
      const response = await noteService.exportAIHistoryToDrive(historyId);
      alert('Exported to Google Drive successfully!');
    } catch (error) {
      console.error('Export to Drive error:', error);
      alert('Failed to export to Google Drive');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex justify-end">
      <div className="bg-white dark:bg-gray-800 w-full max-w-2xl h-full overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4 flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <Sparkles size={24} />
            <h2 className="text-xl font-bold">AI Tools</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={loadHistory}
              className="p-2 hover:bg-white/20 rounded-lg transition"
              title="View History"
            >
              <History size={20} />
            </button>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white/20 rounded-lg transition"
            >
              <X size={20} />
            </button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex border-b dark:border-gray-700 bg-white dark:bg-gray-800">
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <button
                key={tool.id}
                onClick={() => {
                  setActiveTab(tool.id);
                  setResult(null);
                }}
                className={`flex-1 flex items-center justify-center gap-2 px-4 py-3 border-b-2 transition ${
                  activeTab === tool.id
                    ? 'border-blue-600 text-blue-600 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-transparent hover:bg-gray-50 dark:hover:bg-gray-700'
                }`}
              >
                <Icon size={18} />
                <span className="text-sm font-medium">{tool.label}</span>
              </button>
            );
          })}
        </div>

        {/* Content Area */}
        <div className="p-6 space-y-6">
          {/* Explain Topic */}
          {activeTab === 'explain' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Enter Topic or Question
                </label>
                <input
                  type="text"
                  value={explainInput}
                  onChange={(e) => setExplainInput(e.target.value)}
                  placeholder="e.g., Binary Search Algorithm"
                  className="w-full px-4 py-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
                  onKeyPress={(e) => e.key === 'Enter' && handleExplain()}
                />
              </div>
              
              <button
                onClick={handleExplain}
                disabled={loading || !explainInput.trim()}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles size={20} />
                    Generate Explanation
                  </>
                )}
              </button>
            </div>
          )}

          {/* Improve */}
          {activeTab === 'improve' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Paste Content to Improve
                </label>
                <ReactQuill
                  theme="snow"
                  value={improveInput}
                  onChange={setImproveInput}
                  placeholder="Paste or type your content here..."
                  className="bg-white dark:bg-gray-900 min-h-[200px]"
                />
              </div>
              
              <button
                onClick={handleImprove}
                disabled={loading || !improveInput.trim()}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Improving...
                  </>
                ) : (
                  <>
                    <Wand2 size={20} />
                    Improve Content
                  </>
                )}
              </button>
            </div>
          )}

          {/* Summarize */}
          {activeTab === 'summarize' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Paste Content to Summarize
                </label>
                <ReactQuill
                  theme="snow"
                  value={summarizeInput}
                  onChange={setSummarizeInput}
                  placeholder="Paste or type your content here..."
                  className="bg-white dark:bg-gray-900 min-h-[200px]"
                />
              </div>
              
              <button
                onClick={handleSummarize}
                disabled={loading || !summarizeInput.trim()}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Summarizing...
                  </>
                ) : (
                  <>
                    <FileText size={20} />
                    Summarize Content
                  </>
                )}
              </button>
            </div>
          )}

          {/* Generate Code */}
          {activeTab === 'code' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Describe What Code to Generate
                </label>
                <input
                  type="text"
                  value={codeInput}
                  onChange={(e) => setCodeInput(e.target.value)}
                  placeholder="e.g., Binary search implementation"
                  className="w-full px-4 py-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
                  onKeyPress={(e) => e.key === 'Enter' && handleGenerateCode()}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">
                  Programming Language
                </label>
                <select
                  value={codeLanguage}
                  onChange={(e) => setCodeLanguage(e.target.value)}
                  className="w-full px-4 py-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900"
                >
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                  <option value="java">Java</option>
                  <option value="cpp">C++</option>
                  <option value="c">C</option>
                  <option value="go">Go</option>
                </select>
              </div>
              
              <button
                onClick={handleGenerateCode}
                disabled={loading || !codeInput.trim()}
                className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                {loading ? (
                  <>
                    <Loader size={20} className="animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Code size={20} />
                    Generate Code
                  </>
                )}
              </button>
            </div>
          )}

          {/* Result Display */}
          {result && result.type !== 'error' && (
            <div className="mt-6 border dark:border-gray-700 rounded-lg overflow-hidden">
              <div className="bg-gray-100 dark:bg-gray-700 px-4 py-3 flex items-center justify-between">
                <h3 className="font-semibold">Result</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => saveAsNote(result.historyId)}
                    className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition"
                    title="Save as Note"
                  >
                    <Save size={16} />
                  </button>
                  <button
                    onClick={() => exportPDF(result.historyId)}
                    className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition"
                    title="Export PDF"
                  >
                    <Download size={16} />
                  </button>
                  <button
                    onClick={() => exportToDrive(result.historyId)}
                    className="p-2 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition"
                    title="Export to Drive"
                  >
                    <Upload size={16} />
                  </button>
                </div>
              </div>
              
              <div className="p-4 bg-white dark:bg-gray-800">
                {result.type === 'code' ? (
                  <Editor
                    height="400px"
                    language={result.language}
                    value={result.content}
                    theme="vs-dark"
                    options={{ readOnly: false, minimap: { enabled: false } }}
                  />
                ) : (
                  <ReactQuill
                    theme="snow"
                    value={result.content}
                    readOnly={false}
                    className="min-h-[300px]"
                  />
                )}
              </div>
            </div>
          )}

          {/* Error Display */}
          {result && result.type === 'error' && (
            <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-800 dark:text-red-200">{result.content}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIToolsSidebar;