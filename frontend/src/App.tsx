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
import { Login, Register, StudentDashboard, SubmitAssignment, Grades } from './pages';
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
            path="/plagiarism"
            element={
              <AuthenticatedLayout>
                <PlagiarismCheck />
              </AuthenticatedLayout>
            }
          />
	          <Route
	            path="/report-analysis"
	            element={
	              <AuthenticatedLayout>
	                <ReportAnalysis />
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

