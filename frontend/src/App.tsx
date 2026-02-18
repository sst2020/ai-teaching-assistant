import React, { useState } from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import { ThemeProvider } from './contexts/ThemeContext';
import { Header } from './components/layout';
import { Dashboard } from './components/Dashboard';
import { CodeAnalysis } from './components/CodeAnalysis';
import { QAInterface } from './components/QAInterface';
import { PlagiarismCheck } from './components/PlagiarismCheck';
import { ReportAnalysis } from './components/ReportAnalysis';
import { DebugPanel } from './components/common/DebugPanel';
import ErrorBoundary from './components/common/ErrorBoundary';
import ProtectedRoute from './components/common/ProtectedRoute';
import { getRoleHomePath } from './components/common/ProtectedRoute';
import { KnowledgeBase, QATriage, TeacherDashboard as TeacherQuestionQueue } from './components';
import { ApiTester, PerformanceMonitor } from './components/DevTools';
import {
  Login,
  Register,
  StudentDashboard,
  SubmitAssignment,
  Grades,
  TeacherDashboard,
  ManageAssignments,
  GradingInterface,
  Account,
  Forbidden,
} from './pages';
import './App.css';

/**
 * 根据用户角色重定向到对应首页的组件
 */
const RoleBasedRedirect: React.FC = () => {
  const { user, isAuthenticated, isLoading } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={getRoleHomePath(user?.role)} replace />;
};

// Layout component for authenticated pages
const AuthenticatedLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation();

  // Helper to determine active tab based on current path
  const getActiveTab = (): string => {
    const path = location.pathname;
    if (path.startsWith('/code-analysis')) return 'code-analysis';
    if (path.startsWith('/qa')) return 'qa';
    if (path.startsWith('/plagiarism')) return 'plagiarism';
    if (path.startsWith('/report-analysis')) return 'report-analysis';
    if (path.startsWith('/teacher')) return 'teacher';
    if (path.startsWith('/grading')) return 'grading';
    if (path.startsWith('/manage-assignments')) return 'manage-assignments';
    if (path.startsWith('/question-queue')) return 'question-queue';
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

const App: React.FC = () => {
  const [debugPanelVisible, setDebugPanelVisible] = useState(false);

  // 检查是否启用调试面板
  const isDebugMode = process.env.NODE_ENV === 'development' &&
                     process.env.REACT_APP_ENABLE_DEBUG_PANEL === 'true';

  return (
    <ErrorBoundary>
      <AuthProvider>
        <ToastProvider>
          <ThemeProvider>
            <div className="app">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* 根路径：按角色智能跳转 */}
          <Route
            path="/"
            element={<RoleBasedRedirect />}
          />

          {/* Student routes - student + admin 可访问 */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute allowedRoles={['student', 'admin']}>
                <AuthenticatedLayout>
                  <StudentDashboard />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/submit/:assignmentId"
            element={
              <ProtectedRoute allowedRoles={['student', 'admin']}>
                <AuthenticatedLayout>
                  <SubmitAssignment />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/grades"
            element={
              <ProtectedRoute allowedRoles={['student', 'admin']}>
                <AuthenticatedLayout>
                  <Grades />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* Common routes for students and teachers */}
          <Route
            path="/smart-qa"
            element={
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin']}>
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
              <ProtectedRoute allowedRoles={['student', 'teacher', 'admin']}>
                <AuthenticatedLayout>
                  <React.Suspense fallback={<div>加载中...</div>}>
                    <KnowledgeBase />
                  </React.Suspense>
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* Teacher/Admin routes - teacher + admin 可访问 */}
          <Route
            path="/teacher"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <TeacherDashboard />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/manage-assignments"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <ManageAssignments />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/grading"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <GradingInterface />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/question-queue"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <React.Suspense fallback={<div>加载中...</div>}>
                    <TeacherQuestionQueue teacherId="teacher_001" teacherName="教师" />
                  </React.Suspense>
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* Advanced features for teachers and admins */}
          <Route
            path="/code-analysis"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <CodeAnalysis />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/qa"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <QAInterface />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/plagiarism"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <PlagiarismCheck />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/report-analysis"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <ReportAnalysis />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* Developer tools - development environment only */}
          <Route
            path="/dev/api-tester"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <ApiTester />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/dev/performance-monitor"
            element={
              <ProtectedRoute allowedRoles={['teacher', 'admin']}>
                <AuthenticatedLayout>
                  <PerformanceMonitor />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* Account settings - accessible to all authenticated users */}
          <Route
            path="/account"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <Account />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* 403 Forbidden route */}
          <Route
            path="/forbidden"
            element={
              <ProtectedRoute showForbiddenPage={true}>
                <Forbidden />
              </ProtectedRoute>
            }
          />

          {/* Fallback route for unknown paths - 按角色跳转到对应首页 */}
          <Route
            path="*"
            element={<RoleBasedRedirect />}
          />
        </Routes>

        {/* Debug Panel - 仅在开发环境下显示 */}
        {isDebugMode && (
          <DebugPanel
            isVisible={debugPanelVisible}
            onToggle={() => setDebugPanelVisible(!debugPanelVisible)}
          />
        )}
            </div>
          </ThemeProvider>
        </ToastProvider>
      </AuthProvider>
    </ErrorBoundary>
  );
};

export default App;
