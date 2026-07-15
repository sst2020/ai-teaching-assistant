// User types
export interface User {
  id: string
  name: string
  email: string
  role: 'student' | 'teacher' | 'admin'
  student_id?: string
  created_at: string
}

export interface LoginCredentials {
  username: string  // 学号或职工号（10位数字）
  password: string
}

export interface RegisterData {
  name: string
  email: string
  password: string
  role: 'student' | 'teacher'
  student_id?: string  // 学生为学号，教师为职工号，均为10位数字
}

// Assignment types
export interface Assignment {
  id: string
  title: string
  description: string
  due_date: string
  created_by: string
  created_at: string
  status: 'active' | 'closed' | 'draft'
}

export interface Submission {
  id: string
  assignment_id: string
  student_id: string
  files: CodeFile[]
  status: 'submitted' | 'grading' | 'graded'
  submitted_at: string
  grade?: number
  feedback?: string
}

export interface CodeFile {
  id: string
  filename: string
  language: string
  content: string
}

// Grading types
export interface GradingResult {
  id: string
  submission_id: string
  total_score: number
  max_score: number
  rubric_scores: Record<string, number>
  feedback: string
  suggestions: string[]
  plagiarism_check?: PlagiarismResult
  created_at: string
}

export interface PlagiarismResult {
  similarity_score: number
  matches: PlagiarismMatch[]
}

export interface PlagiarismMatch {
  source_file: string
  matched_file: string
  similarity: number
  lines: number[]
}

// Rubric types
export interface Rubric {
  id: string
  assignment_id: string
  name: string
  criteria: RubricCriterion[]
  max_score: number
}

export interface RubricCriterion {
  id: string
  name: string
  description: string
  weight: number
  max_score: number
}

// QA types
export interface QAQuestion {
  id: string
  question: string
  answer?: string
  category?: string
  created_by: string
  created_at: string
  status: 'pending' | 'answered' | 'escalated'
}

export interface KnowledgeBaseEntry {
  id: string
  title: string
  content: string
  category: string
  tags: string[]
  created_at: string
}

// API Response types
export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

// Toast notification types
export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
}

// Student Record types
export interface StudentRecord {
  id: number
  name: string
  student_id: string
  assignment_number: string
  created_at: string
  updated_at: string | null
}

export interface StudentRecordCreate {
  name: string
  student_id: string
  password: string
  assignment_number: string
}

export interface StudentRecordUpdate {
  name?: string
  student_id?: string
  password?: string
  assignment_number?: string
}
