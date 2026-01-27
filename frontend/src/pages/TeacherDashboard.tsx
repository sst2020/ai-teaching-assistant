/**
 * 教师仪表板页面 - 综合管理界面
 *
 * 功能:
 * - 作业管理概览
 * - 评分统计
 * - 待处理任务
 * - 快速操作入口
 */
import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  getAssignments,
  getAssignmentStats,
  getTriageStats,
} from '../services/api';
import { Assignment, AssignmentStats } from '../types/assignment';
import { TriageStats } from '../types/triage';
import ManagementSystemNotice from '../components/ManagementSystemNotice';
import './TeacherDashboard.css';

interface DashboardStats {
  assignments: AssignmentStats | null;
  triage: TriageStats | null;
}

const TeacherDashboard: React.FC = () => {
  const { t, i18n } = useTranslation('teacher');
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stats, setStats] = useState<DashboardStats>({ assignments: null, triage: null });
  const [recentAssignments, setRecentAssignments] = useState<Assignment[]>([]);
  // 预留用于未来的标签切换功能
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [activeTab, setActiveTab] = useState<'overview' | 'assignments' | 'grading' | 'questions'>('overview');

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [assignmentStats, triageStats, assignmentsResponse] = await Promise.all([
        getAssignmentStats().catch(() => null),
        getTriageStats().catch(() => null),
        getAssignments({ page: 1, page_size: 5 }).catch(() => ({ items: [], assignments: [] })),
      ]);

      setStats({
        assignments: assignmentStats,
        triage: triageStats,
      });
      setRecentAssignments(assignmentsResponse.items || assignmentsResponse.assignments || []);
    } catch (err) {
      setError(t('dashboard.error'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [t]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const locale = i18n.language === 'zh' ? 'zh-CN' : 'en-US';
    return date.toLocaleDateString(locale, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (assignment: Assignment) => {
    const now = new Date();
    const dueDate = new Date(assignment.due_date);
    if (!assignment.is_published) {
      return <span className="badge draft">{t('recentAssignments.status.draft')}</span>;
    }
    if (dueDate < now) {
      return <span className="badge expired">{t('recentAssignments.status.expired')}</span>;
    }
    return <span className="badge active">{t('recentAssignments.status.active')}</span>;
  };

  if (loading) {
    return (
      <div className="teacher-dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>{t('dashboard.loading')}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="teacher-dashboard">
      <header className="dashboard-header">
        <h1>{`📚 ${t('dashboard.title')}`}</h1>
        <div className="header-actions">
          <button className="btn-secondary" onClick={loadDashboardData}>
            🔄 {t('dashboard.refresh')}
          </button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* 管理系统引导提示 */}
      <ManagementSystemNotice variant="banner" dismissible={true} />

      {/* 统计卡片 */}
      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <h3>{stats.assignments?.total_assignments || 0}</h3>
            <p>{t('stats.totalAssignments')}</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>{stats.assignments?.pending_count || 0}</h3>
            <p>{t('stats.pendingGrading')}</p>
          </div>
        </div>
        <div className="stat-card highlight">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{stats.assignments?.graded_count || 0}</h3>
            <p>{t('stats.graded')}</p>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">❓</div>
          <div className="stat-content">
            <h3>{stats.triage?.pending || 0}</h3>
            <p>{t('stats.pendingQuestions')}</p>
          </div>
        </div>
      </section>

      {/* 快速操作 */}
      <section className="quick-actions">
        <h2>{t('quickActions.title')}</h2>
        <div className="action-grid">
          <Link to="/grading" className="action-card">
            <span className="action-icon">✏️</span>
            <span className="action-label">{t('quickActions.grading')}</span>
          </Link>
          <Link to="/question-queue" className="action-card">
            <span className="action-icon">💬</span>
            <span className="action-label">{t('quickActions.questionQueue')}</span>
          </Link>
          <Link to="/analytics" className="action-card">
            <span className="action-icon">📊</span>
            <span className="action-label">{t('quickActions.analytics')}</span>
          </Link>
        </div>
      </section>

      {/* 最近作业 */}
      <section className="recent-assignments">
        <div className="section-header">
          <h2>{t('recentAssignments.title')}</h2>
        </div>
        <div className="assignments-table">
          {recentAssignments.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>{t('recentAssignments.columns.title')}</th>
                  <th>{t('recentAssignments.columns.type')}</th>
                  <th>{t('recentAssignments.columns.dueDate')}</th>
                  <th>{t('recentAssignments.columns.status')}</th>
                  <th>{t('recentAssignments.columns.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {recentAssignments.map((assignment) => (
                  <tr key={assignment.id}>
                    <td className="assignment-title">{assignment.title}</td>
                    <td>
                      <span className={`type-badge ${assignment.assignment_type}`}>
                        {assignment.assignment_type === 'code' && `💻 ${t('recentAssignments.types.code')}`}
                        {assignment.assignment_type === 'essay' && `📝 ${t('recentAssignments.types.essay')}`}
                        {assignment.assignment_type === 'quiz' && `❓ ${t('recentAssignments.types.quiz')}`}
                        {assignment.assignment_type === 'project' && `🎯 ${t('recentAssignments.types.project')}`}
                      </span>
                    </td>
                    <td>{formatDate(assignment.due_date)}</td>
                    <td>{getStatusBadge(assignment)}</td>
                    <td className="actions">
                      <button
                        className="btn-icon"
                        onClick={() => navigate(`/grading?assignment=${assignment.id}`)}
                        title={t('quickActions.grading')}
                      >
                        ✏️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p>{t('recentAssignments.empty')}</p>
              <p className="empty-hint">{t('recentAssignments.syncHint')}</p>
            </div>
          )}
        </div>
      </section>

      {/* 待处理提醒 */}
      {(stats.triage?.urgent_pending || 0) > 0 && (
        <section className="urgent-alerts">
          <div className="alert-card urgent">
            <span className="alert-icon">🚨</span>
            <div className="alert-content">
              <h4>{t('urgentAlerts.title')}</h4>
              <p>{t('urgentAlerts.message', { count: stats.triage?.urgent_pending })}</p>
            </div>
            <Link to="/question-queue" className="alert-action">
              {t('urgentAlerts.action')}
            </Link>
          </div>
        </section>
      )}
    </div>
  );
};

export default TeacherDashboard;

