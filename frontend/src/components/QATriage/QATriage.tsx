/**
 * 智能问答分诊组件
 */
import React, { useState } from 'react';
import { TriageResponse, TRIAGE_DECISION_LABELS } from '../../types/triage';
import { askTriageQuestion, markKnowledgeBaseEntryHelpful } from '../../services/api';
import styles from './QATriage.module.css';

interface QATriageProps {
  userId?: string;
  userName?: string;
  sessionId?: string;
}

const QATriage: React.FC<QATriageProps> = ({ userId, userName, sessionId }) => {
  const [question, setQuestion] = useState('');
  const [isUrgent, setIsUrgent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<TriageResponse | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);
    setFeedbackGiven(false);

    try {
      const result = await askTriageQuestion({
        question: question.trim(),
        user_id: userId,
        user_name: userName,
        session_id: sessionId,
        is_urgent: isUrgent,
      });
      setResponse(result);
    } catch (err) {
      setError('提交问题失败，请稍后重试');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleHelpful = async () => {
    if (!response?.matched_entry_id || feedbackGiven) return;
    try {
      await markKnowledgeBaseEntryHelpful(response.matched_entry_id);
      setFeedbackGiven(true);
    } catch (err) {
      console.error('反馈失败', err);
    }
  };

  const getDecisionIcon = (decision: string) => {
    switch (decision) {
      case 'auto_reply': return '🤖';
      case 'auto_reply_confirm': return '🤔';
      case 'to_assistant': return '👨‍🎓';
      case 'to_teacher': return '👨‍🏫';
      case 'to_teacher_urgent': return '🚨';
      default: return '❓';
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 0.8) return '#4caf50';
    if (score >= 0.5) return '#ff9800';
    return '#f44336';
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>💬 智能问答</h2>
        <p>有问题？让我来帮你找答案！</p>
      </div>

      <form onSubmit={handleSubmit} className={styles.form}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="请输入你的问题..."
          rows={4}
          disabled={loading}
        />
        <div className={styles.formFooter}>
          <label className={styles.urgentCheck}>
            <input
              type="checkbox"
              checked={isUrgent}
              onChange={(e) => setIsUrgent(e.target.checked)}
              disabled={loading}
            />
            <span>🚨 紧急问题</span>
          </label>
          <button type="submit" disabled={loading || !question.trim()}>
            {loading ? '处理中...' : '提交问题'}
          </button>
        </div>
      </form>

      {error && <div className={styles.error}>{error}</div>}

      {response && (
        <div className={styles.response}>
          <div className={styles.responseHeader}>
            <span className={styles.decision}>
              {getDecisionIcon(response.decision)}
              {TRIAGE_DECISION_LABELS[response.decision]}
            </span>
            <span
              className={styles.matchScore}
              style={{ color: getMatchScoreColor(response.match_score) }}
            >
              匹配度: {(response.match_score * 100).toFixed(0)}%
            </span>
          </div>

          <div className={styles.meta}>
            {response.detected_category && (
              <span className={styles.category}>分类: {response.detected_category}</span>
            )}
            <span className={styles.difficulty}>{response.difficulty_label}</span>
          </div>

          <div className={styles.confidenceMessage}>
            {response.confidence_message}
          </div>

          {response.answer && (
            <div className={styles.answer}>
              <h4>💡 回答</h4>
              <div className={styles.answerContent}>
                {response.answer.split('\n').map((line, i) => (
                  <p key={i}>{line}</p>
                ))}
              </div>
              {response.matched_entry_id && !feedbackGiven && (
                <div className={styles.feedback}>
                  <span>这个回答有帮助吗？</span>
                  <button onClick={handleHelpful}>👍 有帮助</button>
                </div>
              )}
              {feedbackGiven && (
                <div className={styles.feedbackThanks}>感谢你的反馈！</div>
              )}
            </div>
          )}

          {!response.answer && (
            <div className={styles.noAnswer}>
              <p>暂时没有找到匹配的答案，问题已转交{
                response.decision === 'to_assistant' ? '助教' : '教师'
              }处理。</p>
              <p>请耐心等待回复。</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default QATriage;

