/**
 * 评分结果相关类型定义
 * 与后端 schemas/grading.py 对应
 */

// 评分者类型
export type GradedBy = 'AI' | 'teacher';

// 反馈详情
export interface FeedbackDetail {
  category: string;
  message: string;
  severity?: 'info' | 'warning' | 'error';
  line_number?: number;
  suggestion?: string;
}

// 反馈结构
export interface GradingFeedback {
  summary?: string;
  strengths?: string[];
  improvements?: string[];
  details?: FeedbackDetail[];
  override_reason?: string;
  original_score?: number;
  [key: string]: unknown;
}

// 评分结果基础
export interface GradingResultBase {
  overall_score: number;
  max_score: number;
  feedback?: GradingFeedback;
}

// 创建评分结果请求
export interface GradingResultCreate extends GradingResultBase {
  submission_id: number;
  graded_by?: GradedBy;
  graded_at?: string;
}

// 更新评分结果请求
export interface GradingResultUpdate {
  overall_score?: number;
  max_score?: number;
  feedback?: GradingFeedback;
  graded_by?: GradedBy;
  graded_at?: string;
}

// 教师覆盖评分请求
export interface GradingResultOverride {
  overall_score: number;
  feedback?: GradingFeedback;
  override_reason?: string;
}

// 评分结果响应
export interface GradingResultResponse extends GradingResultBase {
  id: number;
  submission_id: number;
  graded_at: string;
  graded_by: GradedBy;
  percentage_score: number;
  created_at: string;
  updated_at?: string;
}

// 包含提交详情的评分结果
export interface GradingResultWithSubmission extends GradingResultResponse {
  submission_external_id?: string;
  student_id?: number;
  student_external_id?: string;
  student_name?: string;
  assignment_id?: number;
  assignment_external_id?: string;
  assignment_title?: string;
  submitted_at?: string;
}

// 评分结果列表响应
export interface GradingResultListResponse {
  items: GradingResultResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 包含提交详情的评分结果列表
export interface GradingResultWithSubmissionList {
  items: GradingResultWithSubmission[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// 分数分布
export interface ScoreDistribution {
  A: number;  // 90-100
  B: number;  // 80-89
  C: number;  // 70-79
  D: number;  // 60-69
  F: number;  // <60
}

// 评分统计信息
export interface GradingStatistics {
  total_graded: number;
  average_score: number;
  highest_score: number;
  lowest_score: number;
  ai_graded_count: number;
  teacher_graded_count: number;
  score_distribution: ScoreDistribution;
}

// 批量评分请求
export interface BatchGradingRequest {
  submission_ids: number[];
  use_ai?: boolean;
}

// 批量评分响应
export interface BatchGradingResponse {
  success_count: number;
  failed_count: number;
  results: GradingResultResponse[];
  errors: Array<{ submission_id: number; error: string }>;
}

