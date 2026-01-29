// FILE: src/components/guards/GuestRoute.jsx - UPDATED
// ============================================================================

import { Navigate, useLocation } from 'react-router-dom';
import PropTypes from 'prop-types';

const GuestRoute = ({ children }) => {
  const location = useLocation();
  
  // List of pages that should be accessible even when logged in
  const publicRoutes = ['/reset-password', '/verify-email', '/forgot-password'];
  
  // Check if current route is a public route
  const isPublicRoute = publicRoutes.some(route => 
    location.pathname.startsWith(route)
  );

  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  const userStr = localStorage.getItem('user');

  // If user is authenticated AND NOT trying to access a public route, redirect
  if (token && userStr && !isPublicRoute) {
    try {
      const user = JSON.parse(userStr);
      const isAdmin = user.role === 'admin' || user.is_staff || user.is_superuser;

      // Redirect admins to the admin app entry point
      return <Navigate to={isAdmin ? '/admin' : '/dashboard'} replace />;
    } catch (error) {
      console.error('Error parsing user data:', error);
      // If there's an error, show the page
      return children;
    }
  }

  // User is not authenticated OR accessing a public route, show the page
  return children;
};

GuestRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default GuestRoute;