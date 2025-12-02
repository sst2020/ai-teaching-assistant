import React, { useState } from 'react';
import { OriginalityReport as OriginalityReportType } from '../../types/plagiarism';

interface OriginalityReportProps {
  reports: OriginalityReportType[];
  onReportClick?: (report: OriginalityReportType) => void;
}

const OriginalityReportComponent: React.FC<OriginalityReportProps> = ({ reports, onReportClick }) => {
  const [selectedReport, setSelectedReport] = useState<OriginalityReportType | null>(null);
  const [sortBy, setSortBy] = useState<'score' | 'name'>('score');

  const getScoreColor = (score: number): string => {
    if (score >= 80) return '#22c55e';
    if (score >= 60) return '#84cc16';
    if (score >= 40) return '#eab308';
    if (score >= 20) return '#f97316';
    return '#dc2626';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= 80) return '优秀';
    if (score >= 60) return '良好';
    if (score >= 40) return '一般';
    if (score >= 20) return '较低';
    return '很低';
  };

  const getRiskBadge = (level: string): { label: string; className: string } => {
    const mapping: Record<string, { label: string; className: string }> = {
      'none': { label: '无风险', className: 'risk-none' },
      'low': { label: '低风险', className: 'risk-low' },
      'medium': { label: '中风险', className: 'risk-medium' },
      'high': { label: '高风险', className: 'risk-high' },
      'very_high': { label: '极高风险', className: 'risk-very-high' },
    };
    return mapping[level] || { label: level, className: 'risk-unknown' };
  };

  const sortedReports = [...reports].sort((a, b) => {
    if (sortBy === 'score') {
      return a.originality_score - b.originality_score;
    }
    return a.student_name.localeCompare(b.student_name);
  });

  const handleReportClick = (report: OriginalityReportType) => {
    setSelectedReport(report);
    onReportClick?.(report);
  };

  return (
    <div className="originality-reports">
      <div className="reports-header">
        <h3>📋 原创性分析报告</h3>
        <div className="sort-controls">
          <span>排序：</span>
          <button 
            className={sortBy === 'score' ? 'active' : ''} 
            onClick={() => setSortBy('score')}
          >
            按评分
          </button>
          <button 
            className={sortBy === 'name' ? 'active' : ''} 
            onClick={() => setSortBy('name')}
          >
            按姓名
          </button>
        </div>
      </div>

      <div className="reports-grid">
        {sortedReports.map((report) => {
          const risk = getRiskBadge(report.risk_level);
          return (
            <div
              key={report.report_id}
              className={`report-card ${selectedReport?.report_id === report.report_id ? 'selected' : ''}`}
              onClick={() => handleReportClick(report)}
            >
              <div className="card-header">
                <span className="student-name">{report.student_name}</span>
                <span className={`risk-badge ${risk.className}`}>{risk.label}</span>
              </div>
              
              <div className="score-circle" style={{ 
                background: `conic-gradient(${getScoreColor(report.originality_score)} ${report.originality_score}%, #e5e7eb ${report.originality_score}%)`
              }}>
                <div className="score-inner">
                  <span className="score-value">{report.originality_score.toFixed(0)}</span>
                  <span className="score-label">{getScoreLabel(report.originality_score)}</span>
                </div>
              </div>

              <div className="card-stats">
                <div className="stat">
                  <span className="stat-label">相似作业</span>
                  <span className="stat-value">{report.similar_submissions.length}</span>
                </div>
                <div className="stat">
                  <span className="stat-label">匹配段落</span>
                  <span className="stat-value">{report.detailed_matches.length}</span>
                </div>
              </div>

              <p className="card-summary">{report.summary}</p>
            </div>
          );
        })}
      </div>

      {/* 详细报告弹窗 */}
      {selectedReport && (
        <div className="report-detail-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h4>{selectedReport.student_name} 的原创性报告</h4>
              <button className="close-btn" onClick={() => setSelectedReport(null)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="detail-section">
                <h5>📊 评分详情</h5>
                <div className="score-breakdown">
                  {Object.entries(selectedReport.similarity_breakdown).map(([algo, score]) => (
                    <div key={algo} className="breakdown-item">
                      <span className="algo-name">{algo}</span>
                      <div className="algo-bar">
                        <div className="bar-fill" style={{ width: `${score * 100}%` }}></div>
                      </div>
                      <span className="algo-score">{(score * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>

              {selectedReport.detected_transformations.length > 0 && (
                <div className="detail-section">
                  <h5>🔄 检测到的代码变换</h5>
                  <div className="transformations">
                    {selectedReport.detected_transformations.map((t, i) => (
                      <span key={i} className="transformation-tag">{t}</span>
                    ))}
                  </div>
                </div>
              )}

              <div className="detail-section">
                <h5>💡 改进建议</h5>
                <ul className="suggestions">
                  {selectedReport.improvement_suggestions.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OriginalityReportComponent;

