// FILE: src/App.jsx
// ============================================================================

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { Toaster } from 'react-hot-toast';
import { store } from './store';

// Pages
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CoursesPage from './pages/CoursesPage';
import CourseDetailPage from './pages/CourseDetailPage';
import NotesPage from './pages/NotesPage';
import RoadmapPage from './pages/RoadmapPage';
import AnalyticsPage from './pages/AnalyticsPage';
import ProfilePage from './pages/ProfilePage';
import PrivacyPolicy from './pages/PrivacyPolicy';
import TermsOfService from './pages/TermsOfService';

import DashboardPage from '@/pages/User_DashboardPage';
// Import other user pages as needed

// Admin Pages
import AdminDashboard from '@/pages/Admin_Dashboard';

// guards
import ProtectedRoute from '@/components/guards/ProtectedRoute';
import GuestRoute from '@/components/guards/GuestRoute';
import AdminRoute from '@/components/guards/AdminRoute';
import { useEffect } from 'react';

function App() {
  useEffect(() => {
    // Log current auth state for debugging
    const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
    const userStr = localStorage.getItem('user');
    
    console.log('[App] Auth State:', {
      hasToken: !!token,
      hasUser: !!userStr,
      user: userStr ? JSON.parse(userStr) : null
    });
  }, []);
  return (
    <Provider store={store}>
      <Router>
        <Toaster position="top-right" />
         <Routes>
        {/* Public Routes */}
        <Route path="/" element={
          <GuestRoute>
            <HomePage />
          </GuestRoute>
        } />
         <Route path="/login" element={
          <GuestRoute>
            <LoginPage />
          </GuestRoute>
        } />
          <Route path="/register" element={
          <GuestRoute>
            <RegisterPage />
          </GuestRoute>
        } />

                  {/* Add these two new routes */}
          <Route path="/privacy-policy" element={<PrivacyPolicy />} />
          <Route path="/terms-of-service" element={<TermsOfService />} />

        {/* User Dashboard - Student role (no role restriction = all authenticated users) */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        } />

         {/* Admin Dashboard - Admin role only */}
        <Route path="/admin-dashboard" element={
          <AdminRoute>
            <AdminDashboard />
          </AdminRoute>
        } />

          <Route path="/courses" element={
            <ProtectedRoute>
              <CoursesPage />
            </ProtectedRoute>
          } />
          <Route path="/courses/:slug" element={
            <ProtectedRoute>
              <CourseDetailPage />
            </ProtectedRoute>
          } />
          <Route path="/notes" element={
            <ProtectedRoute>
              <NotesPage />
            </ProtectedRoute>
          } />
          <Route path="/roadmap" element={
            <ProtectedRoute>
              <RoadmapPage />
            </ProtectedRoute>
          } />
          <Route path="/analytics" element={
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />

          {/* 404 */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </Provider>
  );
}

export default App;