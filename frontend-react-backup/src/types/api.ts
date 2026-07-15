// API Response Types

export interface HealthResponse {
  status: string;
  version: string;
  timestamp: string;
}

export interface ApiInfo {
  name: string;
  version: string;
  description: string;
  docs_url: string;
}

// Code Analysis Types
export interface CodeAnalysisRequest {
  code: string;
  language: string;
  include_style?: boolean;
  include_complexity?: boolean;
  include_smells?: boolean;
}

export interface StyleIssue {
  line: number;
  column: number;
  code: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
}

export interface FunctionComplexity {
  name: string;
  complexity: number;
  start_line: number;
  end_line: number;
  risk: string;
}

export interface CodeSmell {
  type: string;
  description: string;
  location: string;
  severity: string;
  suggestion: string;
}

export interface ComplexityMetrics {
  cyclomatic_complexity: number;
  maintainability_index: number;
  lines_of_code: number;
  function_count: number;
  average_complexity: number;
  functions: FunctionComplexity[];
}

export interface StyleAnalysis {
  total_issues: number;
  errors: number;
  warnings: number;
  issues: StyleIssue[];
}

export interface CodeAnalysisResponse {
  analysis_id: string;
  language: string;
  analyzed_at: string;
  complexity_metrics: ComplexityMetrics;
  style_analysis: StyleAnalysis;
  code_smells: CodeSmell[];
  overall_quality_score: number;
  recommendations: string[];
}

// Assignment Grading Types
export interface AssignmentSubmission {
  student_id: string;
  assignment_id: string;
  assignment_type: 'code' | 'essay' | 'quiz';
  content: string;
  rubric_id?: string;
}

export interface GradingResult {
  submission_id: string;
  student_id: string;
  assignment_id: string;
  overall_score: number;
  max_score: number;
  status: string;
  feedback: string[];
  graded_at: string;
  feedback_summary: string;
}

// Q&A Types
export interface QuestionRequest {
  student_id: string;
  course_id: string;
  question: string;
  context?: string;
}

// AI 生成的回答结构
export interface AIAnswer {
  answer: string;
  confidence: number;
  sources: string[];
  needs_teacher_review: boolean;
}

export interface QuestionResponse {
  question_id: string;
  student_id: string;
  course_id: string;
  question: string;
  ai_answer: AIAnswer | null;
  teacher_answer: string | null;
  category: string;
  status: string;
  created_at: string;
  answered_at: string | null;
}

// Q&A 智能问答请求（持久化版本）
export interface QALogCreate {
  user_id: string;
  user_name?: string;
  session_id?: string;
  question: string;
}

// Q&A 日志响应
export interface QALogResponse {
  log_id: string;
  user_id: string;
  user_name?: string;
  session_id?: string;
  question: string;
  question_keywords?: string[];
  detected_category?: string;
  detected_difficulty?: number;
  matched_entry_id?: string;
  match_score?: number;
  match_method?: string;
  answer?: string;
  answer_source?: string;
  triage_result?: string;
  assigned_to?: string;
  priority?: number;
  is_urgent?: boolean;
  status?: string;
  is_helpful?: boolean;
  feedback_text?: string;
  handled_by?: string;
  handled_at?: string;
  response_time_seconds?: number;
  created_at: string;
  updated_at?: string;
}

// Q&A 统计信息
export interface QALogStats {
  total_questions: number;
  auto_replied: number;
  to_assistant: number;
  to_teacher: number;
  pending: number;
  avg_response_time: number;
  helpful_rate?: number;
  questions_by_category: Record<string, number>;
  questions_by_difficulty: Record<string, number>;
}

// 知识薄弱点
export interface KnowledgeGap {
  topic: string;
  frequency: number;
  difficulty_level: string;
  sample_questions: string[];
}

// Q&A 分析报告
export interface QAAnalyticsReport {
  course_id: string;
  period_start: string;
  period_end: string;
  total_questions: number;
  ai_resolved_count: number;
  teacher_resolved_count: number;
  average_response_time_seconds: number;
  knowledge_gaps: KnowledgeGap[];
  common_topics: Array<{ topic: string; count: number }>;
  recommendations: string[];
}

// 学生知识薄弱点报告
export interface StudentWeaknessReport {
  student_id: string;
  total_questions: number;
  resolution_rate?: number;
  weakness_areas: Array<{ topic: string; frequency: number }>;
  improvement_suggestions: string[];
}

// Plagiarism Types
export interface PlagiarismRequest {
  submission_id: string;
  student_id: string;
  course_id: string;
  code: string;
}

export interface PlagiarismMatch {
  matched_submission_id: string;
  matched_student_id: string;
  similarity_score: number;
  matching_sections: string[];
}

export interface PlagiarismResponse {
  submission_id: string;
  student_id: string;
  checked_at: string;
  overall_similarity: number;
  is_flagged: boolean;
  matches: PlagiarismMatch[];
  fingerprint: string;
}

// API Error
export interface ApiError {
  detail: string;
  status_code?: number;
}

