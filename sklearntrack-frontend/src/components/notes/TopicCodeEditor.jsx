// FILE: components/notes/TopicCodeEditor.jsx
import { useState } from 'react';
import Editor from '@monaco-editor/react';
import { Play, Square, Loader } from 'lucide-react';

const TopicCodeEditor = ({ code, language, onChange }) => {
  const [running, setRunning] = useState(false);
  const [output, setOutput] = useState('');

  const runCode = async () => {
    setRunning(true);
    setOutput('Running code...');
    
    try {
      // Implement code execution via API
      const response = await api.post('/api/notes/run_code/', {
        code,
        language
      });
      setOutput(response.data.output);
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="border rounded-lg overflow-hidden">
      <div className="flex items-center justify-between bg-gray-800 px-4 py-2">
        <span className="text-white text-sm">{language.toUpperCase()}</span>
        <button
          onClick={runCode}
          disabled={running}
          className="flex items-center gap-2 px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50"
        >
          {running ? <Loader size={16} className="animate-spin" /> : <Play size={16} />}
          Run
        </button>
      </div>
      
      <Editor
        height="400px"
        language={language}
        value={code}
        onChange={onChange}
        theme="vs-dark"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          automaticLayout: true,
        }}
      />
      
      {output && (
        <div className="bg-gray-900 text-white p-4 font-mono text-sm max-h-48 overflow-y-auto">
          <pre>{output}</pre>
        </div>
      )}
    </div>
  );
};

export default TopicCodeEditor;