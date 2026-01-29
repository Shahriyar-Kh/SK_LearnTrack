
// FILE: src/components/guards/AdminRoute.jsx
// =============================================================================

import { Navigate } from 'react-router-dom';

/**
 * Admin-Only Route Component
 * Restricts access to admin users only
 */
const AdminRoute = ({ children }) => {
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  const userStr = localStorage.getItem('user');

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  try {
    const user = userStr ? JSON.parse(userStr) : null;
    
    if (!user) {
      return <Navigate to="/login" replace />;
    }

    // Check if user is admin
    const isAdmin = user.role === 'admin' || user.is_staff || user.is_superuser;

    if (!isAdmin) {
      // Not an admin - redirect to user dashboard
      console.warn('Non-admin user attempted to access admin page');
      return <Navigate to="/dashboard" replace />;
    }

    return children;
  } catch (error) {
    console.error('Error parsing user data:', error);
    return <Navigate to="/login" replace />;
  }
};

export default AdminRoute;