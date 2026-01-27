// Assignment-related types

export interface Assignment {
  id: number | string;  // 数据库 ID
  assignment_id?: string;  // 唯一标识符（后端返回）
  course_id: string;
  title: string;
  description: string;
  instructions: string;
  assignment_type: AssignmentType;
  max_score: number;
  due_date: string;
  created_at: string;
  updated_at: string;
  is_published: boolean;
  allow_late_submission: boolean;
  late_penalty_percent?: number;
  rubric_id?: string;
  attachments?: AssignmentAttachment[];
}

export type AssignmentType = 'code' | 'essay' | 'quiz' | 'project';

export interface AssignmentAttachment {
  id: string;
  filename: string;
  url: string;
  size: number;
  uploaded_at: string;
}

export interface AssignmentListResponse {
  items: Assignment[];
  assignments?: Assignment[]; // 兼容旧字段名
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AssignmentFilters {
  course_id?: string;
  assignment_type?: AssignmentType;
  is_published?: boolean;
  due_before?: string;
  due_after?: string;
  page?: number;
  page_size?: number;
}

export interface AssignmentWithSubmission extends Assignment {
  submission?: {
    id: string;
    status: string;
    submitted_at?: string;
    grade?: number;
  };
}

export interface AssignmentStats {
  total_assignments: number;
  pending_count: number;
  submitted_count: number;
  graded_count: number;
  overdue_count: number;
}

export interface Rubric {
  id: string;
  name: string;
  description: string;
  criteria: RubricCriterion[];
  total_points: number;
}

export interface RubricCriterion {
  id: string;
  name: string;
  description: string;
  max_points: number;
  levels: RubricLevel[];
}

export interface RubricLevel {
  points: number;
  description: string;
}

