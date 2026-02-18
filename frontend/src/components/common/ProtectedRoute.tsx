import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import LoadingSpinner from './LoadingSpinner';
import Forbidden from '../../pages/Forbidden';
import './ProtectedRoute.css';

/**
 * 根据用户角色获取默认首页路径
 */
export const getRoleHomePath = (role?: string): string => {
  switch (role) {
    case 'admin':
      return '/dashboard';
    case 'teacher':
      return '/manage-assignments';
    case 'student':
      return '/dashboard';
    default:
      return '/login';
  }
};

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
 * When access is denied, redirects to the user's role-based home page.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requiredRole,
  allowedRoles,
  fallbackPath,
  showForbiddenPage = false
}) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  // 根据角色计算实际的 fallback 路径
  const resolvedFallbackPath = fallbackPath || getRoleHomePath(user?.role);

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
    if (showForbiddenPage) {
      return <Forbidden />;
    }
    return <Navigate to={resolvedFallbackPath} replace />;
  }

  // Check for allowed roles if specified
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    if (showForbiddenPage) {
      return <Forbidden />;
    }
    return <Navigate to={resolvedFallbackPath} replace />;
  }

  // User is authenticated (and has required role if specified)
  return <>{children}</>;
};

export default ProtectedRoute;

