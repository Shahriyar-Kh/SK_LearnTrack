// FILE: src/pages/RegisterPage.jsx - SIMPLIFIED WORKING VERSION
// ============================================================================

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL, EDUCATION_LEVELS } from '@/utils/constants';

const RegisterPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    full_name: '',
    country: '',
    education_level: 'undergraduate',
    field_of_study: '',
    terms_accepted: false,
  });
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.email) newErrors.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Email is invalid';
    
    if (!formData.password) newErrors.password = 'Password is required';
    else if (formData.password.length < 8) newErrors.password = 'Password must be at least 8 characters';
    
    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }
    
    if (!formData.full_name) newErrors.full_name = 'Full name is required';
    if (!formData.country) newErrors.country = 'Country is required';
    if (!formData.field_of_study) newErrors.field_of_study = 'Field of study is required';
    if (!formData.terms_accepted) newErrors.terms_accepted = 'You must accept the terms';
    
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setMessage({ type: 'error', text: 'Please fix the errors in the form' });
      return;
    }
    
    setLoading(true);
    setErrors({});
    setMessage({ type: '', text: '' });
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(formData),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        // Store tokens
        if (data.tokens) {
          localStorage.setItem('accessToken', data.tokens.access);
          localStorage.setItem('refreshToken', data.tokens.refresh);
          localStorage.setItem('user', JSON.stringify(data.user));
          localStorage.setItem('redirect', data.redirect || '/dashboard');
        }
        
        setMessage({
          type: 'success',
          text: data.message || 'Registration successful! Redirecting...',
        });
        
        // Redirect to dashboard
        setTimeout(() => {
          navigate(data.redirect || '/dashboard');
        }, 1500);
        
      } else {
        // Handle errors
        const errorData = data || {};
        setErrors(errorData);
        
        if (errorData.non_field_errors) {
          setMessage({ type: 'error', text: errorData.non_field_errors[0] });
        } else {
          setMessage({ type: 'error', text: 'Registration failed. Please check your information.' });
        }
      }
      
    } catch (error) {
      console.error('Registration error:', error);
      setMessage({
        type: 'error',
        text: 'Cannot connect to server. Please check your connection.'
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
        <div className="bg-white rounded-3xl shadow-2xl p-8 border border-gray-100">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
            <p className="text-gray-600">Join SK-LearnTrack and start your learning journey</p>
          </div>
          
          {message.text && (
            <div className={`mb-6 p-4 rounded-xl ${
              message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
              'bg-red-50 text-red-800 border border-red-200'
            }`}>
              <div className="flex items-center gap-2">
                <span className="text-lg">{message.type === 'success' ? '✅' : '⚠️'}</span>
                <span className="font-medium">{message.text}</span>
              </div>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.full_name ? 'border-red-500' : 'border-gray-200'
                  }`}
                  placeholder="John Doe"
                  disabled={loading}
                />
                {errors.full_name && (
                  <p className="text-red-500 text-sm mt-1">{errors.full_name}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email *
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.email ? 'border-red-500' : 'border-gray-200'
                  }`}
                  placeholder="your@email.com"
                  disabled={loading}
                />
                {errors.email && (
                  <p className="text-red-500 text-sm mt-1">{errors.email}</p>
                )}
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password *
                </label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.password ? 'border-red-500' : 'border-gray-200'
                  }`}
                  placeholder="••••••••"
                  disabled={loading}
                />
                {errors.password && (
                  <p className="text-red-500 text-sm mt-1">{errors.password}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password *
                </label>
                <input
                  type="password"
                  name="password_confirm"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.password_confirm ? 'border-red-500' : 'border-gray-200'
                  }`}
                  placeholder="••••••••"
                  disabled={loading}
                />
                {errors.password_confirm && (
                  <p className="text-red-500 text-sm mt-1">{errors.password_confirm}</p>
                )}
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Country *
                </label>
                <input
                  type="text"
                  name="country"
                  value={formData.country}
                  onChange={handleChange}
                  className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    errors.country ? 'border-red-500' : 'border-gray-200'
                  }`}
                  placeholder="United States"
                  disabled={loading}
                />
                {errors.country && (
                  <p className="text-red-500 text-sm mt-1">{errors.country}</p>
                )}
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Education Level *
                </label>
                <select
                  name="education_level"
                  value={formData.education_level}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  disabled={loading}
                >
                  {EDUCATION_LEVELS.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Field of Study *
              </label>
              <input
                type="text"
                name="field_of_study"
                value={formData.field_of_study}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.field_of_study ? 'border-red-500' : 'border-gray-200'
                }`}
                placeholder="Computer Science, Business, Medicine, etc."
                disabled={loading}
              />
              {errors.field_of_study && (
                <p className="text-red-500 text-sm mt-1">{errors.field_of_study}</p>
              )}
            </div>
            
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="terms"
                name="terms_accepted"
                checked={formData.terms_accepted}
                onChange={handleChange}
                className="w-5 h-5 mt-1"
                disabled={loading}
              />
              <label htmlFor="terms" className="text-sm text-gray-600">
                I agree to the{' '}
                <button 
                  type="button" 
                  onClick={() => navigate('/terms')}
                  className="text-blue-600 hover:text-blue-700"
                >
                  Terms of Service
                </button>{' '}
                and{' '}
                <button 
                  type="button" 
                  onClick={() => navigate('/privacy')}
                  className="text-blue-600 hover:text-blue-700"
                >
                  Privacy Policy
                </button>
              </label>
            </div>
            {errors.terms_accepted && (
              <p className="text-red-500 text-sm">{errors.terms_accepted}</p>
            )}
            
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Creating Account...
                </div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>
          
          <p className="text-center mt-6 text-gray-600">
            Already have an account?{' '}
            <button
              onClick={() => navigate('/login')}
              className="text-blue-600 hover:text-blue-700 font-semibold"
              disabled={loading}
            >
              Sign in
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;