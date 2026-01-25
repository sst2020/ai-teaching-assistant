import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';
import Forbidden from '../../pages/Forbidden';
import './ProtectedRoute.css';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'student' | 'teacher' | 'admin';
  allowedRoles?: ('student' | 'teacher' | 'admin')[]; // Allow multiple roles
  fallbackPath?: string; // Custom fallback path for unauthorized access
  showForbiddenPage?: boolean; // Whether to show forbidden page instead of redirecting
}

/**
 * ProtectedRoute component that wraps routes requiring authentication.
 * Redirects to login page if user is not authenticated.
 * Optionally checks for specific user roles.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  allowedRoles,
  fallbackPath = '/dashboard',
  showForbiddenPage = false
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="protected-route-loading">
        <LoadingSpinner message="Checking authentication..." />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save the attempted URL for redirecting after login
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check for required role if specified
  if (requiredRole && user?.role !== requiredRole) {
    // User doesn't have the required role
    if (showForbiddenPage) {
      return <Forbidden />;
    }
    return <Navigate to={fallbackPath} replace />;
  }

  // Check for allowed roles if specified
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    // User doesn't have any of the allowed roles
    if (showForbiddenPage) {
      return <Forbidden />;
    }
    return <Navigate to={fallbackPath} replace />;
  }

  // User is authenticated (and has required role if specified)
  return <>{children}</>;
};

export default ProtectedRoute;

