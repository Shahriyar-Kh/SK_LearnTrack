// FILE: src/pages/RegisterPage.jsx
// ============================================================================

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { register, clearError } from '@/store/slices/authSlice';
import toast from 'react-hot-toast';
import Navbar from '@/components/layout/Navbar';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { EDUCATION_LEVELS } from '@/utils/constants';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    full_name: '',
    country: '',
    education_level: 'undergraduate',
    field_of_study: '',
    learning_goal: '',
    preferred_study_hours: 2,
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC',
    terms_accepted: false,
  });

  const [errors, setErrors] = useState({});

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, isAuthenticated, user } = useSelector((state) => state.auth);

  // Clear errors on mount
  useEffect(() => {
    dispatch(clearError());
  }, [dispatch]);

  // Handle successful authentication
  useEffect(() => {
    if (isAuthenticated && user) {
      toast.success('Registration successful! Welcome to SkLearnTrack!');
      navigate('/dashboard'); // Always redirect to user dashboard after registration
    }
  }, [isAuthenticated, user, navigate]);

  const validateForm = () => {
    const newErrors = {};

    // Email validation
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }

    // Password validation
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }

    // Password confirmation
    if (formData.password !== formData.password_confirm) {
      newErrors.password_confirm = 'Passwords do not match';
    }

    // Required fields
    if (!formData.full_name) newErrors.full_name = 'Full name is required';
    if (!formData.country) newErrors.country = 'Country is required';
    if (!formData.field_of_study) newErrors.field_of_study = 'Field of study is required';

    // Terms acceptance
    if (!formData.terms_accepted) {
      newErrors.terms_accepted = 'You must accept the terms and conditions';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear previous errors
    setErrors({});

    // Validate form
    if (!validateForm()) {
      toast.error('Please fix the errors in the form');
      return;
    }

    try {
      await dispatch(register(formData)).unwrap();
      // Success handling is done in useEffect
    } catch (error) {
      console.error('Registration error:', error);
      
      // Handle specific field errors
      if (typeof error === 'object' && error !== null) {
        setErrors(error);
        
        // Show specific error messages
        Object.entries(error).forEach(([field, messages]) => {
          const message = Array.isArray(messages) ? messages[0] : messages;
          toast.error(`${field}: ${message}`);
        });
      } else {
        toast.error(error?.detail || 'Registration failed. Please try again.');
      }
    }
  };

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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-10">
        <div className="max-w-2xl mx-auto">
          <Card>
            <h2 className="text-3xl font-bold text-center mb-6">Create Your Account</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  label="Full Name"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  required
                  error={errors.full_name}
                  placeholder="John Doe"
                />
                
                <Input
                  label="Email"
                  name="email"
                  type="email"
                  value={formData.email}
                  onChange={handleChange}
                  required
                  error={errors.email}
                  placeholder="your@email.com"
                  autoComplete="email"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  label="Password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleChange}
                  required
                  error={errors.password}
                  placeholder="••••••••"
                  autoComplete="new-password"
                />
                
                <Input
                  label="Confirm Password"
                  name="password_confirm"
                  type="password"
                  value={formData.password_confirm}
                  onChange={handleChange}
                  required
                  error={errors.password_confirm}
                  placeholder="••••••••"
                  autoComplete="new-password"
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  label="Country"
                  name="country"
                  value={formData.country}
                  onChange={handleChange}
                  required
                  error={errors.country}
                  placeholder="United States"
                />
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Education Level *
                  </label>
                  <select
                    name="education_level"
                    className={`input-field ${errors.education_level ? 'border-red-500' : ''}`}
                    value={formData.education_level}
                    onChange={handleChange}
                    required
                  >
                    {EDUCATION_LEVELS.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                  {errors.education_level && (
                    <p className="text-red-500 text-sm mt-1">{errors.education_level}</p>
                  )}
                </div>
              </div>

              <Input
                label="Field of Study"
                name="field_of_study"
                value={formData.field_of_study}
                onChange={handleChange}
                required
                error={errors.field_of_study}
                placeholder="Computer Science"
              />

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Learning Goal (Optional)
                </label>
                <textarea
                  name="learning_goal"
                  className="input-field"
                  value={formData.learning_goal}
                  onChange={handleChange}
                  rows="3"
                  placeholder="What do you want to achieve?"
                />
              </div>

              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="terms"
                  name="terms_accepted"
                  checked={formData.terms_accepted}
                  onChange={handleChange}
                  className="w-4 h-4 mt-1"
                />
                <label htmlFor="terms" className="text-sm text-gray-600 dark:text-gray-400">
                  I accept the terms and conditions *
                </label>
              </div>
              {errors.terms_accepted && (
                <p className="text-red-500 text-sm">{errors.terms_accepted}</p>
              )}

              <Button 
                type="submit" 
                loading={loading} 
                className="w-full"
                disabled={loading}
              >
                {loading ? 'Creating Account...' : 'Create Account'}
              </Button>
            </form>

            <p className="text-center mt-6 text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link 
                to="/login" 
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Sign in
              </Link>
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;