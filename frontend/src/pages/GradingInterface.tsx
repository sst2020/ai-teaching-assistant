/**
 * 评分界面
 *
 * 功能:
 * - 查看作业提交列表
 * - 查看 AI 评分结果
 * - 手动覆盖评分
 * - 评分统计概览
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  getAssignments,
  getGradingByAssignment,
  getGradingStatistics,
  getGradingResult,
  overrideGradingResult,
} from '../services/api';
import { Assignment } from '../types/assignment';
import {
  GradingResultResponse,
  GradingResultWithSubmission,
  GradingStatistics,
  GradingResultOverride,
} from '../types/grading';
import './GradingInterface.css';

const GradingInterface: React.FC = () => {
  const { t, i18n } = useTranslation('grading');
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const assignmentIdParam = searchParams.get('assignment');

  // 状态
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [selectedAssignment, setSelectedAssignment] = useState<string | null>(assignmentIdParam);
  const [gradingResults, setGradingResults] = useState<GradingResultResponse[]>([]);
  const [statistics, setStatistics] = useState<GradingStatistics | null>(null);
  const [selectedGrading, setSelectedGrading] = useState<GradingResultWithSubmission | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // 覆盖评分表单
  const [showOverrideForm, setShowOverrideForm] = useState(false);
  const [overrideScore, setOverrideScore] = useState<number>(0);
  const [overrideReason, setOverrideReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // 加载作业列表
  const loadAssignments = useCallback(async () => {
    try {
      const response = await getAssignments({ page: 1, page_size: 100 });
      setAssignments(response.items || response.assignments || []);
    } catch (err) {
      console.error(t('errors.loadAssignments'), err);
    }
  }, [t]);

  // 加载评分结果
  const loadGradingResults = useCallback(async () => {
    if (!selectedAssignment) return;

    setLoading(true);
    setError(null);
    try {
      const [resultsResponse, statsResponse] = await Promise.all([
        getGradingByAssignment(selectedAssignment, page, 20),
        getGradingStatistics(selectedAssignment),
      ]);

      setGradingResults(resultsResponse.items || []);
      setTotalPages(resultsResponse.total_pages || 1);
      setStatistics(statsResponse);
    } catch (err) {
      setError(t('errors.loadGrading'));
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedAssignment, page, t]);

  // 加载评分详情
  const loadGradingDetails = async (gradingId: number) => {
    setLoadingDetails(true);
    try {
      const details = await getGradingResult(gradingId);
      setSelectedGrading(details);
      setOverrideScore(details.overall_score);
    } catch (err) {
      setError(t('errors.loadDetails'));
      console.error(err);
    } finally {
      setLoadingDetails(false);
    }
  };

  // 提交覆盖评分
  const handleOverrideSubmit = async () => {
    if (!selectedGrading) return;

    setSubmitting(true);
    try {
      const overrideData: GradingResultOverride = {
        overall_score: overrideScore,
        override_reason: overrideReason || undefined,
      };

      await overrideGradingResult(selectedGrading.id, overrideData);

      // 刷新数据
      setShowOverrideForm(false);
      setOverrideReason('');
      loadGradingResults();
      loadGradingDetails(selectedGrading.id);
    } catch (err) {
      setError(t('errors.overrideFailed'));
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  useEffect(() => {
    loadAssignments();
  }, [loadAssignments]);

  useEffect(() => {
    if (selectedAssignment) {
      loadGradingResults();
    }
  }, [selectedAssignment, loadGradingResults]);

  const getScoreColor = (percentage: number) => {
    if (percentage >= 90) return 'excellent';
    if (percentage >= 80) return 'good';
    if (percentage >= 70) return 'average';
    if (percentage >= 60) return 'pass';
    return 'fail';
  };

  const formatDate = (dateStr: string) => {
    const locale = i18n.language === 'zh' ? 'zh-CN' : 'en-US';
    return new Date(dateStr).toLocaleString(locale, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="grading-interface">
      <header className="page-header">
        <div className="header-left">
          <button className="btn-back" onClick={() => navigate('/teacher')}>
            ← {t('back')}
          </button>
          <h1>✏️ {t('title')}</h1>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* 作业选择器 */}
      <div className="assignment-selector">
        <label>{t('selectAssignment')}：</label>
        <select
          value={selectedAssignment || ''}
          onChange={(e) => {
            setSelectedAssignment(e.target.value || null);
            setPage(1);
            setSelectedGrading(null);
          }}
        >
          <option value="">{t('selectPlaceholder')}</option>
          {assignments.map((a) => (
            <option key={a.id} value={a.assignment_id || String(a.id)}>
              {a.title}
            </option>
          ))}
        </select>
      </div>

      {selectedAssignment && (
        <div className="grading-content">
          {/* 统计概览 */}
          {statistics && (
            <section className="statistics-panel">
              <h3>📊 {t('statistics.title')}</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-value">{statistics.total_graded}</span>
                  <span className="stat-label">{t('statistics.graded')}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{statistics.average_score.toFixed(1)}</span>
                  <span className="stat-label">{t('statistics.average')}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{statistics.highest_score}</span>
                  <span className="stat-label">{t('statistics.highest')}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{statistics.lowest_score}</span>
                  <span className="stat-label">{t('statistics.lowest')}</span>
                </div>
              </div>
              <div className="grader-stats">
                <span>🤖 {t('statistics.aiGraded')}: {statistics.ai_graded_count}</span>
                <span>👨‍🏫 {t('statistics.teacherGraded')}: {statistics.teacher_graded_count}</span>
              </div>
              <div className="score-distribution">
                <span className="dist-label">{t('statistics.distribution')}:</span>
                <span className="dist-item excellent">A: {statistics.score_distribution.A}</span>
                <span className="dist-item good">B: {statistics.score_distribution.B}</span>
                <span className="dist-item average">C: {statistics.score_distribution.C}</span>
                <span className="dist-item pass">D: {statistics.score_distribution.D}</span>
                <span className="dist-item fail">F: {statistics.score_distribution.F}</span>
              </div>
            </section>
          )}

          <div className="main-content">
            {/* 评分列表 */}
            <section className="grading-list-panel">
              <h3>📝 {t('list.title')}</h3>
              {loading ? (
                <div className="loading">{t('list.loading')}</div>
              ) : gradingResults.length === 0 ? (
                <div className="empty-state">{t('list.empty')}</div>
              ) : (
                <>
                  <div className="grading-list">
                    {gradingResults.map((result) => (
                      <div
                        key={result.id}
                        className={`grading-item ${selectedGrading?.id === result.id ? 'selected' : ''}`}
                        onClick={() => loadGradingDetails(result.id)}
                      >
                        <div className="item-header">
                          <span className={`score-badge ${getScoreColor(result.percentage_score)}`}>
                            {result.overall_score}/{result.max_score}
                          </span>
                          <span className="grader-badge">
                            {result.graded_by === 'AI' ? '🤖' : '👨‍🏫'}
                          </span>
                        </div>
                        <div className="item-meta">
                          <span>{t('list.submission')} #{result.submission_id}</span>
                          <span>{formatDate(result.graded_at)}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* 分页 */}
                  <div className="pagination">
                    <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                      {t('list.prevPage')}
                    </button>
                    <span>{page} / {totalPages}</span>
                    <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                      {t('list.nextPage')}
                    </button>
                  </div>
                </>
              )}
            </section>

            {/* 评分详情 */}
            <section className="grading-detail-panel">
              {loadingDetails ? (
                <div className="loading">{t('detail.loading')}</div>
              ) : selectedGrading ? (
                <>
                  <div className="detail-header">
                    <h3>{t('detail.title')}</h3>
                    <button
                      className="btn-override"
                      onClick={() => setShowOverrideForm(true)}
                    >
                      ✏️ {t('detail.override')}
                    </button>
                  </div>

                  <div className="detail-content">
                    <div className="score-display">
                      <span className={`big-score ${getScoreColor(selectedGrading.percentage_score)}`}>
                        {selectedGrading.overall_score}
                      </span>
                      <span className="max-score">/ {selectedGrading.max_score}</span>
                      <span className="percentage">({selectedGrading.percentage_score.toFixed(1)}%)</span>
                    </div>

                    <div className="detail-info">
                      <p><strong>{t('detail.student')}:</strong> {selectedGrading.student_name || selectedGrading.student_external_id || t('detail.unknown')}</p>
                      <p><strong>{t('detail.assignment')}:</strong> {selectedGrading.assignment_title || t('detail.unknown')}</p>
                      <p><strong>{t('detail.submittedAt')}:</strong> {selectedGrading.submitted_at ? formatDate(selectedGrading.submitted_at) : t('detail.unknown')}</p>
                      <p><strong>{t('detail.gradedAt')}:</strong> {formatDate(selectedGrading.graded_at)}</p>
                      <p><strong>{t('detail.gradedBy')}:</strong> {selectedGrading.graded_by === 'AI' ? `🤖 ${t('detail.aiGrader')}` : `👨‍🏫 ${t('detail.teacherGrader')}`}</p>
                    </div>

                    {selectedGrading.feedback && (
                      <div className="feedback-section">
                        <h4>📋 {t('feedback.title')}</h4>
                        {selectedGrading.feedback.summary && (
                          <p className="feedback-summary">{selectedGrading.feedback.summary}</p>
                        )}
                        {selectedGrading.feedback.strengths && selectedGrading.feedback.strengths.length > 0 && (
                          <div className="feedback-list strengths">
                            <h5>✅ {t('feedback.strengths')}</h5>
                            <ul>
                              {selectedGrading.feedback.strengths.map((s, i) => (
                                <li key={i}>{s}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {selectedGrading.feedback.improvements && selectedGrading.feedback.improvements.length > 0 && (
                          <div className="feedback-list improvements">
                            <h5>💡 {t('feedback.improvements')}</h5>
                            <ul>
                              {selectedGrading.feedback.improvements.map((s, i) => (
                                <li key={i}>{s}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {selectedGrading.feedback.override_reason && (
                          <div className="override-info">
                            <p><strong>{t('feedback.overrideReason')}:</strong> {selectedGrading.feedback.override_reason}</p>
                            <p><strong>{t('feedback.originalScore')}:</strong> {selectedGrading.feedback.original_score}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="no-selection">
                  <p>👈 {t('detail.noSelection')}</p>
                </div>
              )}
            </section>
          </div>
        </div>
      )}

      {/* 覆盖评分模态框 */}
      {showOverrideForm && selectedGrading && (
        <div className="modal-overlay" onClick={() => setShowOverrideForm(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{t('overrideModal.title')}</h2>
              <button className="btn-close" onClick={() => setShowOverrideForm(false)}>×</button>
            </div>
            <div className="modal-body">
              <p>{t('overrideModal.currentScore')}: <strong>{selectedGrading.overall_score}/{selectedGrading.max_score}</strong></p>

              <div className="form-group">
                <label>{t('overrideModal.newScore')}</label>
                <input
                  type="number"
                  value={overrideScore}
                  onChange={(e) => setOverrideScore(Number(e.target.value))}
                  min={0}
                  max={selectedGrading.max_score}
                />
              </div>

              <div className="form-group">
                <label>{t('overrideModal.reason')}</label>
                <textarea
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  rows={3}
                  placeholder={t('overrideModal.reasonPlaceholder')}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowOverrideForm(false)}>
                {t('overrideModal.cancel')}
              </button>
              <button
                className="btn-primary"
                onClick={handleOverrideSubmit}
                disabled={submitting}
              >
                {submitting ? t('overrideModal.submitting') : t('overrideModal.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GradingInterface;

