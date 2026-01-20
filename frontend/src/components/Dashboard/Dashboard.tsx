import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { getHealthStatus, getApiInfo, handleApiError } from '../../services/api';
import { HealthResponse, ApiInfo } from '../../types/api';
import { LoadingSpinner, ErrorMessage } from '../common';
import './Dashboard.css';

// 获取后端 API 基础 URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const Dashboard: React.FC = () => {
  const { t } = useTranslation('dashboard');
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
        <LoadingSpinner message={t('loading')} />
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

  const getStatusText = (status: string | undefined) => {
    if (status === 'healthy') return t('backendStatus.healthy');
    if (status === 'unhealthy') return t('backendStatus.unhealthy');
    return t('backendStatus.unknown');
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>🏠 {t('title')}</h2>
        <p>{t('welcome')}</p>
      </div>

      <div className="dashboard-grid">
        <div className="status-card">
          <div className="card-header">
            <span className="card-icon">🔌</span>
            <h3>{t('backendStatus.title')}</h3>
          </div>
          <div className="card-content">
            <div className={`status-badge ${health?.status === 'healthy' ? 'healthy' : 'unhealthy'}`}>
              {getStatusText(health?.status)}
            </div>
            <div className="status-details">
              <p><strong>{t('backendStatus.version')}:</strong> {health?.version || 'N/A'}</p>
              <p><strong>{t('backendStatus.lastCheck')}:</strong> {health?.timestamp ? new Date(health.timestamp).toLocaleString() : 'N/A'}</p>
            </div>
          </div>
        </div>

        <div className="info-card">
          <div className="card-header">
            <span className="card-icon">ℹ️</span>
            <h3>{t('apiInfo.title')}</h3>
          </div>
          <div className="card-content">
            <p><strong>{t('apiInfo.name')}:</strong> {apiInfo?.name || 'N/A'}</p>
            <p><strong>{t('apiInfo.version')}:</strong> {apiInfo?.version || 'N/A'}</p>
            <p><strong>{t('apiInfo.description')}:</strong> {apiInfo?.description || 'N/A'}</p>
            {apiInfo?.docs_url && (
              <a href={`${API_BASE_URL}${apiInfo.docs_url}`} target="_blank" rel="noopener noreferrer" className="docs-link">
                📚 {t('apiInfo.viewDocs')}
              </a>
            )}
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">📊</span>
            <h3>{t('features.codeAnalysis.title')}</h3>
          </div>
          <div className="card-content">
            <p>{t('features.codeAnalysis.description')}</p>
            <ul>
              {(t('features.codeAnalysis.items', { returnObjects: true }) as string[]).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">💬</span>
            <h3>{t('features.qaAssistant.title')}</h3>
          </div>
          <div className="card-content">
            <p>{t('features.qaAssistant.description')}</p>
            <ul>
              {(t('features.qaAssistant.items', { returnObjects: true }) as string[]).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">📝</span>
            <h3>{t('features.assignmentGrading.title')}</h3>
          </div>
          <div className="card-content">
            <p>{t('features.assignmentGrading.description')}</p>
            <ul>
              {(t('features.assignmentGrading.items', { returnObjects: true }) as string[]).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        </div>

        <div className="feature-card">
          <div className="card-header">
            <span className="card-icon">🔍</span>
            <h3>{t('features.plagiarismDetection.title')}</h3>
          </div>
          <div className="card-content">
            <p>{t('features.plagiarismDetection.description')}</p>
            <ul>
              {(t('features.plagiarismDetection.items', { returnObjects: true }) as string[]).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

