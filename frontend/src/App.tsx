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
import { KnowledgeBase, QATriage, TeacherDashboard as TeacherQuestionQueue } from './components';
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
} from './pages';
import './App.css';

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
    <AuthProvider>
      <ToastProvider>
        <div className="app">
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Authenticated routes with layout */}
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
            path="/question-queue"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <React.Suspense fallback={<div>加载中...</div>}>
                    <TeacherQuestionQueue teacherId="teacher_001" teacherName="教师" />
                  </React.Suspense>
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* 教师端路由 */}
          <Route
            path="/teacher"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <TeacherDashboard />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/manage-assignments"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <ManageAssignments />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/grading"
            element={
              <ProtectedRoute>
                <AuthenticatedLayout>
                  <GradingInterface />
                </AuthenticatedLayout>
              </ProtectedRoute>
            }
          />

          {/* 账户设置路由 */}
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

          {/* Fallback route for unknown paths */}
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
};

export default App;

