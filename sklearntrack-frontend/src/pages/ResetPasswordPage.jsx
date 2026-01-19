// FILE: src/pages/ResetPasswordPage.jsx
// ============================================================================

import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Lock, Eye, EyeOff, BookOpen, CheckCircle, AlertCircle, ArrowRight } from 'lucide-react';
import { API_BASE_URL } from '@/utils/constants';

const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({
    new_password: '',
    new_password_confirm: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [resetSuccess, setResetSuccess] = useState(false);

  useEffect(() => {
    // Check if token exists
    if (!token) {
      setMessage({
        type: 'error',
        text: 'Invalid reset link. Please request a new password reset.',
      });
    }
  }, [token]);

  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) {
      errors.push('Password must be at least 8 characters');
    }
    if (!/[A-Z]/.test(password)) {
      errors.push('Include at least one uppercase letter');
    }
    if (!/[a-z]/.test(password)) {
      errors.push('Include at least one lowercase letter');
    }
    if (!/[0-9]/.test(password)) {
      errors.push('Include at least one number');
    }
    return errors;
  };

  const clearAuthData = () => {
    // Clear all authentication data from localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('user');
    localStorage.removeItem('userRole');
    localStorage.removeItem('isAuthenticated');
    
    // Clear sessionStorage as well
    sessionStorage.removeItem('authToken');
    sessionStorage.removeItem('refreshToken');
    sessionStorage.removeItem('user');
    sessionStorage.removeItem('userRole');
    sessionStorage.removeItem('isAuthenticated');
    
    // Clear any cookies that might be set
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validate passwords match
    if (formData.new_password !== formData.new_password_confirm) {
      setMessage({ type: 'error', text: 'Passwords do not match' });
      return;
    }

    // Validate password strength
    const validationErrors = validatePassword(formData.new_password);
    if (validationErrors.length > 0) {
      setMessage({ type: 'error', text: validationErrors.join('. ') });
      return;
    }

    if (!token) {
      setMessage({ type: 'error', text: 'Invalid reset token' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/reset_password/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          new_password: formData.new_password,
          new_password_confirm: formData.new_password_confirm,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Clear all authentication data before showing success
        clearAuthData();
        
        setResetSuccess(true);
        setMessage({
          type: 'success',
          text: data.message || 'Password reset successful! Redirecting to login...',
        });

        // Clear any pending timeouts to prevent multiple redirects
        const existingTimeout = setTimeout(() => {}, 0);
        clearTimeout(existingTimeout);

        // Redirect to login after 3 seconds
        setTimeout(() => {
          navigate('/login', { replace: true });
        }, 3000);
      } else {
        setMessage({
          type: 'error',
          text: data.error || 'Failed to reset password. The link may have expired.',
        });
      }
    } catch (error) {
      console.error('Reset password error:', error);
      setMessage({
        type: 'error',
        text: 'Cannot connect to server. Please check your connection.',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleGoToLogin = () => {
    clearAuthData();
    navigate('/login', { replace: true });
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

            <h2 className="text-3xl font-bold text-gray-900 mb-2">Reset Password</h2>
            <p className="text-gray-600">
              {resetSuccess ? 'Password updated successfully!' : 'Create a new secure password'}
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

          {!resetSuccess && token && (
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* New Password Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.new_password}
                    onChange={(e) =>
                      setFormData({ ...formData, new_password: e.target.value })
                    }
                    className="w-full pl-12 pr-12 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white"
                    placeholder="••••••••"
                    required
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    disabled={loading}
                  >
                    {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  Must be 8+ characters with uppercase, lowercase, and numbers
                </p>
              </div>

              {/* Confirm Password Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm New Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={formData.new_password_confirm}
                    onChange={(e) =>
                      setFormData({ ...formData, new_password_confirm: e.target.value })
                    }
                    className="w-full pl-12 pr-12 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white"
                    placeholder="••••••••"
                    required
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    disabled={loading}
                  >
                    {showConfirmPassword ? (
                      <EyeOff className="w-5 h-5" />
                    ) : (
                      <Eye className="w-5 h-5" />
                    )}
                  </button>
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
                  <>
                    Reset Password
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>
          )}

          {resetSuccess && (
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
              <p className="text-gray-600 mb-4">Redirecting to login page...</p>
              <button
                onClick={handleGoToLogin}
                className="text-blue-600 hover:text-blue-700 font-semibold"
              >
                Go to Login Now
              </button>
            </div>
          )}

          {!token && (
            <div className="text-center">
              <button
                onClick={() => navigate('/forgot-password')}
                className="text-blue-600 hover:text-blue-700 font-semibold"
              >
                Request New Reset Link
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResetPasswordPage;