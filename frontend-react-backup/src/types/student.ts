// Student-related types

export interface Student {
  id: string;
  user_id: string;
  student_id: string;
  name: string;
  email: string;
  enrolled_courses: string[];
  created_at: string;
  updated_at: string;
}

export interface StudentProfile {
  id: string;
  user_id: string;
  student_id: string;
  name: string;
  email: string;
  enrolled_courses: Course[];
  total_submissions: number;
  average_grade: number;
  created_at: string;
}

export interface Course {
  id: string;
  name: string;
  code: string;
  description: string;
  instructor_name: string;
  semester: string;
  is_active: boolean;
  created_at: string;
}

export interface CourseEnrollment {
  course_id: string;
  student_id: string;
  enrolled_at: string;
  status: 'active' | 'completed' | 'dropped';
}

export interface StudentStats {
  total_courses: number;
  total_submissions: number;
  pending_assignments: number;
  average_grade: number;
  recent_activity: RecentActivity[];
}

export interface RecentActivity {
  id: string;
  type: 'submission' | 'grade' | 'feedback' | 'enrollment';
  description: string;
  timestamp: string;
  related_id?: string;
}

export interface UpdateProfileData {
  name?: string;
  email?: string;
  student_id?: string;
}

