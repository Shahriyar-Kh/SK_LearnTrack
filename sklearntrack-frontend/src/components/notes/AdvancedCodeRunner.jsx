// FILE: AdvancedCodeRunner.jsx
import React, { useState, useEffect } from 'react';
import { Play, StopCircle, Zap, Cpu, HardDrive, Clock, AlertCircle } from 'lucide-react';
import Editor from '@monaco-editor/react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const AdvancedCodeRunner = () => {
  const [code, setCode] = useState('');
  const [language, setLanguage] = useState('python');
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [executing, setExecuting] = useState(false);
  const [executionTime, setExecutionTime] = useState(0);
  const [memoryUsed, setMemoryUsed] = useState(0);
  const [useDocker, setUseDocker] = useState(false);
  const [timeout, setTimeout] = useState(15);
  const [memoryLimit, setMemoryLimit] = useState(512);
  const [supportedLanguages, setSupportedLanguages] = useState({});
  
  const languages = [
    { value: 'python', label: 'Python', icon: '🐍' },
    { value: 'javascript', label: 'JavaScript', icon: '📜' },
    { value: 'java', label: 'Java', icon: '☕' },
    { value: 'cpp', label: 'C++', icon: '⚡' },
    { value: 'c', label: 'C', icon: '🔧' },
    { value: 'rust', label: 'Rust', icon: '🦀' },
    { value: 'go', label: 'Go', icon: '🚀' },
    { value: 'php', label: 'PHP', icon: '🐘' },
    { value: 'ruby', label: 'Ruby', icon: '💎' },
    { value: 'swift', label: 'Swift', icon: '🐦' },
    { value: 'r', label: 'R', icon: '📊' },
  ];
  
  useEffect(() => {
    // Load supported languages
    fetchLanguages();
  }, []);
  
  const fetchLanguages = async () => {
    try {
      const response = await api.post('/api/notes/run_code/', {
        language: 'list'
      });
      setSupportedLanguages(response.data);
    } catch (error) {
      console.error('Failed to fetch languages:', error);
    }
  };
  
  const runCode = async () => {
    setExecuting(true);
    setOutput('');
    
    try {
      const response = await api.post('/api/notes/run_code/', {
        code,
        language,
        input,
        timeout,
        memory_mb: memoryLimit,
        use_docker: useDocker
      });
      
      setOutput(response.data.formatted_output || response.data.output);
      setExecutionTime(response.data.execution_time || 0);
      setMemoryUsed(response.data.memory_used || 0);
      
      // Update UI based on success
      if (response.data.success) {
        // Show success animation
      }
      
    } catch (error) {
      setOutput(`Error: ${error.message}`);
    } finally {
      setExecuting(false);
    }
  };
  
  const stopExecution = () => {
    // Implement WebSocket or signal to stop execution
    setExecuting(false);
  };
  
  const loadExample = (lang) => {
    const examples = {
      python: `# Merge Sort in Python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Test
arr = [64, 34, 25, 12, 22, 11, 90]
print("Original:", arr)
print("Sorted:", merge_sort(arr))`,
      
      javascript: `// Quick Sort in JavaScript
function quickSort(arr) {
  if (arr.length <= 1) return arr;
  
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = arr.filter(x => x < pivot);
  const middle = arr.filter(x => x === pivot);
  const right = arr.filter(x => x > pivot);
  
  return [...quickSort(left), ...middle, ...quickSort(right)];
}

// Test
const numbers = [64, 34, 25, 12, 22, 11, 90];
console.log("Original:", numbers);
console.log("Sorted:", quickSort(numbers));`,
      
      java: `// Binary Search in Java
public class BinarySearch {
    public static int binarySearch(int[] arr, int target) {
        int left = 0, right = arr.length - 1;
        
        while (left <= right) {
            int mid = left + (right - left) / 2;
            
            if (arr[mid] == target) return mid;
            if (arr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        
        return -1;
    }
    
    public static void main(String[] args) {
        int[] arr = {2, 3, 4, 10, 40};
        int target = 10;
        int result = binarySearch(arr, target);
        
        if (result == -1)
            System.out.println("Element not present");
        else
            System.out.println("Element found at index " + result);
    }
}`
    };
    
    setCode(examples[lang] || '// Enter your code here');
    setLanguage(lang);
  };
  
  return (
    <div className="flex flex-col h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Zap size={24} className="text-yellow-500" />
            Advanced Code Runner
          </h1>
          
          <div className="flex items-center gap-2">
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="px-3 py-1 bg-gray-700 rounded border border-gray-600"
            >
              {languages.map(lang => (
                <option key={lang.value} value={lang.value}>
                  {lang.icon} {lang.label}
                </option>
              ))}
            </select>
            
            <button
              onClick={() => loadExample(language)}
              className="px-3 py-1 bg-blue-600 rounded hover:bg-blue-700"
            >
              Load Example
            </button>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Clock size={16} />
            <input
              type="number"
              value={timeout}
              onChange={(e) => setTimeout(parseInt(e.target.value))}
              className="w-20 px-2 py-1 bg-gray-700 rounded border border-gray-600"
              min="1"
              max="60"
            />
            <span className="text-sm">s</span>
          </div>
          
          <div className="flex items-center gap-2">
            <HardDrive size={16} />
            <input
              type="number"
              value={memoryLimit}
              onChange={(e) => setMemoryLimit(parseInt(e.target.value))}
              className="w-20 px-2 py-1 bg-gray-700 rounded border border-gray-600"
              min="64"
              max="2048"
            />
            <span className="text-sm">MB</span>
          </div>
          
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={useDocker}
              onChange={(e) => setUseDocker(e.target.checked)}
              className="rounded"
            />
            <span className="text-sm flex items-center gap-1">
              <Cpu size={14} />
              Use Docker
            </span>
          </label>
          
          <button
            onClick={executing ? stopExecution : runCode}
            disabled={!code.trim()}
            className={`px-4 py-2 rounded flex items-center gap-2 ${
              executing
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-green-600 hover:bg-green-700'
            } disabled:opacity-50`}
          >
            {executing ? (
              <>
                <StopCircle size={16} />
                Stop
              </>
            ) : (
              <>
                <Play size={16} />
                Run
              </>
            )}
          </button>
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Code Editor */}
        <div className="flex-1 flex flex-col border-r border-gray-700">
          <div className="p-4 bg-gray-800 border-b border-gray-700">
            <h2 className="font-semibold">Editor</h2>
          </div>
          <div className="flex-1">
            <Editor
              height="100%"
              language={language}
              value={code}
              onChange={setCode}
              theme="vs-dark"
              options={{
                minimap: { enabled: true },
                fontSize: 14,
                lineNumbers: 'on',
                wordWrap: 'on',
                automaticLayout: true,
                scrollBeyondLastLine: false,
                formatOnPaste: true,
                formatOnType: true,
                suggestOnTriggerCharacters: true,
                acceptSuggestionOnEnter: 'on',
                tabCompletion: 'on',
                wordBasedSuggestions: true,
                parameterHints: { enabled: true },
              }}
            />
          </div>
        </div>
        
        {/* Input/Output Panels */}
        <div className="w-1/3 flex flex-col">
          {/* Input Panel */}
          <div className="flex-1 flex flex-col border-b border-gray-700">
            <div className="p-4 bg-gray-800">
              <h2 className="font-semibold flex items-center gap-2">
                <AlertCircle size={16} />
                Input (stdin)
              </h2>
            </div>
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Enter input for your program..."
                className="w-full h-full p-4 bg-gray-900 font-mono resize-none outline-none"
                spellCheck={false}
              />
            </div>
          </div>
          
          {/* Output Panel */}
          <div className="flex-1 flex flex-col">
            <div className="p-4 bg-gray-800 flex items-center justify-between">
              <h2 className="font-semibold">Output</h2>
              <div className="flex items-center gap-4 text-sm">
                {executionTime > 0 && (
                  <span className="text-green-400">
                    Time: {executionTime.toFixed(2)}s
                  </span>
                )}
                {memoryUsed > 0 && (
                  <span className="text-blue-400">
                    Memory: {memoryUsed.toFixed(1)}MB
                  </span>
                )}
              </div>
            </div>
            <div className="flex-1 p-4 overflow-auto bg-black">
              {output ? (
                <SyntaxHighlighter
                  language="text"
                  style={vscDarkPlus}
                  showLineNumbers={false}
                  customStyle={{
                    margin: 0,
                    padding: 0,
                    background: 'transparent',
                    fontSize: '13px',
                  }}
                >
                  {output}
                </SyntaxHighlighter>
              ) : (
                <div className="text-gray-500 italic">
                  {executing ? 'Running...' : 'Output will appear here'}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      
      {/* Status Bar */}
      <div className="px-4 py-2 bg-gray-800 border-t border-gray-700 text-sm flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="text-green-400">
            {language.toUpperCase()}
          </span>
          <span className="text-gray-400">
            Lines: {code.split('\n').length}
          </span>
          <span className="text-gray-400">
            Characters: {code.length}
          </span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-gray-400">
            {useDocker ? 'Docker Container' : 'Sandbox Mode'}
          </span>
          <span className="text-yellow-400">
            Timeout: {timeout}s | Memory: {memoryLimit}MB
          </span>
        </div>
      </div>
    </div>
  );
};

export default AdvancedCodeRunner;