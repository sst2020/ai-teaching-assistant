import React, { useState, useEffect, useMemo } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { getSubmissions, getSubmission, getSubmissionStats } from '../services/api';
import { Submission, SubmissionStats, DetailedFeedback } from '../types';
import { useToast } from '../contexts/ToastContext';
import './Grades.css';

// Extended submission type with detailed feedback
interface ExtendedSubmission extends Submission {
  detailed_feedback?: DetailedFeedback[];
  assignment_title?: string;
  course_name?: string;
}

const Grades: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [submissions, setSubmissions] = useState<ExtendedSubmission[]>([]);
  const [stats, setStats] = useState<SubmissionStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'graded' | 'pending'>('all');
  const [sortBy, setSortBy] = useState<'date' | 'grade' | 'assignment'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [selectedSubmission, setSelectedSubmission] = useState<ExtendedSubmission | null>(null);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const { showError } = useToast();

  // Check for submission ID in URL params
  const submissionIdFromUrl = searchParams.get('submission');

  const loadSubmissionDetails = async (submissionId: string) => {
    try {
      setIsLoadingDetails(true);
      const details = await getSubmission(submissionId);
      setSelectedSubmission(details as ExtendedSubmission);
    } catch (err) {
      console.error('Failed to load submission details:', err);
      showError('Failed to load submission details');
    } finally {
      setIsLoadingDetails(false);
    }
  };

  useEffect(() => {
    const fetchGrades = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch submissions and stats in parallel
        const [submissionsResponse, statsResponse] = await Promise.all([
          getSubmissions(),
          getSubmissionStats().catch(() => null)
        ]);

        setSubmissions(submissionsResponse.submissions);
        if (statsResponse) {
          setStats(statsResponse);
        }

        // If there's a submission ID in URL, load its details
        if (submissionIdFromUrl) {
          await loadSubmissionDetails(submissionIdFromUrl);
        }
      } catch (err) {
        setError('Failed to load grades. Please try again.');
        showError('Failed to load grades');
        console.error('Grades fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchGrades();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [submissionIdFromUrl, showError]);

  const handleViewDetails = async (submission: ExtendedSubmission) => {
    setSearchParams({ submission: submission.id });
    await loadSubmissionDetails(submission.id);
  };

  const handleCloseDetails = () => {
    setSearchParams({});
    setSelectedSubmission(null);
  };

  // Filter and sort submissions
  const filteredSubmissions = useMemo(() => {
    let result = submissions.filter(sub => {
      if (filter === 'graded') return sub.grade !== undefined;
      if (filter === 'pending') return sub.grade === undefined;
      return true;
    });

    // Sort
    result.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.submitted_at).getTime() - new Date(b.submitted_at).getTime();
          break;
        case 'grade':
          const gradeA = a.grade ?? -1;
          const gradeB = b.grade ?? -1;
          comparison = gradeA - gradeB;
          break;
        case 'assignment':
          comparison = a.assignment_id.localeCompare(b.assignment_id);
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return result;
  }, [submissions, filter, sortBy, sortOrder]);

  // Calculate grade distribution for chart
  const gradeDistribution = useMemo(() => {
    const distribution = { A: 0, B: 0, C: 0, D: 0, F: 0 };
    submissions.forEach(s => {
      if (s.grade !== undefined) {
        const percent = (s.grade / s.max_grade) * 100;
        if (percent >= 90) distribution.A++;
        else if (percent >= 80) distribution.B++;
        else if (percent >= 70) distribution.C++;
        else if (percent >= 60) distribution.D++;
        else distribution.F++;
      }
    });
    return distribution;
  }, [submissions]);

  const averageGrade = useMemo(() => {
    const graded = submissions.filter(s => s.grade !== undefined);
    if (graded.length === 0) return 0;
    return graded.reduce((acc, s) => acc + (s.grade! / s.max_grade * 100), 0) / graded.length;
  }, [submissions]);

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
          <span className="summary-value">{stats?.total_submissions ?? submissions.length}</span>
          <span className="summary-label">Total Submissions</span>
        </div>
        <div className="summary-card">
          <span className="summary-value">
            {stats?.graded_count ?? submissions.filter(s => s.grade !== undefined).length}
          </span>
          <span className="summary-label">Graded</span>
        </div>
        <div className="summary-card">
          <span className="summary-value">
            {stats?.pending_count ?? submissions.filter(s => s.grade === undefined).length}
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

      {/* Grade Distribution Chart */}
      <div className="grade-distribution-section">
        <h2>Grade Distribution</h2>
        <div className="distribution-chart">
          {Object.entries(gradeDistribution).map(([grade, count]) => (
            <div key={grade} className="distribution-bar-container">
              <span className="grade-label">{grade}</span>
              <div className="distribution-bar-wrapper">
                <div
                  className={`distribution-bar grade-${grade.toLowerCase()}`}
                  style={{
                    width: `${submissions.filter(s => s.grade !== undefined).length > 0
                      ? (count / submissions.filter(s => s.grade !== undefined).length) * 100
                      : 0}%`
                  }}
                />
              </div>
              <span className="count-label">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Filter and Sort Controls */}
      <div className="controls-row">
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

        <div className="sort-controls">
          <label htmlFor="sort-by">Sort by:</label>
          <select
            id="sort-by"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'date' | 'grade' | 'assignment')}
            className="sort-select"
          >
            <option value="date">Date</option>
            <option value="grade">Grade</option>
            <option value="assignment">Assignment</option>
          </select>
          <button
            className="sort-order-btn"
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            aria-label={`Sort ${sortOrder === 'asc' ? 'descending' : 'ascending'}`}
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Grades List */}
      <div className="grades-list">
        {filteredSubmissions.length > 0 ? (
          filteredSubmissions.map(submission => (
            <GradeCard
              key={submission.id}
              submission={submission}
              onViewDetails={() => handleViewDetails(submission)}
            />
          ))
        ) : (
          <div className="empty-state">
            <span className="empty-icon">📝</span>
            <p>No submissions found</p>
          </div>
        )}
      </div>

      {/* Detailed Submission Modal */}
      {selectedSubmission && (
        <div className="submission-modal-overlay" onClick={handleCloseDetails}>
          <div className="submission-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Submission Details</h2>
              <button className="close-modal-btn" onClick={handleCloseDetails}>✕</button>
            </div>

            {isLoadingDetails ? (
              <LoadingSpinner message="Loading details..." />
            ) : (
              <div className="modal-content">
                <div className="detail-section">
                  <h3>Assignment</h3>
                  <p>{selectedSubmission.assignment_title || selectedSubmission.assignment_id}</p>
                </div>

                <div className="detail-section">
                  <h3>Submitted</h3>
                  <p>{formatDate(selectedSubmission.submitted_at)}</p>
                </div>

                <div className="detail-section grade-section">
                  <h3>Grade</h3>
                  {selectedSubmission.grade !== undefined ? (
                    <div className="grade-display">
                      <span className="grade-value">
                        {selectedSubmission.grade}/{selectedSubmission.max_grade}
                      </span>
                      <span className="grade-percent">
                        ({((selectedSubmission.grade / selectedSubmission.max_grade) * 100).toFixed(1)}%)
                      </span>
                      <div className="grade-bar">
                        <div
                          className="grade-bar-fill"
                          style={{ width: `${(selectedSubmission.grade / selectedSubmission.max_grade) * 100}%` }}
                        />
                      </div>
                    </div>
                  ) : (
                    <span className="pending-badge">Pending</span>
                  )}
                </div>

                {/* Detailed Feedback by Category */}
                {selectedSubmission.detailed_feedback && selectedSubmission.detailed_feedback.length > 0 && (
                  <div className="detail-section">
                    <h3>Detailed Feedback</h3>
                    <div className="detailed-feedback-list">
                      {selectedSubmission.detailed_feedback.map((fb, idx) => (
                        <div key={idx} className="feedback-category">
                          <div className="category-header">
                            <span className="category-name">{fb.category}</span>
                            <span className="category-score">{fb.score}/{fb.max_score}</span>
                          </div>
                          <div className="category-bar">
                            <div
                              className="category-bar-fill"
                              style={{ width: `${(fb.score / fb.max_score) * 100}%` }}
                            />
                          </div>
                          <p className="category-comments">{fb.comments}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* General Feedback */}
                <div className="detail-section">
                  <h3>Feedback</h3>
                  {selectedSubmission.feedback ? (
                    <p className="feedback-text">{selectedSubmission.feedback}</p>
                  ) : (
                    <p className="no-feedback">No feedback provided yet.</p>
                  )}
                </div>

                {/* Submission Content Preview */}
                <div className="detail-section">
                  <h3>Your Submission</h3>
                  <div className="code-preview-box">
                    <pre><code>{selectedSubmission.content || 'No content available'}</code></pre>
                  </div>
                </div>

                {selectedSubmission.graded_at && (
                  <div className="detail-section graded-info">
                    <span>Graded on: {formatDate(selectedSubmission.graded_at)}</span>
                    {selectedSubmission.graded_by && <span> by {selectedSubmission.graded_by}</span>}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

interface GradeCardProps {
  submission: ExtendedSubmission;
  onViewDetails: () => void;
}

const GradeCard: React.FC<GradeCardProps> = ({ submission, onViewDetails }) => {
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

  const getGradeLetter = (percent: number | null): string => {
    if (percent === null) return '-';
    if (percent >= 90) return 'A';
    if (percent >= 80) return 'B';
    if (percent >= 70) return 'C';
    if (percent >= 60) return 'D';
    return 'F';
  };

  return (
    <div className={`grade-card ${getGradeClass(gradePercent)}`}>
      <div className="grade-card-header" onClick={() => setIsExpanded(!isExpanded)}>
        <div className="grade-letter-badge">
          {getGradeLetter(gradePercent)}
        </div>
        <div className="grade-info">
          <h3>{submission.assignment_title || submission.assignment_id}</h3>
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

          {/* Quick stats for detailed feedback */}
          {submission.detailed_feedback && submission.detailed_feedback.length > 0 && (
            <div className="quick-feedback-stats">
              {submission.detailed_feedback.map((fb, idx) => (
                <div key={idx} className="quick-stat">
                  <span className="stat-name">{fb.category}</span>
                  <span className="stat-score">{fb.score}/{fb.max_score}</span>
                </div>
              ))}
            </div>
          )}

          {submission.graded_at && (
            <div className="graded-info">
              <span>Graded on: {formatDate(submission.graded_at)}</span>
              {submission.graded_by && <span>By: {submission.graded_by}</span>}
            </div>
          )}

          <button className="view-details-btn" onClick={(e) => { e.stopPropagation(); onViewDetails(); }}>
            View Full Details
          </button>
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

