/**
 * Material Design 3 - Main Application Component
 *
 * Main entry point for the AI Teaching Assistant frontend.
 * Implements MD3 Expressive theme with routing and authentication.
 */

import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { Header } from './components/layout';
import { Dashboard } from './components/Dashboard';
import { CodeAnalysis } from './components/CodeAnalysis';
import { QAInterface } from './components/QAInterface';
import { PlagiarismCheck } from './components/PlagiarismCheck';
import { ReportAnalysis } from './components/ReportAnalysis';
import { DebugPanel } from './components/common/DebugPanel';
import ProtectedRoute from './components/common/ProtectedRoute';
import { KnowledgeBase, QATriage, TeacherDashboard } from './components';
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
    if (path.startsWith('/plagiarism')) return 'plagiarism';
    if (path.startsWith('/report-analysis')) return 'report-analysis';
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
  const [debugPanelVisible, setDebugPanelVisible] = useState(false);

  // Check if debug panel is enabled
  const isDebugMode = process.env.NODE_ENV === 'development' &&
                     process.env.REACT_APP_ENABLE_DEBUG_PANEL === 'true';

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
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <Dashboard />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/code-analysis"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <CodeAnalysis />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/qa"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <QAInterface />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/plagiarism"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <PlagiarismCheck />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/report-analysis"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <ReportAnalysis />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/student-dashboard"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <StudentDashboard />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/submit/:assignmentId"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <SubmitAssignment />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/grades"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <Grades />
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />

            {/* 智能问答分诊系统路由 */}
            <Route
              path="/smart-qa"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <React.Suspense fallback={<div>加载中...</div>}>
                      <QATriage userId="current_user" userName="当前用户" />
                    </React.Suspense>
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-base"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <React.Suspense fallback={<div>加载中...</div>}>
                      <KnowledgeBase />
                    </React.Suspense>
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/teacher-dashboard"
              element={
                <ProtectedRoute>
                  <AuthenticatedLayout>
                    <React.Suspense fallback={<div>加载中...</div>}>
                      <TeacherDashboard teacherId="teacher_001" teacherName="教师" />
                    </React.Suspense>
                  </AuthenticatedLayout>
                </ProtectedRoute>
              }
            />

            {/* Fallback route */}
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>

          {/* Debug Panel - 仅在开发环境下显示 */}
          {isDebugMode && (
            <DebugPanel
              isVisible={debugPanelVisible}
              onToggle={() => setDebugPanelVisible(!debugPanelVisible)}
            />
          )}
        </div>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
