// FILE: src/pages/ForgotPasswordPage.jsx
// ============================================================================

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, ArrowLeft, BookOpen, CheckCircle, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '@/utils/constants';

const ForgotPasswordPage = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [emailSent, setEmailSent] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!email) {
      setMessage({ type: 'error', text: 'Please enter your email address' });
      return;
    }

    if (!/\S+@\S+\.\S+/.test(email)) {
      setMessage({ type: 'error', text: 'Please enter a valid email address' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/request_password_reset/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ email: email.toLowerCase().trim() }),
      });

      const data = await response.json();

      if (response.ok) {
        setEmailSent(true);
        setMessage({
          type: 'success',
          text: data.message || 'Password reset link sent! Please check your email.',
        });
      } else {
        setMessage({
          type: 'error',
          text: data.error || 'Failed to send reset link. Please try again.',
        });
      }
    } catch (error) {
      console.error('Forgot password error:', error);
      setMessage({
        type: 'error',
        text: 'Cannot connect to server. Please check your connection.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Blobs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
      <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-40 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-gray-100">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-6">
              <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold text-gray-900">SK-LearnTrack</span>
            </div>

            <h2 className="text-3xl font-bold text-gray-900 mb-2">Forgot Password?</h2>
            <p className="text-gray-600">
              {emailSent
                ? "We've sent you a reset link"
                : "No worries, we'll send you reset instructions"}
            </p>
          </div>

          {/* Message Display */}
          {message.text && (
            <div
              className={`mb-6 p-4 rounded-xl ${
                message.type === 'success'
                  ? 'bg-green-50 text-green-800 border border-green-200'
                  : 'bg-red-50 text-red-800 border border-red-200'
              }`}
            >
              <div className="flex items-center gap-2">
                {message.type === 'success' ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <AlertCircle className="w-5 h-5" />
                )}
                <span className="font-medium">{message.text}</span>
              </div>
            </div>
          )}

          {!emailSent ? (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white"
                    placeholder="your@email.com"
                    autoComplete="email"
                    required
                    disabled={loading}
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                ) : (
                  'Send Reset Link'
                )}
              </button>
            </form>
          ) : (
            <div className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
                <p className="text-sm text-blue-800">
                  Check your email <strong>{email}</strong> for a link to reset your password. If it
                  doesn't appear within a few minutes, check your spam folder.
                </p>
              </div>

              <button
                onClick={() => {
                  setEmailSent(false);
                  setMessage({ type: '', text: '' });
                }}
                className="w-full bg-gray-100 text-gray-700 py-3 rounded-xl font-semibold hover:bg-gray-200 transition-all duration-200"
              >
                Try Another Email
              </button>
            </div>
          )}

          {/* Back to Login */}
          <button
            onClick={() => navigate('/login')}
            className="w-full mt-6 flex items-center justify-center gap-2 text-gray-600 hover:text-gray-900 font-medium transition-colors"
            disabled={loading}
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Login
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForgotPasswordPage;