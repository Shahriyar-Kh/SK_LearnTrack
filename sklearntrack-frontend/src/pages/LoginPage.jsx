// FILE: src/pages/LoginPage.jsx
// ============================================================================

import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { login, clearError } from '@/store/slices/authSlice';
import toast from 'react-hot-toast';
import Navbar from '@/components/layout/Navbar';
import Input from '@/components/common/Input';
import Button from '@/components/common/Button';
import Card from '@/components/common/Card';

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, isAuthenticated, redirect, user } = useSelector((state) => state.auth);

  // Clear errors on mount
  useEffect(() => {
    dispatch(clearError());
  }, [dispatch]);

  // Handle successful authentication
  useEffect(() => {
    if (isAuthenticated && user) {
      // Determine redirect based on user role
      const redirectPath = user.role === 'admin' || user.is_staff || user.is_superuser
        ? '/admin-dashboard'
        : '/dashboard';
      
      navigate(redirectPath);
    }
  }, [isAuthenticated, user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate inputs
    if (!formData.email || !formData.password) {
      toast.error('Please fill in all fields');
      return;
    }

    try {
      const result = await dispatch(login(formData)).unwrap();
      toast.success('Login successful!');
      
      // Navigate based on redirect URL from response
      const redirectPath = result.redirect || '/dashboard';
      navigate(redirectPath);
    } catch (error) {
      console.error('Login error:', error);
      const errorMessage = error?.detail || error?.message || 'Login failed. Please check your credentials.';
      toast.error(errorMessage);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-20">
        <div className="max-w-md mx-auto">
          <Card>
            <h2 className="text-3xl font-bold text-center mb-6">Welcome Back</h2>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                label="Email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                required
                autoComplete="email"
              />
              
              <Input
                label="Password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                required
                autoComplete="current-password"
              />

              <Button 
                type="submit" 
                loading={loading} 
                className="w-full"
                disabled={loading}
              >
                {loading ? 'Signing in...' : 'Sign In'}
              </Button>
            </form>

            <p className="text-center mt-6 text-gray-600 dark:text-gray-400">
              Don't have an account?{' '}
              <Link 
                to="/register" 
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Sign up
              </Link>
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;