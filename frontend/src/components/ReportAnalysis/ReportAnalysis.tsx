import React, { useState, useRef, ChangeEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { analyzeProjectReport, analyzeUploadedReport } from '../../services/api';
import {
  ReportAnalysisRequest,
  ReportAnalysisResponse,
  ReportFileType,
  ReportSection,
  ImprovementSuggestion,
  SectionType
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

  const handleFileUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);

    // For PDF and DOCX files, upload directly to backend for processing
    const fileExtension = file.name.toLowerCase().split('.').pop();
    if (fileExtension === 'pdf' || fileExtension === 'docx' || fileExtension === 'md' || fileExtension === 'markdown') {
      setIsAnalyzing(true);
      setError(null);

      try {
        const resp = await analyzeUploadedReport(file);
        setResult(resp);
        setActiveTab('structure');
      } catch (e) {
        setError(e instanceof Error ? e.message : t('errors.analysisFailed'));
      } finally {
        setIsAnalyzing(false);
      }
      return;
    }

    // For text files, read content in browser
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
    // 根据文件扩展名确定类型
    let fileType: ReportFileType = 'markdown';
    if (fileName.endsWith('.pdf')) {
      fileType = 'pdf';
    } else if (fileName.endsWith('.docx')) {
      fileType = 'docx';
    }
    handleAnalyze(textContent, fileName || 'report.md', fileType);
  };

  // Helper function to get section type label
  const getSectionTypeLabel = (type: SectionType): string => {
    const labels: Record<SectionType, string> = {
      abstract: t('structure.abstract'),
      introduction: t('structure.introduction'),
      related_work: t('structure.relatedWork'),
      method: t('structure.method'),
      results: t('structure.results'),
      discussion: t('structure.discussion'),
      conclusion: t('structure.conclusion'),
      references: t('structure.references'),
      appendix: t('structure.appendix'),
      other: t('structure.other')
    };
    return labels[type] || type;
  };

  // Render structure tab
  const renderStructureTab = () => {
    if (!result) return null;

    return (
      <div className="result-section">
        <h3>📋 {t('structure.title')}</h3>

        <div className="score-display">
          <div className="score-value" style={{ color: result.overall_score >= 70 ? '#28a745' : result.overall_score >= 50 ? '#ffc107' : '#dc3545' }}>
            {Math.round(result.overall_score)}
          </div>
          <div className="score-label">{t('quality.overall')}</div>
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-title">{t('structure.wordCount')}</div>
            <div className="metric-value">{result.quality.total_word_count}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('structure.sections')}</div>
            <div className="metric-value">{result.parsed.sections.length}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('quality.grammar')}</div>
            <div className="metric-value">{Math.round(result.language_quality.academic_tone_score)}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('quality.formatting')}</div>
            <div className="metric-value">{Math.round(result.formatting.title_consistency_score)}</div>
          </div>
        </div>

        <h4>{t('structure.sections')}</h4>
        <div className="section-list">
          {result.parsed.sections.map((section: ReportSection) => (
            <div key={section.id} className="section-item">
              <div className="section-header">
                <div className="section-title">{section.title || t('structure.defaultTitle')}</div>
                <div className="section-type">{getSectionTypeLabel(section.section_type)}</div>
              </div>
              <div className="section-content">
                {section.text.substring(0, 200)}{section.text.length > 200 ? '...' : ''}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render quality tab
  const renderQualityTab = () => {
    if (!result) return null;

    return (
      <div className="result-section">
        <h3>📊 {t('quality.title')}</h3>

        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-title">{t('structure.wordCount')}</div>
            <div className="metric-value">{result.quality.total_word_count}</div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('quality.grammar')}</div>
            <div className="metric-value" style={{ color: result.language_quality.academic_tone_score >= 70 ? '#28a745' : result.language_quality.academic_tone_score >= 50 ? '#ffc107' : '#dc3545' }}>
              {Math.round(result.language_quality.academic_tone_score)}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('quality.formatting')}</div>
            <div className="metric-value" style={{ color: result.formatting.title_consistency_score >= 70 ? '#28a745' : result.formatting.title_consistency_score >= 50 ? '#ffc107' : '#dc3545' }}>
              {Math.round(result.formatting.title_consistency_score)}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('quality.citations')}</div>
            <div className="metric-value">{result.parsed.references.length}</div>
          </div>
        </div>

        <h4>{t('structure.chapterStats')}</h4>
        <div className="section-list">
          {result.quality.chapter_length_stats.map((stat, index) => (
            <div key={index} className="section-item">
              <div className="section-header">
                <div className="section-title">{stat.title}</div>
                <div className="metric-value">{stat.word_count} {t('structure.words')}</div>
              </div>
              <div className="section-content">
                <div>{t('structure.proportion')}: {(stat.proportion * 100).toFixed(1)}%</div>
                <div>{t('structure.evaluation')}: {stat.evaluation}</div>
              </div>
            </div>
          ))}
        </div>

        <h4>{t('quality.figureTableStats')}</h4>
        <div className="section-item">
          <div className="section-content">
            <div>{t('structure.figures')}: {result.quality.figure_table_stats.figure_count}</div>
            <div>{t('structure.tables')}: {result.quality.figure_table_stats.table_count}</div>
            <div>{t('structure.evaluation')}: {result.quality.figure_table_stats.evaluation}</div>
          </div>
        </div>
      </div>
    );
  };

  // Render logic tab
  const renderLogicTab = () => {
    if (!result) return null;

    return (
      <div className="result-section">
        <h3>💡 {t('logic.title')}</h3>

        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-title">{t('logic.sectionOrder')}</div>
            <div className="metric-value" style={{ color: result.logic.section_order_score >= 70 ? '#28a745' : result.logic.section_order_score >= 50 ? '#ffc107' : '#dc3545' }}>
              {Math.round(result.logic.section_order_score)}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('logic.coherence')}</div>
            <div className="metric-value" style={{ color: result.logic.coherence_score >= 70 ? '#28a745' : result.logic.coherence_score >= 50 ? '#ffc107' : '#dc3545' }}>
              {Math.round(result.logic.coherence_score)}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('logic.argumentation')}</div>
            <div className="metric-value" style={{ color: result.logic.argumentation_score >= 70 ? '#28a745' : result.logic.argumentation_score >= 50 ? '#ffc107' : '#dc3545' }}>
              {Math.round(result.logic.argumentation_score)}
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-title">{t('logic.innovation')}</div>
            <div className="metric-value" style={{ color: result.innovation.novelty_score >= 70 ? '#28a745' : result.innovation.novelty_score >= 50 ? '#ffc107' : '#dc3545' }}>
              {Math.round(result.innovation.novelty_score)}
            </div>
          </div>
        </div>

        <h4>{t('logic.summary')}</h4>
        <div className="section-item">
          <div className="section-content">{result.logic.summary}</div>
        </div>

        <h4>{t('logic.issues')}</h4>
        <div className="section-list">
          {result.logic.issues.length > 0 ? (
            result.logic.issues.map((issue, index) => (
              <div key={index} className="section-item">
                <div className="section-header">
                  <div className="section-title">{issue.issue_type.replace('_', ' ')}</div>
                </div>
                <div className="section-content">
                  <div><strong>{t('logic.description')}:</strong> {issue.description}</div>
                  {issue.suggested_fix && <div><strong>{t('logic.suggestedFix')}:</strong> {issue.suggested_fix}</div>}
                </div>
              </div>
            ))
          ) : (
            <div className="section-item">
              <div className="section-content">{t('logic.noIssues')}</div>
            </div>
          )}
        </div>

        <h4>{t('logic.innovationPoints')}</h4>
        <div className="section-list">
          {result.innovation.innovation_points.length > 0 ? (
            result.innovation.innovation_points.map((point, index) => (
              <div key={index} className="section-item">
                <div className="section-content">
                  <div><strong>{t('logic.highlight')}:</strong> {point.highlight_text}</div>
                  <div><strong>{t('logic.reason')}:</strong> {point.reason}</div>
                </div>
              </div>
            ))
          ) : (
            <div className="section-item">
              <div className="section-content">{t('logic.noInnovation')}</div>
            </div>
          )}
        </div>
      </div>
    );
  };

  // Render suggestions tab
  const renderSuggestionsTab = () => {
    if (!result) return null;

    return (
      <div className="result-section">
        <h3>✏️ {t('suggestions.title')}</h3>

        {result.suggestions.length > 0 ? (
          <div className="suggestions-list">
            {result.suggestions.map((suggestion: ImprovementSuggestion, index) => (
              <div key={index} className="suggestion-item">
                <div className="suggestion-category">{suggestion.category}</div>
                <div className="suggestion-summary">{suggestion.summary}</div>
                <div className="suggestion-details">{suggestion.details}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="section-item">
            <div className="section-content">{t('suggestions.empty')}</div>
          </div>
        )}
      </div>
    );
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
                accept=".txt,.md,.markdown,.pdf,.docx"
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

        {activeTab === 'structure' && result && renderStructureTab()}
        {activeTab === 'quality' && result && renderQualityTab()}
        {activeTab === 'logic' && result && renderLogicTab()}
        {activeTab === 'suggestions' && result && renderSuggestionsTab()}
      </div>
    </div>
  );
};

export default ReportAnalysis;
