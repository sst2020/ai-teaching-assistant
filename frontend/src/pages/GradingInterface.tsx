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
      console.error('加载作业列表失败', err);
    }
  }, []);

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
      setError('加载评分数据失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [selectedAssignment, page]);

  // 加载评分详情
  const loadGradingDetails = async (gradingId: number) => {
    setLoadingDetails(true);
    try {
      const details = await getGradingResult(gradingId);
      setSelectedGrading(details);
      setOverrideScore(details.overall_score);
    } catch (err) {
      setError('加载评分详情失败');
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
      setError('覆盖评分失败');
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
    return new Date(dateStr).toLocaleString('zh-CN', {
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
            ← 返回
          </button>
          <h1>✏️ 批改作业</h1>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      {/* 作业选择器 */}
      <div className="assignment-selector">
        <label>选择作业：</label>
        <select
          value={selectedAssignment || ''}
          onChange={(e) => {
            setSelectedAssignment(e.target.value || null);
            setPage(1);
            setSelectedGrading(null);
          }}
        >
          <option value="">-- 请选择作业 --</option>
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
              <h3>📊 评分统计</h3>
              <div className="stats-grid">
                <div className="stat-item">
                  <span className="stat-value">{statistics.total_graded}</span>
                  <span className="stat-label">已评分</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{statistics.average_score.toFixed(1)}</span>
                  <span className="stat-label">平均分</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{statistics.highest_score}</span>
                  <span className="stat-label">最高分</span>
                </div>
                <div className="stat-item">
                  <span className="stat-value">{statistics.lowest_score}</span>
                  <span className="stat-label">最低分</span>
                </div>
              </div>
              <div className="grader-stats">
                <span>🤖 AI 评分: {statistics.ai_graded_count}</span>
                <span>👨‍🏫 教师评分: {statistics.teacher_graded_count}</span>
              </div>
              <div className="score-distribution">
                <span className="dist-label">分数分布:</span>
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
              <h3>📝 提交列表</h3>
              {loading ? (
                <div className="loading">加载中...</div>
              ) : gradingResults.length === 0 ? (
                <div className="empty-state">暂无评分记录</div>
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
                          <span>提交 #{result.submission_id}</span>
                          <span>{formatDate(result.graded_at)}</span>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* 分页 */}
                  <div className="pagination">
                    <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                      上一页
                    </button>
                    <span>{page} / {totalPages}</span>
                    <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                      下一页
                    </button>
                  </div>
                </>
              )}
            </section>

            {/* 评分详情 */}
            <section className="grading-detail-panel">
              {loadingDetails ? (
                <div className="loading">加载详情中...</div>
              ) : selectedGrading ? (
                <>
                  <div className="detail-header">
                    <h3>评分详情</h3>
                    <button
                      className="btn-override"
                      onClick={() => setShowOverrideForm(true)}
                    >
                      ✏️ 覆盖评分
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
                      <p><strong>学生:</strong> {selectedGrading.student_name || selectedGrading.student_external_id || '未知'}</p>
                      <p><strong>作业:</strong> {selectedGrading.assignment_title || '未知'}</p>
                      <p><strong>提交时间:</strong> {selectedGrading.submitted_at ? formatDate(selectedGrading.submitted_at) : '未知'}</p>
                      <p><strong>评分时间:</strong> {formatDate(selectedGrading.graded_at)}</p>
                      <p><strong>评分者:</strong> {selectedGrading.graded_by === 'AI' ? '🤖 AI 自动评分' : '👨‍🏫 教师评分'}</p>
                    </div>

                    {selectedGrading.feedback && (
                      <div className="feedback-section">
                        <h4>📋 反馈详情</h4>
                        {selectedGrading.feedback.summary && (
                          <p className="feedback-summary">{selectedGrading.feedback.summary}</p>
                        )}
                        {selectedGrading.feedback.strengths && selectedGrading.feedback.strengths.length > 0 && (
                          <div className="feedback-list strengths">
                            <h5>✅ 优点</h5>
                            <ul>
                              {selectedGrading.feedback.strengths.map((s, i) => (
                                <li key={i}>{s}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {selectedGrading.feedback.improvements && selectedGrading.feedback.improvements.length > 0 && (
                          <div className="feedback-list improvements">
                            <h5>💡 改进建议</h5>
                            <ul>
                              {selectedGrading.feedback.improvements.map((s, i) => (
                                <li key={i}>{s}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {selectedGrading.feedback.override_reason && (
                          <div className="override-info">
                            <p><strong>覆盖原因:</strong> {selectedGrading.feedback.override_reason}</p>
                            <p><strong>原始分数:</strong> {selectedGrading.feedback.original_score}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <div className="no-selection">
                  <p>👈 点击左侧列表查看评分详情</p>
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
              <h2>覆盖评分</h2>
              <button className="btn-close" onClick={() => setShowOverrideForm(false)}>×</button>
            </div>
            <div className="modal-body">
              <p>当前分数: <strong>{selectedGrading.overall_score}/{selectedGrading.max_score}</strong></p>

              <div className="form-group">
                <label>新分数</label>
                <input
                  type="number"
                  value={overrideScore}
                  onChange={(e) => setOverrideScore(Number(e.target.value))}
                  min={0}
                  max={selectedGrading.max_score}
                />
              </div>

              <div className="form-group">
                <label>覆盖原因（可选）</label>
                <textarea
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  rows={3}
                  placeholder="说明为什么需要修改分数..."
                />
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={() => setShowOverrideForm(false)}>
                取消
              </button>
              <button
                className="btn-primary"
                onClick={handleOverrideSubmit}
                disabled={submitting}
              >
                {submitting ? '提交中...' : '确认覆盖'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GradingInterface;

