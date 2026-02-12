/**
 * 智能问答分诊组件 - 增强版
 * 根据用户角色显示不同功能
 */
import React, { useState, useEffect } from 'react';
import { TriageResponse, TRIAGE_DECISION_LABELS } from '../../types/triage';
import { 
  askTriageQuestion, 
  markKnowledgeBaseEntryHelpful,
  getPendingQuestions,
  answerQuestion
} from '../../services/api';
import { useRoleAccess } from '../../hooks/useRoleAccess';
import styles from './QATriage.module.css';

interface QATriageProps {
  userId?: string;
  userName?: string;
  sessionId?: string;
}

const QATriage: React.FC<QATriageProps> = ({ userId, userName, sessionId }) => {
  // 学生功能状态
  const [question, setQuestion] = useState('');
  const [isUrgent, setIsUrgent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<TriageResponse | null>(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);

  // 教师功能状态
  const [pendingQuestions, setPendingQuestions] = useState<any[]>([]);
  const [selectedQuestion, setSelectedQuestion] = useState<any>(null);
  const [teacherAnswer, setTeacherAnswer] = useState('');
  const [answering, setAnswering] = useState(false);
  const [answerSuccess, setAnswerSuccess] = useState(false);

  // 角色检查
  const isStudent = useRoleAccess(['student']);
  const isTeacher = useRoleAccess(['teacher']);
  const isAdmin = useRoleAccess(['admin']);
  const isTeacherOrAdmin = useRoleAccess(['teacher', 'admin']);

  // 获取待回答问题列表（仅教师/管理员）
  useEffect(() => {
    if (isTeacherOrAdmin) {
      loadPendingQuestions();
    }
  }, [isTeacherOrAdmin]);

  const loadPendingQuestions = async () => {
    try {
      const data = await getPendingQuestions();
      setPendingQuestions(data);
    } catch (err) {
      console.error('获取待回答问题失败:', err);
    }
  };

  // 学生提交问题
  const handleStudentSubmit = async (e: React.FormEvent) => {
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

  // 教师回答问题
  const handleTeacherAnswer = async () => {
    if (!selectedQuestion || !teacherAnswer.trim()) return;

    setAnswering(true);
    try {
      await answerQuestion({
        log_id: selectedQuestion.log_id,
        teacher_id: userId || 'unknown',
        answer: teacherAnswer,
        update_knowledge_base: false, // 可以让用户选择是否更新知识库
        new_keywords: [] // 可以让用户输入新关键词
      });

      setAnswerSuccess(true);
      setTeacherAnswer('');
      setSelectedQuestion(null);
      
      // 重新加载待回答问题列表
      setTimeout(loadPendingQuestions, 1000);
    } catch (err) {
      setError('回答问题失败，请稍后重试');
      console.error(err);
    } finally {
      setAnswering(false);
    }
  };

  // 处理知识库反馈
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

      {/* 学生提问区域 */}
      {isStudent && (
        <div className={styles.studentSection}>
          <h3>📝 提问</h3>
          <form onSubmit={handleStudentSubmit} className={styles.form}>
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
        </div>
      )}

      {/* 教师回答问题区域 */}
      {isTeacherOrAdmin && (
        <div className={styles.teacherSection}>
          <h3>👨‍🏫 待回答问题</h3>
          {pendingQuestions.length > 0 ? (
            <div className={styles.pendingQuestions}>
              <select 
                value={selectedQuestion?.log_id || ''} 
                onChange={(e) => {
                  const question = pendingQuestions.find(q => q.log_id === e.target.value);
                  setSelectedQuestion(question);
                }}
                className={styles.questionSelect}
              >
                <option value="">选择一个问题</option>
                {pendingQuestions.map((q) => (
                  <option key={q.log_id} value={q.log_id}>
                    [{q.detected_category}] {q.question.substring(0, 50)}...
                  </option>
                ))}
              </select>

              {selectedQuestion && (
                <div className={styles.selectedQuestion}>
                  <h4>问题详情</h4>
                  <p><strong>分类:</strong> {selectedQuestion.detected_category}</p>
                  <p><strong>难度:</strong> {selectedQuestion.detected_difficulty}</p>
                  <p><strong>问题:</strong> {selectedQuestion.question}</p>
                  
                  <div className={styles.answerForm}>
                    <h4>回答</h4>
                    <textarea
                      value={teacherAnswer}
                      onChange={(e) => setTeacherAnswer(e.target.value)}
                      placeholder="请输入您的回答..."
                      rows={6}
                      disabled={answering}
                    />
                    <div className={styles.answerActions}>
                      <button 
                        onClick={handleTeacherAnswer} 
                        disabled={answering || !teacherAnswer.trim()}
                      >
                        {answering ? '提交中...' : '提交回答'}
                      </button>
                      {answerSuccess && (
                        <span className={styles.successMessage}>回答已提交！</span>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p>没有待回答的问题</p>
          )}
        </div>
      )}

      {error && <div className={styles.error}>{error}</div>}

      {/* 学生问题响应显示 */}
      {isStudent && response && (
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