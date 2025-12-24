// FILE: src/components/notes/AIActionsPanel.jsx
// ============================================================================

import { useState } from 'react';
import { Wand2, Loader } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';

const AIActionsPanel = ({ noteContent, onAction, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [selectedAction, setSelectedAction] = useState(null);

  const aiActions = [
    { id: 'summarize_short', label: 'Short Summary', desc: '2-3 sentences' },
    { id: 'summarize_medium', label: 'Medium Summary', desc: '1 paragraph' },
    { id: 'summarize_detailed', label: 'Detailed Summary', desc: 'With key points' },
    { id: 'expand', label: 'Expand Content', desc: 'Add more details' },
    { id: 'rewrite', label: 'Rewrite for Clarity', desc: 'Improve readability' },
    { id: 'breakdown', label: 'Topic Breakdown', desc: 'Structure into topics' },
  ];

  const handleAction = async (actionId) => {
    setLoading(true);
    setSelectedAction(actionId);
    try {
      await onAction(actionId, noteContent);
    } finally {
      setLoading(false);
      setSelectedAction(null);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-2xl w-full max-h-[80vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold flex items-center gap-2">
            <Wand2 size={24} className="text-primary-600" />
            AI Actions
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            ✕
          </button>
        </div>

        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Select an AI action to enhance your note content
        </p>

        <div className="grid md:grid-cols-2 gap-4">
          {aiActions.map((action) => (
            <button
              key={action.id}
              onClick={() => handleAction(action.id)}
              disabled={loading}
              className="p-4 border-2 dark:border-gray-700 rounded-lg hover:border-primary-600 dark:hover:border-primary-600 transition-all text-left disabled:opacity-50"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="font-semibold mb-1">{action.label}</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{action.desc}</p>
                </div>
                {loading && selectedAction === action.id && (
                  <Loader size={20} className="animate-spin text-primary-600" />
                )}
              </div>
            </button>
          ))}
        </div>

        <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
          <p className="text-sm">
            <strong>Note:</strong> AI actions will replace your current note content. Make sure to
            save your work before applying AI actions.
          </p>
        </div>
      </Card>
    </div>
  );
};

export default AIActionsPanel;