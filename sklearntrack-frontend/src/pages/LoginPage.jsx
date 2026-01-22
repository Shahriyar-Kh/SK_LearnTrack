// FILE: src/pages/LoginPage.jsx - FIXED WITH SPECIFIC ERROR MESSAGES
// ============================================================================

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, Eye, EyeOff, BookOpen, ArrowRight, Shield, CheckCircle, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '@/utils/constants';

const LoginPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [googleInitialized, setGoogleInitialized] = useState(false);
  const [fieldErrors, setFieldErrors] = useState({ email: '', password: '' }); // ✅ NEW: Field-level errors

  useEffect(() => {
    const initGoogleOAuth = () => {
      if (window.google && window.google.accounts && window.google.accounts.id) {
        const clientId = import.meta.env.VITE_GOOGLE_OAUTH_CLIENT_ID;
        
        if (!clientId || clientId === 'your-google-client-id.apps.googleusercontent.com') {
          console.error('[Google OAuth] Client ID is not configured');
          return;
        }

        try {
          window.google.accounts.id.initialize({
            client_id: clientId,
            callback: handleGoogleResponse,
            auto_select: false,
            cancel_on_tap_outside: true,
            context: 'signin',
            ux_mode: 'popup',
          });
          
          const buttonDiv = document.getElementById('google-signin-button');
          if (buttonDiv && buttonDiv.children.length === 0) {
            window.google.accounts.id.renderButton(
              buttonDiv,
              {
                theme: 'outline',
                size: 'large',
                width: 300,
                text: 'continue_with',
                shape: 'pill',
                logo_alignment: 'center',
              }
            );
            setGoogleInitialized(true);
          }
        } catch (error) {
          console.error('[Google OAuth] Initialization error:', error);
        }
      }
    };

    if (!document.querySelector('script[src*="accounts.google.com/gsi/client"]')) {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => initGoogleOAuth();
      document.body.appendChild(script);
    } else {
      initGoogleOAuth();
    }
  }, []);

