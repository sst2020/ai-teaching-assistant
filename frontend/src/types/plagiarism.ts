/**
 * 查重与原创性分析系统 - 类型定义
 */

// 相似度算法类型
export type SimilarityAlgorithm = 'ast' | 'levenshtein' | 'cosine' | 'token' | 'combined';

// 代码变换类型
export type CodeTransformationType =
  | 'variable_rename'
  | 'function_rename'
  | 'extract_function'
  | 'inline_variable'
  | 'reorder_statements'
  | 'comment_modification'
  | 'whitespace_change';

// 相似度等级
export type SimilarityLevel = 'none' | 'low' | 'medium' | 'high' | 'very_high';

// 匹配类型
export type MatchType = 'exact' | 'structural' | 'token_sequence' | 'renamed' | 'partial';

// 详细代码匹配信息
export interface DetailedCodeMatch {
  source_student_id: string;
  target_student_id: string;
  source_start_line: number;
  source_end_line: number;
  source_start_col: number;
  source_end_col: number;
  target_start_line: number;
  target_end_line: number;
  target_start_col: number;
  target_end_col: number;
  source_snippet: string;
  target_snippet: string;
  similarity: number;
  algorithm: SimilarityAlgorithm;
  transformation_type?: CodeTransformationType;
  explanation: string;
}

// 代码匹配
export interface CodeMatch {
  match_type: MatchType;
  similarity: number;
  code_snippet_1: string;
  code_snippet_2: string;
  line_range_1: [number, number];
  line_range_2: [number, number];
  explanation: string;
}

// 相似度矩阵条目
export interface SimilarityMatrixEntry {
  student_id_1: string;
  student_id_2: string;
  student_name_1: string;
  student_name_2: string;
  similarity_score: number;
  algorithm_scores: Record<string, number>;
  is_flagged: boolean;
}

// 相似度矩阵
export interface SimilarityMatrix {
  report_id: string;
  assignment_id: string;
  created_at: string;
  student_ids: string[];
  student_names: string[];
  matrix: number[][];
  entries: SimilarityMatrixEntry[];
  threshold: number;
  flagged_count: number;
}

// 提交对比结果
export interface SubmissionComparison {
  submission_id_1: string;
  submission_id_2: string;
  student_id_1: string;
  student_id_2: string;
  similarity_score: number;
  matches: CodeMatch[];
  analysis_notes: string;
}

// 原创性报告
export interface OriginalityReport {
  report_id: string;
  submission_id: string;
  student_id: string;
  student_name: string;
  assignment_id: string;
  created_at: string;
  originality_score: number;
  similarity_breakdown: Record<string, number>;
  detailed_matches: DetailedCodeMatch[];
  similar_submissions: string[];
  detected_transformations: CodeTransformationType[];
  improvement_suggestions: string[];
  summary: string;
  risk_level: SimilarityLevel;
}

// 提交数据
export interface SubmissionData {
  student_id: string;
  student_name?: string;
  code: string;
  submission_id?: string;
}

// 批量分析请求
export interface BatchAnalysisRequest {
  assignment_id: string;
  course_id?: string;
  submissions: SubmissionData[];
  similarity_threshold?: number;
  algorithms?: SimilarityAlgorithm[];
  generate_reports?: boolean;
}

// 批量分析响应
export interface BatchAnalysisResponse {
  report_id: string;
  assignment_id: string;
  created_at: string;
  total_submissions: number;
  total_comparisons: number;
  flagged_count: number;
  similarity_matrix: SimilarityMatrix;
  suspicious_pairs: SubmissionComparison[];
  originality_reports: OriginalityReport[];
  summary: string;
}

// 查重设置
export interface PlagiarismSettings {
  similarity_threshold: number;
  algorithms: SimilarityAlgorithm[];
  ast_weight: number;
  token_weight: number;
  text_weight: number;
  detect_renaming: boolean;
  detect_refactoring: boolean;
}

// 上传的文件信息
export interface UploadedFile {
  file: File;
  studentId: string;
  studentName: string;
  code: string;
  status: 'pending' | 'reading' | 'ready' | 'error';
  error?: string;
}

// 教师提交作业的请求类型
export interface TeacherAssignmentSubmit {
  assignment_id: string;
  course_id: string;
  title: string;
  description: string;
  due_date: string; // ISO 8601 format
  max_score?: number;
  assignment_type?: string;
  file_attachment?: ArrayBuffer; // 文件内容
  file_name?: string;
  rubric?: Record<string, any>;
  instructions?: string;
}

// 批量上传请求类型
export interface BatchUploadRequest {
  assignment_id: string;
  course_id: string;
  student_submissions: Array<{
    student_id: string;
    student_name: string;
    file_content: string;
    file_name: string;
  }>;
  sync_to_file_manager: boolean;
}

// 文件管理同步请求类型
export interface FileManagerSyncRequest {
  assignment_id: string;
  course_id: string;
  sync_type: 'full' | 'incremental';
  target_path: string;
  include_submissions?: boolean;
  include_feedback?: boolean;
}

// 文件管理同步响应类型
export interface FileManagerSyncResponse {
  sync_id: string;
  assignment_id: string;
  course_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  total_files: number;
  processed_files: number;
  failed_files: number;
  start_time: string;
  end_time?: string;
  error_message?: string;
}

// 作业提交记录类型
export interface AssignmentSubmissionRecord {
  submission_id: string;
  assignment_id: string;
  student_id: string;
  student_name: string;
  file_name: string;
  file_size: number;
  submitted_at: string;
  status: string;
  content_preview: string;
}

// 作业传输响应类型
export interface AssignmentTransferResponse {
  transfer_id: string;
  assignment_id: string;
  course_id: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed' | 'cancelled';
  total_submissions: number;
  successful_transfers: number;
  failed_transfers: number;
  start_time: string;
  end_time?: string;
  error_details?: Array<Record<string, any>>;
}

// 文件验证结果类型
export interface FileValidationResult {
  filename: string;
  is_valid: boolean;
  validation_errors: string[];
  file_size: number;
  detected_language?: string;
}

// 批量上传响应类型
export interface BatchUploadResponse {
  upload_id: string;
  assignment_id: string;
  course_id: string;
  total_files: number;
  successfully_uploaded: number;
  failed_uploads: number;
  validation_results: FileValidationResult[];
  start_time: string;
  end_time?: string;
}

