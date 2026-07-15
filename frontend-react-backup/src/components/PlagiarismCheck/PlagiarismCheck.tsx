import React, { useState, useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import BatchUpload from './BatchUpload';
import SimilarityMatrix from './SimilarityMatrix';
import RelationshipGraph from './RelationshipGraph';
import SuspiciousList from './SuspiciousList';
import OriginalityReport from './OriginalityReport';
import { batchAnalyzePlagiarism } from '../../services/api';
import {
  UploadedFile,
  BatchAnalysisResponse,
  SubmissionData,
  SimilarityMatrixEntry,
  SubmissionComparison,
  OriginalityReport as OriginalityReportType,
} from '../../types/plagiarism';
import './PlagiarismCheck.css';

type TabType = 'upload' | 'matrix' | 'graph' | 'list' | 'reports';

const PlagiarismCheck: React.FC = () => {
  const { t } = useTranslation('plagiarism');
  const [activeTab, setActiveTab] = useState<TabType>('upload');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<BatchAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [threshold, setThreshold] = useState(0.7);

  const handleFilesReady = useCallback(async (files: UploadedFile[]) => {
    setIsAnalyzing(true);
    setError(null);

    try {
      const submissions: SubmissionData[] = files.map(f => ({
        student_id: f.studentId,
        student_name: f.studentName,
        code: f.code,
      }));

      const result = await batchAnalyzePlagiarism({
        assignment_id: `batch_${Date.now()}`,
        submissions,
        similarity_threshold: threshold,
        algorithms: ['combined'],
        generate_reports: true,
      });

      setAnalysisResult(result);
      setActiveTab('matrix');
    } catch (err) {
      setError(err instanceof Error ? err.message : t('errors.analysisFailed'));
    } finally {
      setIsAnalyzing(false);
    }
  }, [threshold, t]);

  const handleCellClick = (entry: SimilarityMatrixEntry) => {
    console.log('Cell clicked:', entry);
    setActiveTab('list');
  };

  const handlePairClick = (pair: SubmissionComparison) => {
    console.log('Pair clicked:', pair);
  };

  const handleReportClick = (report: OriginalityReportType) => {
    console.log('Report clicked:', report);
  };

  const tabs = [
    { id: 'upload' as TabType, label: `📤 ${t('upload.title')}`, icon: '📤' },
    { id: 'matrix' as TabType, label: `📊 ${t('matrix.title')}`, icon: '📊', disabled: !analysisResult },
    { id: 'graph' as TabType, label: `🔗 ${t('graph.title')}`, icon: '🔗', disabled: !analysisResult },
    { id: 'list' as TabType, label: `⚠️ ${t('suspicious.title')}`, icon: '⚠️', disabled: !analysisResult },
    { id: 'reports' as TabType, label: `📋 ${t('report.title')}`, icon: '📋', disabled: !analysisResult },
  ];

  return (
    <div className="plagiarism-check">
      <div className="page-header">
        <h1>{`🔍 ${t('title')}`}</h1>
        <p>{t('subtitle')}</p>
      </div>

      {/* 设置栏 */}
      <div className="settings-bar">
        <div className="setting-item">
          <label>{t('settings.threshold')}：</label>
          <input
            type="range"
            min="0.3"
            max="0.95"
            step="0.05"
            value={threshold}
            onChange={(e) => setThreshold(parseFloat(e.target.value))}
          />
          <span className="threshold-value">{(threshold * 100).toFixed(0)}%</span>
        </div>
        {analysisResult && (
          <div className="result-summary">
            <span>{t('results.analyzed', { count: analysisResult.total_submissions })}</span>
            <span className="flagged">{t('results.flagged', { count: analysisResult.flagged_count })}</span>
          </div>
        )}
      </div>

      {/* 标签页导航 */}
      <div className="tab-nav">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''} ${tab.disabled ? 'disabled' : ''}`}
            onClick={() => !tab.disabled && setActiveTab(tab.id)}
            disabled={tab.disabled}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="error-message">
          <span>{`❌ ${error}`}</span>
          <button onClick={() => setError(null)}>{t('common.close')}</button>
        </div>
      )}

      {/* 内容区域 */}
      <div className="tab-content">
        {activeTab === 'upload' && (
          <BatchUpload onFilesReady={handleFilesReady} isAnalyzing={isAnalyzing} />
        )}
        {activeTab === 'matrix' && analysisResult && (
          <SimilarityMatrix data={analysisResult.similarity_matrix} onCellClick={handleCellClick} />
        )}
        {activeTab === 'graph' && analysisResult && (
          <RelationshipGraph
            matrix={analysisResult.similarity_matrix}
            suspiciousPairs={analysisResult.suspicious_pairs}
          />
        )}
        {activeTab === 'list' && analysisResult && (
          <SuspiciousList
            pairs={analysisResult.suspicious_pairs}
            matrix={analysisResult.similarity_matrix}
            onPairClick={handlePairClick}
          />
        )}
        {activeTab === 'reports' && analysisResult && (
          <OriginalityReport
            reports={analysisResult.originality_reports}
            onReportClick={handleReportClick}
          />
        )}
      </div>
    </div>
  );
};

export default PlagiarismCheck;