const handleGoogleResponse = async (response) => {
  try {
    setLoading(true);
    setMessage({ type: '', text: '' });
    
    if (!response.credential) {
      throw new Error('No credential received from Google');
    }
    
    const res = await fetch(`${API_BASE_URL}/api/auth/google_auth/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ credential: response.credential }),
    });
    
    const data = await res.json();

    if (!res.ok) {
      // 🔒 SECURITY: Use error_type to show user-friendly messages
      if (data.error_type === 'google_auth_failed' || data.error_type === 'google_auth_error') {
        throw new Error(data.detail || 'Google authentication failed. Please try again.');
      } else if (data.error_type === 'account_disabled') {
        throw new Error('Your account has been disabled. Please contact support.');
      } else {
        throw new Error(data.detail || data.error || 'Authentication failed');
      }
    }

    if (data.tokens) {
      localStorage.setItem('accessToken', data.tokens.access);
      localStorage.setItem('token', data.tokens.access);
      localStorage.setItem('refreshToken', data.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(data.user));
    }

    setMessage({
      type: 'success',
      text: data.is_new_user ? 'Welcome! Account created successfully!' : 'Login successful!',
    });

    setTimeout(() => {
      navigate(data.redirect || '/dashboard');
    }, 1000);

  } catch (error) {
    console.error('[Google OAuth] Error:', error);
    // 🔒 SECURITY: Never show raw error messages from backend
    setMessage({
      type: 'error',
      text: error.message || 'Google authentication failed. Please try again or use email login.',
    });
  } finally {
    setLoading(false);
  }
};
  // ✅ NEW: Email format validation
  const validateEmail = (email) => {
    if (!email) {
      return 'Email is required';
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Please enter a valid email address';
    }
    return '';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // ✅ FIXED: Frontend validation before API call
    const errors = {
      email: '',
      password: ''
    };

    // Validate email format
    const emailError = validateEmail(formData.email);
    if (emailError) {
      errors.email = emailError;
      setFieldErrors(errors);
      setMessage({ type: 'error', text: emailError });
      return;
    }

    // Validate password exists
    if (!formData.password) {
      errors.password = 'Password is required';
      setFieldErrors(errors);
      setMessage({ type: 'error', text: 'Password is required' });
      return;
    }

    setLoading(true);
    setMessage({ type: '', text: '' });
    setFieldErrors({ email: '', password: '' });

    try {
      console.log('[Email Login] Attempting login for:', formData.email);
      
      const response = await fetch(`${API_BASE_URL}/api/token/`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email.toLowerCase().trim(),
          password: formData.password,
        }),
      });

      const data = await response.json();
      console.log('[Email Login] Response:', data);

      if (response.ok) {
        // Store tokens
        localStorage.setItem('accessToken', data.access);
        localStorage.setItem('token', data.access);
        localStorage.setItem('refreshToken', data.refresh);
        localStorage.setItem('user', JSON.stringify(data.user));

        setMessage({ type: 'success', text: 'Login successful! Redirecting...' });

        setTimeout(() => {
          navigate(data.redirect || '/dashboard');
        }, 1000);
      } else {
        // ✅ FIXED: Handle specific error types from backend
        const errorType = data.error_type;
        const errorDetail = data.detail;

        if (errorType === 'email_not_found') {
          setFieldErrors({ ...errors, email: errorDetail });
          setMessage({
            type: 'error',
            text: errorDetail || 'This email is not registered. Please sign up first.',
          });
        } else if (errorType === 'incorrect_password') {
          setFieldErrors({ ...errors, password: errorDetail });
          setMessage({
            type: 'error',
            text: errorDetail || 'Incorrect password. Please try again.',
          });
        } else if (errorType === 'account_disabled') {
          setMessage({
            type: 'error',
            text: errorDetail || 'This account has been disabled. Please contact support.',
          });
        } else {
          // Generic error
          setMessage({
            type: 'error',
            text: errorDetail || 'Login failed. Please check your credentials.',
          });
        }
      }
    } catch (error) {
      console.error('[Email Login] Error:', error);
      setMessage({ 
        type: 'error', 
        text: 'Cannot connect to server. Please check your connection.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const features = [
    'AI-Enhanced Note Taking',
    'Personalized Learning Roadmaps',
    'Comprehensive Analytics',
    'Secure Cloud Sync',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Blobs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
      <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-40 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>

      <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center relative z-10">
        {/* Left Side - Branding */}
        <div className="hidden lg:block space-y-6 p-8">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg">
              <BookOpen className="w-8 h-8 text-white" />
            </div>
            <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              SK-LearnTrack
            </span>
          </div>

          <h1 className="text-5xl font-bold text-gray-900 leading-tight">
            Welcome Back to Your
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
              Learning Journey
            </span>
          </h1>

          <p className="text-xl text-gray-600">
            Continue building your skills with AI-powered study tools and personalized learning paths.
          </p>

          <div className="space-y-4 pt-8">
            {features.map((feature, idx) => (
              <div key={idx} className="flex items-center gap-3 group">
                <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                  <CheckCircle className="w-5 h-5 text-white" />
                </div>
                <span className="text-gray-700 font-medium text-lg">{feature}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right Side - Login Form */}
        <div className="w-full max-w-md mx-auto">
          <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-gray-100">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="lg:hidden flex items-center justify-center gap-2 mb-6">
                <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl">
                  <BookOpen className="w-6 h-6 text-white" />
                </div>
                <span className="text-2xl font-bold text-gray-900">SK-LearnTrack</span>
              </div>

              <h2 className="text-3xl font-bold text-gray-900 mb-2">Sign In</h2>
              <p className="text-gray-600">Welcome back! Please enter your details</p>
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

            {/* Google Sign In */}
            <div className="mb-6">
              <div id="google-signin-button" className="w-full flex justify-center"></div>
              {!googleInitialized && !message.text && (
                <div className="text-center text-sm text-gray-500 mt-2">
                  Loading Google Sign-In...
                </div>
              )}
            </div>

            {/* Divider */}
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-200"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Or continue with email</span>
              </div>
            </div>

            {/* Login Form */}
            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => {
                      setFormData({ ...formData, email: e.target.value });
                      // Clear email error when typing
                      if (fieldErrors.email) {
                        setFieldErrors({ ...fieldErrors, email: '' });
                      }
                    }}
                    className={`w-full pl-12 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white ${
                      fieldErrors.email ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="your@email.com"
                    autoComplete="email"
                    required
                    disabled={loading}
                  />
                </div>
                {/* ✅ NEW: Show field-specific error */}
                {fieldErrors.email && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {fieldErrors.email}
                  </p>
                )}
              </div>

              {/* Password Input */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">Password</label>
                  <button
                    type="button"
                    onClick={() => navigate('/forgot-password')}
                    className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    disabled={loading}
                  >
                    Forgot?
                  </button>
                </div>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    value={formData.password}
                    onChange={(e) => {
                      setFormData({ ...formData, password: e.target.value });
                      // Clear password error when typing
                      if (fieldErrors.password) {
                        setFieldErrors({ ...fieldErrors, password: '' });
                      }
                    }}
                    className={`w-full pl-12 pr-12 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-white ${
                      fieldErrors.password ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="••••••••"
                    autoComplete="current-password"
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
                {/* ✅ NEW: Show field-specific error */}
                {fieldErrors.password && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {fieldErrors.password}
                  </p>
                )}
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
                    Sign In
                    <ArrowRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </form>

            {/* Security Badge */}
            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
              <Shield className="w-4 h-4" />
              <span>Secured with 256-bit encryption</span>
            </div>

            {/* Sign Up Link */}
            <p className="mt-6 text-center text-gray-600">
              Don't have an account?{' '}
              <button
                onClick={() => navigate('/register')}
                className="text-blue-600 hover:text-blue-700 font-semibold"
                disabled={loading}
              >
                Sign up for free
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;