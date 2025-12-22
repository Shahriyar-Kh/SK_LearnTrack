// FILE: src/pages/RegisterPage.jsx
// ============================================================================

import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { register } from '@/store/slices/authSlice';
import toast from 'react-hot-toast';
import Navbar from '@/components/layout/Navbar';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';
import { EDUCATION_LEVELS } from '@/utils/constants';

const RegisterPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    password_confirm: '',
    full_name: '',
    country: '',
    education_level: 'undergraduate',
    field_of_study: '',
    learning_goal: '',
    preferred_study_hours: 2,
    timezone: 'UTC',
    terms_accepted: false,
  });

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading } = useSelector((state) => state.auth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.password_confirm) {
      toast.error('Passwords do not match');
      return;
    }

    if (!formData.terms_accepted) {
      toast.error('Please accept terms and conditions');
      return;
    }

    try {
      await dispatch(register(formData)).unwrap();
      toast.success('Registration successful!');
      navigate('/dashboard');
    } catch (error) {
      toast.error(error?.detail || 'Registration failed');
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
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  required
                />
                
                <Input
                  label="Username"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  required
                />
              </div>

              <Input
                label="Email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                required
              />

              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  label="Password"
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  required
                />
                
                <Input
                  label="Confirm Password"
                  type="password"
                  value={formData.password_confirm}
                  onChange={(e) => setFormData({ ...formData, password_confirm: e.target.value })}
                  required
                />
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <Input
                  label="Country"
                  value={formData.country}
                  onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                  required
                />
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Education Level
                  </label>
                  <select
                    className="input-field"
                    value={formData.education_level}
                    onChange={(e) => setFormData({ ...formData, education_level: e.target.value })}
                    required
                  >
                    {EDUCATION_LEVELS.map((level) => (
                      <option key={level.value} value={level.value}>
                        {level.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <Input
                label="Field of Study"
                value={formData.field_of_study}
                onChange={(e) => setFormData({ ...formData, field_of_study: e.target.value })}
                required
              />

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="terms"
                  checked={formData.terms_accepted}
                  onChange={(e) => setFormData({ ...formData, terms_accepted: e.target.checked })}
                  className="w-4 h-4"
                />
                <label htmlFor="terms" className="text-sm text-gray-600 dark:text-gray-400">
                  I accept the terms and conditions
                </label>
              </div>

              <Button type="submit" loading={loading} className="w-full">
                Create Account
              </Button>
            </form>

            <p className="text-center mt-6 text-gray-600 dark:text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="text-primary-600 hover:text-primary-700 font-medium">
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
