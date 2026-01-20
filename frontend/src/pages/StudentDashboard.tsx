import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import {
  getStudentStats,
  getEnrolledCourses,
  getAssignmentsWithSubmissions
} from '../services/api';
import { StudentStats, Course, AssignmentWithSubmission } from '../types';
import './StudentDashboard.css';

const StudentDashboard: React.FC = () => {
  const { t, i18n } = useTranslation('student');
  const { user } = useAuth();
  const [stats, setStats] = useState<StudentStats | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [assignments, setAssignments] = useState<AssignmentWithSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const [statsData, coursesData, assignmentsData] = await Promise.all([
          getStudentStats(),
          getEnrolledCourses(),
          getAssignmentsWithSubmissions(),
        ]);

        setStats(statsData);
        setCourses(coursesData);
        setAssignments(assignmentsData);
      } catch (err) {
        setError(t('dashboard.error'));
        console.error('Dashboard error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, [t]);

  const upcomingAssignments = assignments
    .filter(a => !a.submission || a.submission.status === 'pending')
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .slice(0, 5);

  // 格式化日期，根据当前语言
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const locale = i18n.language === 'zh' ? 'zh-CN' : 'en-US';
    return date.toLocaleDateString(locale, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const isOverdue = (dateString: string): boolean => {
    return new Date(dateString) < new Date();
  };

  if (isLoading) {
    return (
      <div className="student-dashboard-loading">
        <LoadingSpinner message={t('dashboard.loading')} />
      </div>
    );
  }

  return (
    <div className="student-dashboard">
      <div className="dashboard-header">
        <h1>{t('dashboard.welcome')}, {user?.name || 'Student'}!</h1>
        <p className="dashboard-subtitle">{t('dashboard.title')}</p>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon">📚</span>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_courses || 0}</span>
            <span className="stat-label">{t('stats.enrolledCourses')}</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">📝</span>
          <div className="stat-content">
            <span className="stat-value">{stats?.pending_assignments || 0}</span>
            <span className="stat-label">{t('stats.pendingAssignments')}</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">✅</span>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_submissions || 0}</span>
            <span className="stat-label">{t('stats.submissions')}</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">⭐</span>
          <div className="stat-content">
            <span className="stat-value">
              {stats?.average_grade ? `${stats.average_grade.toFixed(1)}%` : 'N/A'}
            </span>
            <span className="stat-label">{t('stats.averageGrade')}</span>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Upcoming Assignments */}
        <section className="dashboard-section">
          <div className="section-header">
            <h2>📅 {t('assignments.upcoming')}</h2>
            <Link to="/assignments" className="view-all-link">{t('assignments.viewAll')}</Link>
          </div>
          {upcomingAssignments.length > 0 ? (
            <div className="assignment-list">
              {upcomingAssignments.map(assignment => (
                <div key={assignment.id} className="assignment-card">
                  <div className="assignment-info">
                    <h3>{assignment.title}</h3>
                    <p className="assignment-course">{assignment.course_id}</p>
                  </div>
                  <div className="assignment-meta">
                    <span className={`due-date ${isOverdue(assignment.due_date) ? 'overdue' : ''}`}>
                      {t('assignments.due')}: {formatDate(assignment.due_date)}
                    </span>
                    <Link
                      to={`/submit/${assignment.id}`}
                      className="submit-btn"
                    >
                      {t('assignments.submit')}
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-message">{t('assignments.empty')}</p>
          )}
        </section>

        {/* Enrolled Courses */}
        <section className="dashboard-section">
          <div className="section-header">
            <h2>📚 {t('courses.title')}</h2>
            <Link to="/courses" className="view-all-link">{t('courses.viewAll')}</Link>
          </div>
          {courses.length > 0 ? (
            <div className="courses-grid">
              {courses.slice(0, 4).map(course => (
                <div key={course.id} className="course-card">
                  <h3>{course.name}</h3>
                  <p className="course-code">{course.code}</p>
                  <p className="course-instructor">👨‍🏫 {course.instructor_name}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-message">{t('courses.empty')}</p>
          )}
        </section>
      </div>
    </div>
  );
};

export default StudentDashboard;

