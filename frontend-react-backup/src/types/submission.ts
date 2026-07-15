// Submission-related types

export interface Submission {
  id: string;
  student_id: string;
  assignment_id: string;
  course_id: string;
  content: string;
  file_url?: string;
  submitted_at: string;
  status: SubmissionStatus;
  grade?: number;
  max_grade: number;
  feedback?: string;
  graded_at?: string;
  graded_by?: string;
}

export type SubmissionStatus = 
  | 'pending' 
  | 'submitted' 
  | 'grading' 
  | 'graded' 
  | 'returned' 
  | 'late';

export interface CreateSubmissionRequest {
  assignment_id: string;
  content: string;
  file?: File;
}

export interface SubmissionListResponse {
  submissions: Submission[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface SubmissionFilters {
  assignment_id?: string;
  course_id?: string;
  status?: SubmissionStatus;
  page?: number;
  page_size?: number;
}

export interface SubmissionFeedback {
  submission_id: string;
  grade: number;
  feedback: string;
  detailed_feedback?: DetailedFeedback[];
}

export interface DetailedFeedback {
  category: string;
  score: number;
  max_score: number;
  comments: string;
}

export interface SubmissionStats {
  total_submissions: number;
  pending_count: number;
  graded_count: number;
  average_grade: number;
  on_time_rate: number;
}

