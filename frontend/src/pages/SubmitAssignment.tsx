import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import { getAssignment, createSubmission } from '../services/api';
import { Assignment } from '../types';
import './SubmitAssignment.css';

const SubmitAssignment: React.FC = () => {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [content, setContent] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAssignment = async () => {
      if (!assignmentId) return;
      
      try {
        setIsLoading(true);
        setError(null);
        const data = await getAssignment(assignmentId);
        setAssignment(data);
      } catch (err) {
        setError('Failed to load assignment details.');
        console.error('Assignment fetch error:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchAssignment();
  }, [assignmentId]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setSubmitError('File size must be less than 10MB');
        return;
      }
      setFile(selectedFile);
      setSubmitError(null);
    }
  };

  const handleRemoveFile = () => {
    setFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!assignmentId) return;
    
    if (!content.trim() && !file) {
      setSubmitError('Please provide code or upload a file');
      return;
    }

    try {
      setIsSubmitting(true);
      setSubmitError(null);
      
      await createSubmission({
        assignment_id: assignmentId,
        content: content.trim(),
        file: file || undefined,
      });
      
      // Navigate to success page or dashboard
      navigate('/student-dashboard', { 
        state: { message: 'Assignment submitted successfully!' } 
      });
    } catch (err) {
      setSubmitError('Failed to submit assignment. Please try again.');
      console.error('Submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="submit-assignment-loading">
        <LoadingSpinner message="Loading assignment..." />
      </div>
    );
  }

  if (error || !assignment) {
    return (
      <div className="submit-assignment-error">
        <ErrorMessage message={error || 'Assignment not found'} />
        <Link to="/student-dashboard" className="back-link">
          ← Back to Dashboard
        </Link>
      </div>
    );
  }

  const isOverdue = new Date(assignment.due_date) < new Date();

  return (
    <div className="submit-assignment">
      <div className="submit-header">
        <Link to="/student-dashboard" className="back-link">
          ← Back to Dashboard
        </Link>
        <h1>Submit Assignment</h1>
      </div>

      {/* Assignment Details */}
      <div className="assignment-details">
        <h2>{assignment.title}</h2>
        <div className="assignment-meta-info">
          <span className="assignment-type">{assignment.assignment_type}</span>
          <span className={`due-date ${isOverdue ? 'overdue' : ''}`}>
            Due: {formatDate(assignment.due_date)}
            {isOverdue && ' (Overdue)'}
          </span>
          <span className="max-score">Max Score: {assignment.max_score}</span>
        </div>
        <div className="assignment-description">
          <h3>Instructions</h3>
          <p>{assignment.instructions || assignment.description}</p>
        </div>
      </div>

      {/* Submission Form */}
      <form className="submission-form" onSubmit={handleSubmit}>
        {submitError && <ErrorMessage message={submitError} />}
        
        {isOverdue && !assignment.allow_late_submission && (
          <div className="warning-banner">
            ⚠️ This assignment is past due and late submissions are not allowed.
          </div>
        )}

        {isOverdue && assignment.allow_late_submission && (
          <div className="info-banner">
            ℹ️ This is a late submission. A {assignment.late_penalty_percent || 0}% penalty may apply.
          </div>
        )}

        {/* Code Editor */}
        <div className="form-section">
          <label htmlFor="code-content">Your Code / Answer</label>
          <textarea
            id="code-content"
            className="code-editor"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste your code or write your answer here..."
            rows={15}
            disabled={isSubmitting}
          />
        </div>

        {/* File Upload */}
        <div className="form-section">
          <label>Upload File (Optional)</label>
          <div className="file-upload-area">
            {file ? (
              <div className="selected-file">
                <span className="file-icon">📄</span>
                <span className="file-name">{file.name}</span>
                <span className="file-size">({formatFileSize(file.size)})</span>
                <button
                  type="button"
                  className="remove-file-btn"
                  onClick={handleRemoveFile}
                  disabled={isSubmitting}
                >
                  ✕
                </button>
              </div>
            ) : (
              <div className="upload-prompt">
                <input
                  ref={fileInputRef}
                  type="file"
                  id="file-upload"
                  onChange={handleFileChange}
                  disabled={isSubmitting}
                  accept=".py,.js,.ts,.java,.cpp,.c,.txt,.pdf,.zip"
                />
                <label htmlFor="file-upload" className="upload-label">
                  <span className="upload-icon">📁</span>
                  <span>Click to upload or drag and drop</span>
                  <span className="upload-hint">Max 10MB • .py, .js, .ts, .java, .cpp, .c, .txt, .pdf, .zip</span>
                </label>
              </div>
            )}
          </div>
        </div>

        {/* Submit Button */}
        <div className="form-actions">
          <Link to="/student-dashboard" className="cancel-btn">
            Cancel
          </Link>
          <button
            type="submit"
            className="submit-btn"
            disabled={isSubmitting || (isOverdue && !assignment.allow_late_submission)}
          >
            {isSubmitting ? <LoadingSpinner size="small" message="" /> : 'Submit Assignment'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Helper functions
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

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

export default SubmitAssignment;

