// FILE: src/components/notes/YouTubeImporter.jsx
// ============================================================================

import { useState } from 'react';
import { Youtube, Loader, X, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import toast from 'react-hot-toast';

const YouTubeImporter = ({ onImport, onClose }) => {
  const [videoUrl, setVideoUrl] = useState('');
  const [noteTitle, setNoteTitle] = useState('');
  const [generateNotes, setGenerateNotes] = useState(true);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState('input'); // 'input', 'processing', 'success'
  const [result, setResult] = useState(null);

  const validateYouTubeUrl = (url) => {
    const patterns = [
      /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
      /^(https?:\/\/)?(www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/
    ];
    
    return patterns.some(pattern => pattern.test(url));
  };

  const extractVideoId = (url) => {
    const patterns = [
      /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
      /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/
    ];
    
    for (const pattern of patterns) {
      const match = url.match(pattern);
      if (match) return match[1];
    }
    return null;
  };

  const handleImport = async () => {
    // Validation
    if (!videoUrl.trim()) {
      toast.error('Please enter a YouTube URL');
      return;
    }

    if (!validateYouTubeUrl(videoUrl)) {
      toast.error('Please enter a valid YouTube URL');
      return;
    }

    try {
      setLoading(true);
      setStep('processing');

      const importData = {
        video_url: videoUrl,
        generate_notes: generateNotes,
        ...(noteTitle && { note_title: noteTitle })
      };

      const response = await onImport(importData);
      
      setResult(response);
      setStep('success');
      
    } catch (error) {
      console.error('Import error:', error);
      toast.error(error.message || 'Failed to import YouTube video');
      setStep('input');
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setVideoUrl('');
    setNoteTitle('');
    setGenerateNotes(true);
    setStep('input');
    setResult(null);
  };

  const handleComplete = () => {
    onClose();
    handleReset();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <Card className="max-w-3xl w-full">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-2xl font-bold flex items-center gap-2">
            <Youtube size={28} className="text-red-600" />
            Import YouTube Video
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        {/* Input Step */}
        {step === 'input' && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">
                YouTube Video URL *
              </label>
              <input
                type="url"
                value={videoUrl}
                onChange={(e) => setVideoUrl(e.target.value)}
                placeholder="https://www.youtube.com/watch?v=..."
                className="input-field w-full"
                autoFocus
              />
              <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                Paste the full YouTube video URL
              </p>
            </div>

            {/* Video Preview */}
            {videoUrl && validateYouTubeUrl(videoUrl) && (
              <div className="border dark:border-gray-700 rounded-lg p-4 bg-gray-50 dark:bg-gray-800">
                <div className="aspect-video bg-black rounded overflow-hidden">
                  <iframe
                    width="100%"
                    height="100%"
                    src={`https://www.youtube.com/embed/${extractVideoId(videoUrl)}`}
                    title="YouTube video preview"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                </div>
              </div>
            )}

            <div className="flex items-center gap-3 p-4 border dark:border-gray-700 rounded-lg">
              <input
                type="checkbox"
                id="generate-notes"
                checked={generateNotes}
                onChange={(e) => setGenerateNotes(e.target.checked)}
                className="w-4 h-4 text-primary-600 rounded"
              />
              <label htmlFor="generate-notes" className="flex-1 cursor-pointer">
                <div className="font-medium">Auto-generate notes with AI</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Automatically create structured notes from the video transcript
                </div>
              </label>
            </div>

            {generateNotes && (
              <div>
                <label className="block text-sm font-medium mb-2">
                  Note Title (Optional)
                </label>
                <input
                  type="text"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  placeholder="Leave blank to use video title"
                  className="input-field w-full"
                />
              </div>
            )}

            <div className="p-4 bg-blue-50 dark:bg-blue-900 rounded-lg">
              <h4 className="font-semibold mb-2 text-sm">What happens next?</h4>
              <ul className="text-sm text-gray-700 dark:text-gray-300 space-y-1">
                <li>1. We'll fetch the video transcript from YouTube</li>
                <li>2. The transcript will be saved to your account</li>
                {generateNotes && (
                  <li>3. AI will generate structured notes from the transcript</li>
                )}
                <li>{generateNotes ? '4' : '3'}. You can edit and enhance the notes as needed</li>
              </ul>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleImport}
                disabled={!videoUrl || loading}
                className="flex items-center gap-2"
              >
                <Youtube size={20} />
                Import Video
              </Button>
              <Button variant="secondary" onClick={onClose}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        {/* Processing Step */}
        {step === 'processing' && (
          <div className="text-center py-12">
            <Loader size={64} className="animate-spin mx-auto text-primary-600 mb-6" />
            <h4 className="text-xl font-semibold mb-2">Processing Video...</h4>
            <div className="space-y-2 text-gray-600 dark:text-gray-400">
              <p>⏳ Fetching video transcript...</p>
              {generateNotes && (
                <>
                  <p>🤖 Generating AI notes...</p>
                  <p>📝 Creating structured content...</p>
                </>
              )}
            </div>
            <div className="mt-6 p-4 bg-yellow-50 dark:bg-yellow-900 rounded-lg inline-block">
              <p className="text-sm">
                This may take 30-60 seconds depending on video length
              </p>
            </div>
          </div>
        )}

        {/* Success Step */}
        {step === 'success' && result && (
          <div className="space-y-6">
            <div className="text-center py-6">
              <CheckCircle size={64} className="mx-auto text-green-600 mb-4" />
              <h4 className="text-2xl font-semibold mb-2">Successfully Imported!</h4>
              <p className="text-gray-600 dark:text-gray-400">
                {result.video_title || 'Your video'} has been processed
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 border dark:border-gray-700 rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <Youtube size={20} className="text-red-600" />
                  <h5 className="font-semibold">Video Info</h5>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Transcript ID: {result.transcript_id}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Title: {result.video_title}
                </p>
              </div>

              {result.note_id && (
                <div className="p-4 border dark:border-gray-700 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText size={20} className="text-primary-600" />
                    <h5 className="font-semibold">Notes Created</h5>
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Note ID: {result.note_id}
                  </p>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Title: {result.note_title}
                  </p>
                </div>
              )}
            </div>

            <div className="p-4 bg-green-50 dark:bg-green-900 rounded-lg">
              <h5 className="font-semibold mb-2">✅ What's been done:</h5>
              <ul className="text-sm space-y-1">
                <li>✓ Video transcript extracted and saved</li>
                {result.note_id && (
                  <>
                    <li>✓ AI-generated notes created</li>
                    <li>✓ Source reference added to notes</li>
                  </>
                )}
                <li>✓ Ready for you to view and edit</li>
              </ul>
            </div>

            <div className="flex gap-2">
              <Button onClick={handleComplete} className="flex items-center gap-2">
                <CheckCircle size={20} />
                View Notes
              </Button>
              <Button variant="secondary" onClick={handleReset}>
                Import Another Video
              </Button>
            </div>
          </div>
        )}

        {/* Help Section */}
        {step === 'input' && (
          <div className="mt-6 border-t dark:border-gray-700 pt-6">
            <details className="cursor-pointer">
              <summary className="font-semibold text-sm mb-2">
                💡 Need help? Click here for tips
              </summary>
              <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2 mt-2">
                <p><strong>Supported URL formats:</strong></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>https://www.youtube.com/watch?v=VIDEO_ID</li>
                  <li>https://youtu.be/VIDEO_ID</li>
                  <li>https://www.youtube.com/embed/VIDEO_ID</li>
                </ul>
                <p className="mt-3"><strong>Note:</strong> Only videos with available transcripts can be imported. Educational and tutorial videos typically have transcripts available.</p>
              </div>
            </details>
          </div>
        )}
      </Card>
    </div>
  );
};

export default YouTubeImporter;