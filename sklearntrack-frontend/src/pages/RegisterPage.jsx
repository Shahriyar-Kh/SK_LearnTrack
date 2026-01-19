// FILE: src/pages/RegisterPage.jsx - FIXED WITH PROPER REDIRECT
// ============================================================================

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Mail, Lock, User, Globe, GraduationCap, BookOpen, Eye, EyeOff, CheckCircle, AlertCircle, ArrowRight, Shield } from 'lucide-react';
import { API_BASE_URL } from '@/utils/constants';

const EDUCATION_LEVELS = [
  { value: 'high_school', label: 'High School' },
  { value: 'undergraduate', label: 'Undergraduate' },
  { value: 'graduate', label: 'Graduate' },
  { value: 'postgraduate', label: 'Postgraduate' },
  { value: 'professional', label: 'Professional' },
];

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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});
  const [message, setMessage] = useState({ type: '', text: '' });
  const [touchedFields, setTouchedFields] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const handleBlur = (fieldName) => {
    setTouchedFields(prev => ({ ...prev, [fieldName]: true }));
    validateField(fieldName, formData[fieldName]);
  };

  const validateField = (fieldName, value) => {
    const newErrors = { ...errors };
    
    switch (fieldName) {
      case 'email':
        if (!value) {
          newErrors.email = 'Email is required';
        } else if (!/\S+@\S+\.\S+/.test(value)) {
          newErrors.email = 'Please enter a valid email';
        } else {
          delete newErrors.email;
        }
        break;
      case 'password':
        if (!value) {
          newErrors.password = 'Password is required';
        } else if (value.length < 8) {
          newErrors.password = 'Must be at least 8 characters';
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(value)) {
          newErrors.password = 'Include uppercase, lowercase, and number';
        } else {
          delete newErrors.password;
        }
        break;
      case 'password_confirm':
        if (value !== formData.password) {
          newErrors.password_confirm = 'Passwords do not match';
        } else {
          delete newErrors.password_confirm;
        }
        break;
      case 'full_name':
        if (!value || value.trim().length < 2) {
          newErrors.full_name = 'Please enter your full name';
        } else {
          delete newErrors.full_name;
        }
        break;
      case 'country':
        if (!value) {
          newErrors.country = 'Country is required';
        } else {
          delete newErrors.country;
        }
        break;
      case 'field_of_study':
        if (!value) {
          newErrors.field_of_study = 'Field of study is required';
        } else {
          delete newErrors.field_of_study;
        }
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
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
    
    // Mark all fields as touched
    const allFields = Object.keys(formData);
    const touched = {};
    allFields.forEach(field => touched[field] = true);
    setTouchedFields(touched);
    
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
      console.log('[Registration] Submitting:', formData.email);
      
      const response = await fetch(`${API_BASE_URL}/api/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          email: formData.email.toLowerCase().trim(),
          password: formData.password,
          password_confirm: formData.password_confirm,
          full_name: formData.full_name.trim(),
          country: formData.country.trim(),
          education_level: formData.education_level,
          field_of_study: formData.field_of_study.trim(),
          terms_accepted: formData.terms_accepted,
        }),
      });

      const data = await response.json();
      console.log('[Registration] Response:', data);

      if (response.ok && data.success) {
        // ✅ FIXED: Store tokens if provided
        if (data.tokens) {
          localStorage.setItem('accessToken', data.tokens.access);
          localStorage.setItem('token', data.tokens.access);
          localStorage.setItem('refreshToken', data.tokens.refresh);
          localStorage.setItem('user', JSON.stringify(data.user));
        }

        setMessage({
          type: 'success',
          text: data.message || 'Registration successful! Redirecting to login...',
        });

        // ✅ FIXED: Redirect to login page after 2 seconds
        setTimeout(() => {
          navigate('/login');
        }, 2000);

      } else {
        // Handle validation errors from backend
        if (data.errors) {
          setErrors(data.errors);
          setMessage({
            type: 'error',
            text: 'Please fix the errors below',
          });
        } else {
          setMessage({
            type: 'error',
            text: data.detail || data.error || 'Registration failed. Please try again.',
          });
        }
      }
    } catch (error) {
      console.error('[Registration] Error:', error);
      setMessage({
        type: 'error',
        text: 'Cannot connect to server. Please check your connection.',
      });
    } finally {
      setLoading(false);
    }
  };

  const getFieldError = (fieldName) => {
    return touchedFields[fieldName] && errors[fieldName];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Background Blobs */}
      <div className="absolute top-20 left-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
      <div className="absolute top-40 right-10 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
      <div className="absolute -bottom-8 left-40 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>

      <div className="w-full max-w-2xl relative z-10">
        <div className="bg-white/80 backdrop-blur-lg rounded-3xl shadow-2xl p-8 border border-gray-100">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-6">
              <div className="p-3 bg-gradient-to-br from-blue-600 to-purple-600 rounded-2xl shadow-lg">
                <BookOpen className="w-8 h-8 text-white" />
              </div>
              <span className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                SK-LearnTrack
              </span>
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Create Your Account</h1>
            <p className="text-gray-600">Join thousands of learners on their journey to success</p>
          </div>
          
          {/* Message Display */}
          {message.text && (
            <div className={`mb-6 p-4 rounded-xl ${
              message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' :
              'bg-red-50 text-red-800 border border-red-200'
            }`}>
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
          
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Personal Information */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                    onBlur={() => handleBlur('full_name')}
                    className={`w-full pl-12 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      getFieldError('full_name') ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="John Doe"
                    disabled={loading}
                  />
                </div>
                {getFieldError('full_name') && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.full_name}
                  </p>
                )}
              </div>
              
              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    onBlur={() => handleBlur('email')}
                    className={`w-full pl-12 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      getFieldError('email') ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="your@email.com"
                    autoComplete="email"
                    disabled={loading}
                  />
                </div>
                {getFieldError('email') && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.email}
                  </p>
                )}
              </div>
            </div>
            
            {/* Password Fields */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    onBlur={() => handleBlur('password')}
                    className={`w-full pl-12 pr-12 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      getFieldError('password') ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="••••••••"
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
                {getFieldError('password') && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.password}
                  </p>
                )}
              </div>
              
              {/* Confirm Password */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confirm Password *
                </label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type={showConfirmPassword ? 'text' : 'password'}
                    name="password_confirm"
                    value={formData.password_confirm}
                    onChange={handleChange}
                    onBlur={() => handleBlur('password_confirm')}
                    className={`w-full pl-12 pr-12 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      getFieldError('password_confirm') ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="••••••••"
                    disabled={loading}
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    disabled={loading}
                  >
                    {showConfirmPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
                {getFieldError('password_confirm') && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.password_confirm}
                  </p>
                )}
              </div>
            </div>
            
            {/* Academic Information */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Country */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Country *
                </label>
                <div className="relative">
                  <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    name="country"
                    value={formData.country}
                    onChange={handleChange}
                    onBlur={() => handleBlur('country')}
                    className={`w-full pl-12 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                      getFieldError('country') ? 'border-red-500' : 'border-gray-200'
                    }`}
                    placeholder="United States"
                    disabled={loading}
                  />
                </div>
                {getFieldError('country') && (
                  <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    {errors.country}
                  </p>
                )}
              </div>
              
              {/* Education Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Education Level *
                </label>
                <div className="relative">
                  <GraduationCap className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none z-10" />
                  <select
                    name="education_level"
                    value={formData.education_level}
                    onChange={handleChange}
                    className="w-full pl-12 pr-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all appearance-none bg-white"
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
            </div>
            
            {/* Field of Study */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Field of Study *
              </label>
              <div className="relative">
                <BookOpen className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  name="field_of_study"
                  value={formData.field_of_study}
                  onChange={handleChange}
                  onBlur={() => handleBlur('field_of_study')}
                  className={`w-full pl-12 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
                    getFieldError('field_of_study') ? 'border-red-500' : 'border-gray-200'
                  }`}
                  placeholder="Computer Science, Business, Medicine, etc."
                  disabled={loading}
                />
              </div>
              {getFieldError('field_of_study') && (
                <p className="text-red-500 text-sm mt-1 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.field_of_study}
                </p>
              )}
            </div>
            
            {/* Terms and Conditions */}
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  id="terms"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  className="w-5 h-5 mt-0.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 cursor-pointer"
                  disabled={loading}
                />
                <label htmlFor="terms" className="text-sm text-gray-700 cursor-pointer">
                  I agree to the{' '}
                  <span className="text-blue-600 hover:text-blue-700 font-medium">
                    Terms of Service
                  </span>{' '}
                  and{' '}
                  <span className="text-blue-600 hover:text-blue-700 font-medium">
                    Privacy Policy
                  </span>
                </label>
              </div>
              {errors.terms_accepted && touchedFields.terms_accepted && (
                <p className="text-red-500 text-sm mt-2 flex items-center gap-1">
                  <AlertCircle className="w-4 h-4" />
                  {errors.terms_accepted}
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
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Creating Account...
                </>
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
          
          {/* Security Badge */}
          <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
            <Shield className="w-4 h-4" />
            <span>Your information is secure and encrypted</span>
          </div>
          
          {/* Sign In Link */}
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