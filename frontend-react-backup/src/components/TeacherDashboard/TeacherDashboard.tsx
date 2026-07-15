/**
 * 教师仪表板组件 - 问题队列管理
 */
import React, { useState, useEffect, useCallback } from 'react';
import { PendingQuestion, TriageStats } from '../../types/triage';
import {
  getPendingQueue,
  teacherTakeover,
  teacherAnswer,
  getTriageStats,
} from '../../services/api';
import styles from './TeacherDashboard.module.css';

interface TeacherDashboardProps {
  teacherId: string;
  teacherName?: string;
  role?: 'teacher' | 'assistant';
}

const TeacherDashboard: React.FC<TeacherDashboardProps> = ({
  teacherId,
  teacherName,
  role = 'teacher',
}) => {
  const [questions, setQuestions] = useState<PendingQuestion[]>([]);
  const [stats, setStats] = useState<TriageStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedQuestion, setSelectedQuestion] = useState<PendingQuestion | null>(null);
  const [answerText, setAnswerText] = useState('');
  const [updateKB, setUpdateKB] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const loadQueue = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getPendingQueue(role, teacherId);
      setQuestions(response.questions);
    } catch (err) {
      setError('加载问题队列失败');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [role, teacherId]);

  const loadStats = useCallback(async () => {
    try {
      const response = await getTriageStats();
      setStats(response);
    } catch (err) {
      console.error('加载统计失败', err);
    }
  }, []);

  useEffect(() => {
    loadQueue();
    loadStats();
    const interval = setInterval(loadQueue, 30000);
    return () => clearInterval(interval);
  }, [loadQueue, loadStats]);

  const handleTakeover = async (question: PendingQuestion) => {
    try {
      await teacherTakeover({
        log_id: question.log_id,
        teacher_id: teacherId,
        teacher_name: teacherName,
      });
      setSelectedQuestion(question);
      setAnswerText('');
      setUpdateKB(false);
    } catch (err) {
      setError('接管问题失败');
      console.error(err);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!selectedQuestion || !answerText.trim()) return;
    setSubmitting(true);
    try {
      await teacherAnswer({
        log_id: selectedQuestion.log_id,
        teacher_id: teacherId,
        answer: answerText.trim(),
        update_knowledge_base: updateKB,
      });
      setSelectedQuestion(null);
      setAnswerText('');
      loadQueue();
      loadStats();
    } catch (err) {
      setError('提交回答失败');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  const formatWaitTime = (seconds: number) => {
    if (seconds < 60) return `${Math.round(seconds)}秒`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`;
    return `${Math.round(seconds / 3600)}小时`;
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>{`📋 ${role === 'teacher' ? '教师' : '助教'}问题队列`}</h2>
        {stats && (
          <div className={styles.stats}>
            <span className={styles.statItem}>待处理: {stats.pending}</span>
            <span className={styles.statItem + ' ' + styles.urgent}>紧急: {stats.urgent_pending}</span>
            <span className={styles.statItem}>今日回复: {stats.auto_replied + stats.to_assistant + stats.to_teacher}</span>
          </div>
        )}
      </div>

      {error && <div className={styles.error}>{error}</div>}

      <div className={styles.content}>
        <div className={styles.queuePanel}>
          <h3>待处理问题 ({questions.length})</h3>
          {loading && <div className={styles.loading}>加载中...</div>}
          <div className={styles.questionList}>
            {questions.map((q) => (
              <div
                key={q.log_id}
                className={`${styles.questionCard} ${q.is_urgent ? styles.urgent : ''} ${
                  selectedQuestion?.log_id === q.log_id ? styles.selected : ''
                }`}
                onClick={() => handleTakeover(q)}
              >
                <div className={styles.questionHeader}>
                  {q.is_urgent && <span className={styles.urgentBadge}>🚨 紧急</span>}
                  <span className={styles.difficulty}>{q.difficulty_label}</span>
                  <span className={styles.waitTime}>等待 {formatWaitTime(q.waiting_time_seconds)}</span>
                </div>
                <p className={styles.questionText}>{q.question}</p>
                <div className={styles.questionMeta}>
                  {q.user_name && <span>提问者: {q.user_name}</span>}
                  {q.detected_category && <span>分类: {q.detected_category}</span>}
                </div>
              </div>
            ))}
            {!loading && questions.length === 0 && (
              <div className={styles.empty}>暂无待处理问题 🎉</div>
            )}
          </div>
        </div>

        <div className={styles.answerPanel}>
          {selectedQuestion ? (
            <>
              <h3>回答问题</h3>
              <div className={styles.selectedQuestion}>
                <p>{selectedQuestion.question}</p>
              </div>
              <textarea
                value={answerText}
                onChange={(e) => setAnswerText(e.target.value)}
                placeholder="请输入你的回答..."
                rows={8}
                disabled={submitting}
              />
              <div className={styles.answerOptions}>
                <label>
                  <input
                    type="checkbox"
                    checked={updateKB}
                    onChange={(e) => setUpdateKB(e.target.checked)}
                    disabled={submitting}
                  />
                  添加到知识库
                </label>
                <button
                  onClick={handleSubmitAnswer}
                  disabled={submitting || !answerText.trim()}
                >
                  {submitting ? '提交中...' : '提交回答'}
                </button>
              </div>
            </>
          ) : (
            <div className={styles.noSelection}>
              <p>👈 点击左侧问题开始回答</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;

