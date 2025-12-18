import React, { useState, useEffect } from 'react';
import { getHealthStatus, getApiInfo, handleApiError } from '../../services/api';
import { HealthResponse, ApiInfo } from '../../types/api';
import { LoadingSpinner, ErrorMessage } from '../common';
import './Dashboard.css';

// 获取后端 API 基础 URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [healthData, infoData] = await Promise.all([
        getHealthStatus(),
        getApiInfo(),
      ]);
      setHealth(healthData);
      setApiInfo(infoData);
    } catch (err) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="dashboard">
        <LoadingSpinner message="Loading dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard">
        <ErrorMessage message={error} onRetry={fetchData} />
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>🏠 Dashboard</h2>
        <p>Welcome to the AI Teaching Assistant</p>
      </div>

      <div className="dashboard-grid">
        <div className="status-card">
          <div className="card-header">
            <span className="card-icon">🔌</span>
            <h3>Backend Status</h3>
          </div>
          <div className="card-content">
            <div className={`status-badge ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
              {health?.status || 'Unknown'}
            </div>
            <div className="status-details">
              <p><strong>Version:</strong> {health?.version || 'N/A'}</p>
              <p><strong>Last Check:</strong> {health?.timestamp ? new Date(health.timestamp).toLocaleString() : 'N/A'}</p>
            </div>
          </div>
        </div>

        <div className="info-card">
          <div className="card-header">
            <span className="card-icon">ℹ️</span>
            <h3>API Information</h3>
          </div>
          <div className="card-content">
            <p><strong>Name:</strong> {apiInfo?.name || 'N/A'}</p>
            <p><strong>Version:</strong> {apiInfo?.version || 'N/A'}</p>
            <p><strong>Description:</strong> {apiInfo?.description || 'N/A'}</p>
            {apiInfo?.docs_url && (
              <a href={`${API_BASE_URL}${apiInfo.docs_url}`} target="_blank" rel="noopener noreferrer" className="docs-link">
                📚 View API Documentation
              </a>
            )}
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">📊</span>
            <h3>Code Analysis</h3>
          </div>
          <div className="card-content">
            <p>Analyze Python code for style issues, complexity metrics, and code smells.</p>
            <ul>
              <li>PEP 8 style checking</li>
              <li>Cyclomatic complexity</li>
              <li>Code smell detection</li>
            </ul>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">💬</span>
            <h3>Q&A Assistant</h3>
          </div>
          <div className="card-content">
            <p>Get instant answers to programming questions with AI-powered assistance.</p>
            <ul>
              <li>Natural language queries</li>
              <li>Context-aware responses</li>
              <li>Confidence scoring</li>
            </ul>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">📝</span>
            <h3>Assignment Grading</h3>
          </div>
          <div className="card-content">
            <p>Automated grading with detailed feedback for code and essay submissions.</p>
            <ul>
              <li>Rubric-based grading</li>
              <li>Detailed feedback</li>
              <li>Plagiarism detection</li>
            </ul>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">🔍</span>
            <h3>Plagiarism Detection</h3>
          </div>
          <div className="card-content">
            <p>Detect code similarity using AST-based fingerprinting technology.</p>
            <ul>
              <li>AST fingerprinting</li>
              <li>Similarity scoring</li>
              <li>Match highlighting</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

