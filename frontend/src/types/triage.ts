/**
 * 分诊相关类型定义
 */

// 分诊决策枚举
export type TriageDecision =
  | 'auto_reply'
  | 'auto_reply_confirm'
  | 'to_assistant'
  | 'to_teacher'
  | 'to_teacher_urgent';

// 问答日志状态枚举
export type QALogStatus = 'answered' | 'pending' | 'escalated' | 'closed';

// 分诊结果枚举
export type TriageResult = 'auto_reply' | 'to_assistant' | 'to_teacher' | 'pending';

// 分诊决策标签映射
export const TRIAGE_DECISION_LABELS: Record<TriageDecision, string> = {
  auto_reply: '自动回复',
  auto_reply_confirm: '自动回复（待确认）',
  to_assistant: '转助教',
  to_teacher: '转教师',
  to_teacher_urgent: '紧急转教师',
};

// 状态标签映射
export const STATUS_LABELS: Record<QALogStatus, string> = {
  answered: '已回答',
  pending: '待处理',
  escalated: '已升级',
  closed: '已关闭',
};

// 分诊请求
export interface TriageRequest {
  question: string;
  user_id?: string;
  user_name?: string;
  session_id?: string;
  is_urgent?: boolean;
  context?: string;
}

// 分诊响应
export interface TriageResponse {
  log_id: string;
  question: string;
  detected_category: string | null;
  detected_difficulty: number;
  difficulty_label: string;
  match_score: number;
  matched_entry_id: string | null;
  decision: TriageDecision;
  answer: string | null;
  answer_source: string | null;
  assigned_to: string | null;
  priority: number;
  is_urgent: boolean;
  confidence_message: string;
  created_at: string;
}

// 待处理问题
export interface PendingQuestion {
  log_id: string;
  question: string;
  user_id: string | null;
  user_name: string | null;
  detected_category: string | null;
  detected_difficulty: number;
  difficulty_label: string;
  match_score: number | null;
  priority: number;
  is_urgent: boolean;
  triage_result: string;
  created_at: string;
  waiting_time_seconds: number;
}

// 待处理队列响应
export interface PendingQueueResponse {
  total: number;
  urgent_count: number;
  questions: PendingQuestion[];
}

// 教师接管请求
export interface TeacherTakeoverRequest {
  log_id: string;
  teacher_id: string;
  teacher_name?: string;
}

// 教师回答请求
export interface TeacherAnswerRequest {
  log_id: string;
  teacher_id: string;
  answer: string;
  update_knowledge_base?: boolean;
  new_keywords?: string[];
}

// 教师回答响应
export interface TeacherAnswerResponse {
  log_id: string;
  answer: string;
  answered_by: string;
  answered_at: string;
  knowledge_base_updated: boolean;
  new_entry_id: string | null;
}

// 分诊统计
export interface TriageStats {
  total_questions: number;
  auto_replied: number;
  to_assistant: number;
  to_teacher: number;
  pending: number;
  urgent_pending: number;
  avg_response_time: number | null;
  avg_waiting_time: number | null;
  resolution_rate: number;
  questions_by_difficulty: Record<string, number>;
  questions_by_decision: Record<string, number>;
}

// 难度级别信息
export interface DifficultyInfo {
  level: string;
  name: string;
  description: string;
  examples: string[];
}

// 难度级别列表响应
export interface DifficultyLevelsResponse {
  levels: DifficultyInfo[];
}

