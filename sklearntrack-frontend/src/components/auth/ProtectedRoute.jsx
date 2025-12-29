// FILE: src/components/routing/ProtectedRoute.jsx
// ============================================================================

import { Navigate, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';
import PropTypes from 'prop-types';

const ProtectedRoute = ({ children, requiredRole = null, redirectTo = '/login' }) => {
  const location = useLocation();
  const { isAuthenticated, user } = useSelector((state) => state.auth);

  // If not authenticated, redirect to login
  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  // If specific role is required, check user's role
  if (requiredRole) {
    const hasRequiredRole = checkRole(user, requiredRole);
    
    if (!hasRequiredRole) {
      // Redirect based on user's actual role
      if (user?.role === 'admin' || user?.is_staff || user?.is_superuser) {
        return <Navigate to="/admin-dashboard" replace />;
      }
      return <Navigate to="/dashboard" replace />;
    }
  }

  return children;
};

// Helper function to check if user has required role
const checkRole = (user, requiredRole) => {
  if (!user) return false;

  // Handle array of allowed roles
  if (Array.isArray(requiredRole)) {
    return requiredRole.some(role => hasRole(user, role));
  }

  return hasRole(user, requiredRole);
};

// Check if user has specific role
const hasRole = (user, role) => {
  switch (role) {
    case 'admin':
      return user.role === 'admin' || user.is_staff || user.is_superuser;
    case 'student':
      return user.role === 'student' && !user.is_staff && !user.is_superuser;
    case 'any':
      return true;
    default:
      return user.role === role;
  }
};

ProtectedRoute.propTypes = {
  children: PropTypes.node.isRequired,
  requiredRole: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.arrayOf(PropTypes.string)
  ]),
  redirectTo: PropTypes.string,
};

export default ProtectedRoute;