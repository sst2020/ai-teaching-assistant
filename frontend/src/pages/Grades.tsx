import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { getSubmissions } from '../services/api';
import { Submission } from '../types';
import './Grades.css';

const Grades: React.FC = () => {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'graded' | 'pending'>('all');

  useEffect(() => {
    const fetchGrades = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await getSubmissions({ status: 'graded' });
        setSubmissions(response.submissions);
      } catch (err) {
        setError('Failed to load grades. Please try again.');
        console.error('Grades fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGrades();
  }, []);

  const filteredSubmissions = submissions.filter(sub => {
    if (filter === 'graded') return sub.grade !== undefined;
    if (filter === 'pending') return sub.grade === undefined;
    return true;
  });

  const averageGrade = submissions
    .filter(s => s.grade !== undefined)
    .reduce((acc, s, _, arr) => acc + (s.grade! / s.max_grade * 100) / arr.length, 0);

  if (isLoading) {
    return (
      <div className="grades-loading">
        <LoadingSpinner message="Loading your grades..." />
      </div>
    );
  }

  return (
    <div className="grades-page">
      <div className="grades-header">
        <div className="header-content">
          <h1>📊 My Grades</h1>
          <p className="grades-subtitle">View your graded assignments and feedback</p>
        </div>
        <Link to="/student-dashboard" className="back-link">
          ← Back to Dashboard
        </Link>
      </div>

      {error && <ErrorMessage message={error} />}

      {/* Summary Stats */}
      <div className="grades-summary">
        <div className="summary-card">
          <span className="summary-value">{submissions.length}</span>
          <span className="summary-label">Total Submissions</span>
        </div>
        <div className="summary-card">
          <span className="summary-value">
            {submissions.filter(s => s.grade !== undefined).length}
          </span>
          <span className="summary-label">Graded</span>
        </div>
        <div className="summary-card">
          <span className="summary-value">
            {submissions.filter(s => s.grade === undefined).length}
          </span>
          <span className="summary-label">Pending</span>
        </div>
        <div className="summary-card highlight">
          <span className="summary-value">
            {averageGrade > 0 ? `${averageGrade.toFixed(1)}%` : 'N/A'}
          </span>
          <span className="summary-label">Average Grade</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="filter-tabs">
        <button 
          className={`filter-tab ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({submissions.length})
        </button>
        <button 
          className={`filter-tab ${filter === 'graded' ? 'active' : ''}`}
          onClick={() => setFilter('graded')}
        >
          Graded ({submissions.filter(s => s.grade !== undefined).length})
        </button>
        <button 
          className={`filter-tab ${filter === 'pending' ? 'active' : ''}`}
          onClick={() => setFilter('pending')}
        >
          Pending ({submissions.filter(s => s.grade === undefined).length})
        </button>
      </div>

      {/* Grades List */}
      <div className="grades-list">
        {filteredSubmissions.length > 0 ? (
          filteredSubmissions.map(submission => (
            <GradeCard key={submission.id} submission={submission} />
          ))
        ) : (
          <div className="empty-state">
            <span className="empty-icon">📝</span>
            <p>No submissions found</p>
          </div>
        )}
      </div>
    </div>
  );
};

interface GradeCardProps {
  submission: Submission;
}

const GradeCard: React.FC<GradeCardProps> = ({ submission }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const gradePercent = submission.grade !== undefined 
    ? (submission.grade / submission.max_grade * 100) 
    : null;
  
  const getGradeClass = (percent: number | null): string => {
    if (percent === null) return 'pending';
    if (percent >= 90) return 'excellent';
    if (percent >= 80) return 'good';
    if (percent >= 70) return 'average';
    if (percent >= 60) return 'below-average';
    return 'needs-improvement';
  };

  return (
    <div className={`grade-card ${getGradeClass(gradePercent)}`}>
      <div className="grade-card-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="grade-info">
          <h3>{submission.assignment_id}</h3>
          <span className="submission-date">
            Submitted: {formatDate(submission.submitted_at)}
          </span>
        </div>
        <div className="grade-score">
          {submission.grade !== undefined ? (
            <>
              <span className="score">{submission.grade}/{submission.max_grade}</span>
              <span className="percent">({gradePercent?.toFixed(1)}%)</span>
            </>
          ) : (
            <span className="pending-badge">Pending</span>
          )}
        </div>
        <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▼</span>
      </div>

      {isExpanded && (
        <div className="grade-card-details">
          <div className="feedback-section">
            <h4>Feedback</h4>
            {submission.feedback ? (
              <p className="feedback-text">{submission.feedback}</p>
            ) : (
              <p className="no-feedback">No feedback provided yet.</p>
            )}
          </div>
          {submission.graded_at && (
            <div className="graded-info">
              <span>Graded on: {formatDate(submission.graded_at)}</span>
              {submission.graded_by && <span>By: {submission.graded_by}</span>}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Helper function
const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export default Grades;

