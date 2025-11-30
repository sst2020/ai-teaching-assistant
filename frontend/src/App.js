/**
 * Material Design 3 - Main Application Component (JavaScript version)
 *
 * Note: The primary application uses App.tsx (TypeScript).
 * This file is kept for compatibility but App.tsx is the main entry point.
 */

import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { Header } from './components/layout';
import { Dashboard } from './components/Dashboard';
import { CodeAnalysis } from './components/CodeAnalysis';
import { QAInterface } from './components/QAInterface';
import { Login, Register, StudentDashboard, SubmitAssignment, Grades } from './pages';
import './App.css';

/**
 * AuthenticatedLayout - Wrapper for authenticated pages
 * Provides consistent layout with Header and MD3-styled main content area
 */
const AuthenticatedLayout = ({ children }) => {
  const location = useLocation();

  // Determine active tab based on current route path
  const getActiveTab = () => {
    const path = location.pathname;
    if (path.startsWith('/code-analysis')) return 'code-analysis';
    if (path.startsWith('/qa')) return 'qa';
    return 'dashboard';
  };

  const activeTab = getActiveTab();

  return (
    <>
      <Header activeTab={activeTab} />
      <main className="app-main">
        <div className="content-container">
          {children}
        </div>
      </main>
    </>
  );
};

/**
 * App - Main Application Component
 *
 * Implements MD3 Expressive theme with:
 * - Surface colors via CSS custom properties
 * - MD3 motion tokens for page transitions
 * - Proper spacing using 4dp grid system
 * - Elevation and shape specifications
 */
function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <div className="app">
          <Routes>
            {/* Public routes - no authentication required */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Authenticated routes with MD3 layout */}
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={
                <AuthenticatedLayout>
                  <Dashboard />
                </AuthenticatedLayout>
              }
            />
            <Route
              path="/code-analysis"
              element={
                <AuthenticatedLayout>
                  <CodeAnalysis />
                </AuthenticatedLayout>
              }
            />
            <Route
              path="/qa"
              element={
                <AuthenticatedLayout>
                  <QAInterface />
                </AuthenticatedLayout>
              }
            />
            <Route
              path="/student-dashboard"
              element={
                <AuthenticatedLayout>
                  <StudentDashboard />
                </AuthenticatedLayout>
              }
            />
            <Route
              path="/submit/:assignmentId"
              element={
                <AuthenticatedLayout>
                  <SubmitAssignment />
                </AuthenticatedLayout>
              }
            />
            <Route
              path="/grades"
              element={
                <AuthenticatedLayout>
                  <Grades />
                </AuthenticatedLayout>
              }
            />

            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
