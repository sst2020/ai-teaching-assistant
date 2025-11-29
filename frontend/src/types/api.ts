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

export interface QuestionResponse {
  question_id: string;
  student_id: string;
  course_id: string;
  question: string;
  ai_answer: string;
  confidence: number;
  category: string;
  status: string;
  needs_teacher_review: boolean;
  created_at: string;
  answered_at: string;
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

