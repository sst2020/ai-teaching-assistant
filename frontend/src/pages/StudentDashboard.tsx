import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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
        setError('Failed to load dashboard data. Please try again.');
        console.error('Dashboard error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const upcomingAssignments = assignments
    .filter(a => !a.submission || a.submission.status === 'pending')
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .slice(0, 5);

  const recentGrades = assignments
    .filter(a => a.submission?.grade !== undefined)
    .sort((a, b) => 
      new Date(b.submission?.submitted_at || 0).getTime() - 
      new Date(a.submission?.submitted_at || 0).getTime()
    )
    .slice(0, 5);

  if (isLoading) {
    return (
      <div className="student-dashboard-loading">
        <LoadingSpinner message="Loading your dashboard..." />
      </div>
    );
  }

  return (
    <div className="student-dashboard">
      <div className="dashboard-header">
        <h1>Welcome back, {user?.name || 'Student'}!</h1>
        <p className="dashboard-subtitle">Here's an overview of your academic progress</p>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-icon">📚</span>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_courses || 0}</span>
            <span className="stat-label">Enrolled Courses</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">📝</span>
          <div className="stat-content">
            <span className="stat-value">{stats?.pending_assignments || 0}</span>
            <span className="stat-label">Pending Assignments</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">✅</span>
          <div className="stat-content">
            <span className="stat-value">{stats?.total_submissions || 0}</span>
            <span className="stat-label">Submissions</span>
          </div>
        </div>
        <div className="stat-card">
          <span className="stat-icon">⭐</span>
          <div className="stat-content">
            <span className="stat-value">
              {stats?.average_grade ? `${stats.average_grade.toFixed(1)}%` : 'N/A'}
            </span>
            <span className="stat-label">Average Grade</span>
          </div>
        </div>
      </div>

      <div className="dashboard-content">
        {/* Upcoming Assignments */}
        <section className="dashboard-section">
          <div className="section-header">
            <h2>📅 Upcoming Assignments</h2>
            <Link to="/assignments" className="view-all-link">View All</Link>
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
                      Due: {formatDate(assignment.due_date)}
                    </span>
                    <Link 
                      to={`/submit/${assignment.id}`} 
                      className="submit-btn"
                    >
                      Submit
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-message">No upcoming assignments. Great job staying on top of things!</p>
          )}
        </section>

        {/* Enrolled Courses */}
        <section className="dashboard-section">
          <div className="section-header">
            <h2>📚 My Courses</h2>
            <Link to="/courses" className="view-all-link">View All</Link>
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
            <p className="empty-message">You're not enrolled in any courses yet.</p>
          )}
        </section>
      </div>
    </div>
  );
};

// Helper functions
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const isOverdue = (dateString: string): boolean => {
  return new Date(dateString) < new Date();
};

export default StudentDashboard;

