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
import {
  getAssignments,
  getAssignmentStats,
  getTriageStats,
} from '../services/api';
import { Assignment, AssignmentStats } from '../types/assignment';
import { TriageStats } from '../types/triage';
import './TeacherDashboard.css';

interface DashboardStats {
  assignments: AssignmentStats | null;
  triage: TriageStats | null;
}

const TeacherDashboard: React.FC = () => {
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
      setError('加载仪表板数据失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
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
      return <span className="badge draft">草稿</span>;
    }
    if (dueDate < now) {
      return <span className="badge expired">已截止</span>;
    }
    return <span className="badge active">进行中</span>;
  };

  if (loading) {
    return (
      <div className="teacher-dashboard">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>加载中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="teacher-dashboard">
      <header className="dashboard-header">
        <h1>📚 教师工作台</h1>
        <div className="header-actions">
          <button className="btn-primary" onClick={() => navigate('/manage-assignments')}>
            ➕ 新建作业
          </button>
          <button className="btn-secondary" onClick={loadDashboardData}>
            🔄 刷新
          </button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* 统计卡片 */}
      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📝</div>
          <div className="stat-content">
            <h3>{stats.assignments?.total_assignments || 0}</h3>
            <p>总作业数</p>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">⏳</div>
          <div className="stat-content">
            <h3>{stats.assignments?.pending_count || 0}</h3>
            <p>待批改</p>
          </div>
        </div>
        <div className="stat-card highlight">
          <div className="stat-icon">✅</div>
          <div className="stat-content">
            <h3>{stats.assignments?.graded_count || 0}</h3>
            <p>已批改</p>
          </div>
        </div>
        <div className="stat-card warning">
          <div className="stat-icon">❓</div>
          <div className="stat-content">
            <h3>{stats.triage?.pending || 0}</h3>
            <p>待回答问题</p>
          </div>
        </div>
      </section>

      {/* 快速操作 */}
      <section className="quick-actions">
        <h2>快速操作</h2>
        <div className="action-grid">
          <Link to="/manage-assignments" className="action-card">
            <span className="action-icon">📋</span>
            <span className="action-label">作业管理</span>
          </Link>
          <Link to="/grading" className="action-card">
            <span className="action-icon">✏️</span>
            <span className="action-label">批改作业</span>
          </Link>
          <Link to="/question-queue" className="action-card">
            <span className="action-icon">💬</span>
            <span className="action-label">问题队列</span>
          </Link>
          <Link to="/analytics" className="action-card">
            <span className="action-icon">📊</span>
            <span className="action-label">数据分析</span>
          </Link>
        </div>
      </section>

      {/* 最近作业 */}
      <section className="recent-assignments">
        <div className="section-header">
          <h2>最近作业</h2>
          <Link to="/manage-assignments" className="view-all">查看全部 →</Link>
        </div>
        <div className="assignments-table">
          {recentAssignments.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>作业标题</th>
                  <th>类型</th>
                  <th>截止日期</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {recentAssignments.map((assignment) => (
                  <tr key={assignment.id}>
                    <td className="assignment-title">{assignment.title}</td>
                    <td>
                      <span className={`type-badge ${assignment.assignment_type}`}>
                        {assignment.assignment_type === 'code' && '💻 代码'}
                        {assignment.assignment_type === 'essay' && '📝 论文'}
                        {assignment.assignment_type === 'quiz' && '❓ 测验'}
                        {assignment.assignment_type === 'project' && '🎯 项目'}
                      </span>
                    </td>
                    <td>{formatDate(assignment.due_date)}</td>
                    <td>{getStatusBadge(assignment)}</td>
                    <td className="actions">
                      <button
                        className="btn-icon"
                        onClick={() => navigate(`/grading?assignment=${assignment.id}`)}
                        title="批改"
                      >
                        ✏️
                      </button>
                      <button
                        className="btn-icon"
                        onClick={() => navigate(`/manage-assignments?edit=${assignment.id}`)}
                        title="编辑"
                      >
                        ⚙️
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <p>暂无作业</p>
              <button className="btn-primary" onClick={() => navigate('/manage-assignments')}>
                创建第一个作业
              </button>
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
              <h4>紧急问题待处理</h4>
              <p>有 {stats.triage?.urgent_pending} 个紧急问题需要您的关注</p>
            </div>
            <Link to="/question-queue" className="alert-action">
              立即处理
            </Link>
          </div>
        </section>
      )}
    </div>
  );
};

export default TeacherDashboard;

