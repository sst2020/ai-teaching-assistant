import React, { useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { analyzeProjectReport } from '../../services/api';
import {
  ReportAnalysisRequest,
  ReportAnalysisResponse,
  ReportFileType,
} from '../../types/reportAnalysis';
import './ReportAnalysis.css';

type TabType = 'upload' | 'structure' | 'quality' | 'logic' | 'suggestions';

const ReportAnalysis: React.FC = () => {
  const { t } = useTranslation('report');
  const [activeTab, setActiveTab] = useState<TabType>('upload');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<ReportAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [textContent, setTextContent] = useState('');
  const [fileName, setFileName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAnalyze = async (content: string, name: string, fileType: ReportFileType) => {
    setIsAnalyzing(true);
    setError(null);
    try {
      const request: ReportAnalysisRequest = {
        file_name: name,
        file_type: fileType,
        content,
      };
      const resp = await analyzeProjectReport(request);
      setResult(resp);
      setActiveTab('structure');
    } catch (e) {
      setError(e instanceof Error ? e.message : t('errors.analysisFailed'));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      setTextContent(content);
    };
    reader.readAsText(file);
  };

  const handleSubmit = () => {
    if (!textContent.trim()) {
      setError(t('errors.noContent'));
      return;
    }
    // 根据文件扩展名确定类型，默认为 markdown
    let fileType: ReportFileType = 'markdown';
    if (fileName.endsWith('.pdf')) {
      fileType = 'pdf';
    } else if (fileName.endsWith('.docx')) {
      fileType = 'docx';
    }
    handleAnalyze(textContent, fileName || 'report.md', fileType);
  };

  return (
    <div className="report-analysis">
      <div className="page-header">
        <h1>📑 {t('title')}</h1>
        <p>{t('subtitle')}</p>
      </div>

      <div className="tab-nav">
        <button
          className={`tab-btn ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          {t('tabs.upload')}
        </button>
        <button
          className={`tab-btn ${activeTab === 'structure' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('structure')}
        >
          {t('tabs.structure')}
        </button>
        <button
          className={`tab-btn ${activeTab === 'quality' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('quality')}
        >
          {t('tabs.quality')}
        </button>
        <button
          className={`tab-btn ${activeTab === 'logic' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('logic')}
        >
          {t('tabs.logic')}
        </button>
        <button
          className={`tab-btn ${activeTab === 'suggestions' ? 'active' : ''} ${!result ? 'disabled' : ''}`}
          disabled={!result}
          onClick={() => result && setActiveTab('suggestions')}
        >
          {t('tabs.suggestions')}
        </button>
      </div>

      {error && (
        <div className="error-message">
          <span>❌ {error}</span>
          <button onClick={() => setError(null)}>{t('common.close')}</button>
        </div>
      )}

      <div className="tab-content">
        {activeTab === 'upload' && (
          <div className="upload-section">
            <div className="upload-area">
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileUpload}
                accept=".txt,.md,.markdown"
                style={{ display: 'none' }}
              />
              <button
                className="upload-btn"
                onClick={() => fileInputRef.current?.click()}
                disabled={isAnalyzing}
              >
                📁 {t('upload.selectFile')}
              </button>
              {fileName && <span className="file-name">{fileName}</span>}
            </div>
            <div className="text-input-area">
              <textarea
                placeholder={t('upload.pasteContent')}
                value={textContent}
                onChange={(e) => setTextContent(e.target.value)}
                disabled={isAnalyzing}
                rows={10}
              />
            </div>
            <button
              className="analyze-btn"
              onClick={handleSubmit}
              disabled={isAnalyzing || !textContent.trim()}
            >
              {isAnalyzing ? `⏳ ${t('analysis.analyzing')}` : `🔍 ${t('analysis.startAnalysis')}`}
            </button>
          </div>
        )}

        {activeTab === 'structure' && result && (
          <div className="result-section">
            <h3>📋 {t('structure.title')}</h3>
            <pre>{JSON.stringify(result.parsed, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'quality' && result && (
          <div className="result-section">
            <h3>📊 {t('quality.title')}</h3>
            <pre>{JSON.stringify(result.quality, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'logic' && result && (
          <div className="result-section">
            <h3>💡 {t('logic.title')}</h3>
            <pre>{JSON.stringify({ logic: result.logic, innovation: result.innovation }, null, 2)}</pre>
          </div>
        )}

        {activeTab === 'suggestions' && result && (
          <div className="result-section">
            <h3>✏️ {t('suggestions.title')}</h3>
            <pre>{JSON.stringify(result.suggestions, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportAnalysis;
