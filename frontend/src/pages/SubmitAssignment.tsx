import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { LoadingSpinner, ErrorMessage, ConfirmDialog } from '../components/common';
import { getAssignment, createSubmission, getAssignmentRubric } from '../services/api';
import { Assignment, Rubric } from '../types';
import { useToast } from '../contexts/ToastContext';
import './SubmitAssignment.css';

// Language detection based on file extension
const getLanguageFromExtension = (filename: string): string => {
  const ext = filename.split('.').pop()?.toLowerCase() || '';
  const languageMap: Record<string, string> = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'jsx': 'javascript',
    'tsx': 'typescript',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'c',
    'cs': 'csharp',
    'go': 'go',
    'rs': 'rust',
    'rb': 'ruby',
    'php': 'php',
    'html': 'html',
    'css': 'css',
    'json': 'json',
    'xml': 'xml',
    'sql': 'sql',
    'md': 'markdown',
    'txt': 'plaintext',
  };
  return languageMap[ext] || 'plaintext';
};

const SubmitAssignment: React.FC = () => {
  const { assignmentId } = useParams<{ assignmentId: string }>();
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { showSuccess, showError, showWarning, showInfo } = useToast();

  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [rubric, setRubric] = useState<Rubric | null>(null);
  const [content, setContent] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [editorLanguage, setEditorLanguage] = useState('python');
  const [showPreview, setShowPreview] = useState(false);
  const [draftSaved, setDraftSaved] = useState(false);
  const [showRubric, setShowRubric] = useState(false);

  // Dialog states
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);

  // Auto-save draft to localStorage
  const saveDraft = useCallback(() => {
    if (assignmentId && content) {
      localStorage.setItem(`draft_${assignmentId}`, content);
      setDraftSaved(true);
      setTimeout(() => setDraftSaved(false), 2000);
    }
  }, [assignmentId, content]);

  // Keyboard shortcut for saving draft (Ctrl+S)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        saveDraft();
        showInfo('Draft saved');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [saveDraft, showInfo]);

  // Auto-save every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (content.trim()) {
        saveDraft();
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [content, saveDraft]);

  // Load draft from localStorage on mount
  useEffect(() => {
    if (assignmentId) {
      const savedDraft = localStorage.getItem(`draft_${assignmentId}`);
      if (savedDraft) {
        setContent(savedDraft);
        showInfo('Draft restored from previous session');
      }
    }
  }, [assignmentId, showInfo]);

  useEffect(() => {
    const fetchAssignment = async () => {
      if (!assignmentId) return;

      try {
        setIsLoading(true);
        setError(null);
        const data = await getAssignment(assignmentId);
        setAssignment(data);

        // Try to fetch rubric if available
        if (data.rubric_id) {
          try {
            const rubricData = await getAssignmentRubric(assignmentId);
            setRubric(rubricData);
          } catch {
            // Rubric not available, that's okay
          }
        }
      } catch (err) {
        setError('Failed to load assignment details.');
        console.error('Assignment fetch error:', err);
        showError('Failed to load assignment details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchAssignment();
  }, [assignmentId, showError]);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setSubmitError('File size must be less than 10MB');
        showError('File size must be less than 10MB');
        return;
      }

      // Detect language from file extension
      const detectedLanguage = getLanguageFromExtension(selectedFile.name);
      setEditorLanguage(detectedLanguage);

      // Read file content and populate editor
      try {
        const text = await selectedFile.text();
        setContent(text);
        showSuccess(`File "${selectedFile.name}" loaded into editor`);
      } catch {
        // If we can't read as text, just store the file
        showInfo('File uploaded (binary file)');
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
    showInfo('File removed');
  };

  const handleEditorChange = (value: string | undefined) => {
    setContent(value || '');
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setEditorLanguage(e.target.value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!assignmentId) return;

    if (!content.trim() && !file) {
      setSubmitError('Please provide code or upload a file');
      showWarning('Please provide code or upload a file');
      return;
    }

    // Show confirmation dialog
    setShowSubmitDialog(true);
  };

  const confirmSubmit = async () => {
    setShowSubmitDialog(false);

    if (!assignmentId) return;

    try {
      setIsSubmitting(true);
      setSubmitError(null);

      await createSubmission({
        assignment_id: assignmentId,
        content: content.trim(),
        file: file || undefined,
      });

      // Clear draft after successful submission
      localStorage.removeItem(`draft_${assignmentId}`);

      showSuccess('Assignment submitted successfully!');

      // Navigate to success page or dashboard
      navigate('/student-dashboard', {
        state: { message: 'Assignment submitted successfully!' }
      });
    } catch (err) {
      setSubmitError('Failed to submit assignment. Please try again.');
      showError('Failed to submit assignment. Please try again.');
      console.error('Submission error:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClearDraft = () => {
    setShowClearDialog(true);
  };

  const confirmClearDraft = () => {
    setShowClearDialog(false);
    setContent('');
    if (assignmentId) {
      localStorage.removeItem(`draft_${assignmentId}`);
    }
    showInfo('Draft cleared');
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
        {draftSaved && <span className="draft-saved-indicator">✓ Draft saved</span>}
      </div>

      {/* Assignment Details */}
      <div className="assignment-details">
        <div className="assignment-header-row">
          <h2>{assignment.title}</h2>
          {rubric && (
            <button
              type="button"
              className="view-rubric-btn"
              onClick={() => setShowRubric(!showRubric)}
            >
              {showRubric ? 'Hide Rubric' : 'View Rubric'}
            </button>
          )}
        </div>
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

        {/* Rubric Display */}
        {showRubric && rubric && (
          <div className="rubric-section">
            <h3>Grading Rubric: {rubric.name}</h3>
            <p className="rubric-description">{rubric.description}</p>
            <div className="rubric-criteria">
              {rubric.criteria.map((criterion) => (
                <div key={criterion.id} className="criterion-card">
                  <div className="criterion-header">
                    <span className="criterion-name">{criterion.name}</span>
                    <span className="criterion-points">{criterion.max_points} pts</span>
                  </div>
                  <p className="criterion-description">{criterion.description}</p>
                  <div className="criterion-levels">
                    {criterion.levels.map((level, idx) => (
                      <div key={idx} className="level-item">
                        <span className="level-points">{level.points} pts:</span>
                        <span className="level-description">{level.description}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
            <div className="rubric-total">Total Points: {rubric.total_points}</div>
          </div>
        )}
      </div>

      {/* Submission Form */}
      <form className="submission-form" onSubmit={handleSubmit}>
        {submitError && <ErrorMessage message={submitError} />}

        {isOverdue && !assignment.allow_late_submission && (
          <div className="warning-banner" role="alert" id="overdue-warning">
            ⚠️ This assignment is past due and late submissions are not allowed.
          </div>
        )}

        {isOverdue && assignment.allow_late_submission && (
          <div className="info-banner" role="status">
            ℹ️ This is a late submission. A {assignment.late_penalty_percent || 0}% penalty may apply.
          </div>
        )}

        {/* Code Editor with Monaco */}
        <div className="form-section" role="group" aria-labelledby="code-editor-label">
          <div className="editor-header">
            <label id="code-editor-label" htmlFor="code-content">Your Code / Answer</label>
            <div className="editor-controls">
              <select
                id="language-select"
                value={editorLanguage}
                onChange={handleLanguageChange}
                className="language-select"
                aria-label="Select programming language"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="cpp">C++</option>
                <option value="c">C</option>
                <option value="csharp">C#</option>
                <option value="go">Go</option>
                <option value="rust">Rust</option>
                <option value="plaintext">Plain Text</option>
              </select>
              <button
                type="button"
                className="preview-btn"
                onClick={() => setShowPreview(!showPreview)}
                aria-pressed={showPreview}
                aria-label={showPreview ? 'Switch to edit mode' : 'Preview code'}
              >
                {showPreview ? 'Edit' : 'Preview'}
              </button>
              <button
                type="button"
                className="clear-btn"
                onClick={handleClearDraft}
                disabled={!content.trim()}
                aria-label="Clear draft content"
              >
                Clear
              </button>
            </div>
          </div>

          {showPreview ? (
            <div className="code-preview">
              <pre><code>{content || 'No content to preview'}</code></pre>
            </div>
          ) : (
            <div className="monaco-editor-container">
              <Editor
                height="400px"
                language={editorLanguage}
                value={content}
                onChange={handleEditorChange}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                  lineNumbers: 'on',
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 4,
                  wordWrap: 'on',
                  readOnly: isSubmitting,
                }}
                loading={<LoadingSpinner message="Loading editor..." />}
              />
            </div>
          )}
          <div className="editor-footer">
            <span className="char-count">{content.length} characters</span>
            <span className="line-count">{content.split('\n').length} lines</span>
            <span className="shortcut-hint">Ctrl+S to save draft</span>
          </div>
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
                  aria-label="Remove file"
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
                  accept=".py,.js,.ts,.jsx,.tsx,.java,.cpp,.c,.cs,.go,.rs,.rb,.php,.txt,.pdf,.zip"
                  aria-label="Upload file"
                />
                <label htmlFor="file-upload" className="upload-label">
                  <span className="upload-icon">📁</span>
                  <span>Click to upload or drag and drop</span>
                  <span className="upload-hint">Max 10MB • Supports code files, PDF, and ZIP</span>
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
            type="button"
            className="save-draft-btn"
            onClick={saveDraft}
            disabled={!content.trim()}
          >
            Save Draft
          </button>
          <button
            type="submit"
            className="submit-btn"
            disabled={isSubmitting || (isOverdue && !assignment.allow_late_submission)}
            aria-describedby={isOverdue && !assignment.allow_late_submission ? 'overdue-warning' : undefined}
          >
            {isSubmitting ? <LoadingSpinner size="small" message="" /> : 'Submit Assignment'}
          </button>
        </div>
      </form>

      {/* Confirmation Dialogs */}
      <ConfirmDialog
        isOpen={showClearDialog}
        title="Clear Draft"
        message="Are you sure you want to clear your draft? This action cannot be undone."
        confirmText="Clear"
        cancelText="Keep Draft"
        variant="warning"
        onConfirm={confirmClearDraft}
        onCancel={() => setShowClearDialog(false)}
      />

      <ConfirmDialog
        isOpen={showSubmitDialog}
        title="Submit Assignment"
        message="Are you sure you want to submit this assignment? This action cannot be undone."
        confirmText="Submit"
        cancelText="Review Again"
        variant="default"
        onConfirm={confirmSubmit}
        onCancel={() => setShowSubmitDialog(false)}
      />
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

