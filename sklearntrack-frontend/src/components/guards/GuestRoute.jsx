// FILE: src/components/guards/GuestRoute.jsx - UPDATED
// ============================================================================

import { Navigate } from 'react-router-dom';
import PropTypes from 'prop-types';

const GuestRoute = ({ children }) => {
  // Check if user is authenticated
  const token = localStorage.getItem('accessToken') || localStorage.getItem('token');
  const userStr = localStorage.getItem('user');

  // If user is authenticated, redirect to appropriate dashboard
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr);
      const isAdmin = user.role === 'admin' || user.is_staff || user.is_superuser;
      
      return <Navigate to={isAdmin ? '/admin-dashboard' : '/dashboard'} replace />;
    } catch (error) {
      console.error('Error parsing user data:', error);
      // If there's an error, still show the guest page
      return children;
    }
  }

  // User is not authenticated, show the guest page
  return children;
};

GuestRoute.propTypes = {
  children: PropTypes.node.isRequired,
};

export default GuestRoute;