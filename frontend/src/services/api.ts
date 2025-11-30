import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  HealthResponse,
  ApiInfo,
  CodeAnalysisRequest,
  CodeAnalysisResponse,
  AssignmentSubmission,
  GradingResult,
  QuestionRequest,
  QuestionResponse,
  PlagiarismRequest,
  PlagiarismResponse,
  ApiError,
} from '../types/api';
import {
  LoginCredentials,
  RegisterData,
  LoginResponse,
  RegisterResponse,
  AuthTokens,
  User,
} from '../types/auth';
import {
  StudentProfile,
  Course,
  StudentStats,
  UpdateProfileData,
} from '../types/student';
import {
  Submission,
  CreateSubmissionRequest,
  SubmissionListResponse,
  SubmissionFilters,
  SubmissionStats,
} from '../types/submission';
import {
  Assignment,
  AssignmentListResponse,
  AssignmentFilters,
  AssignmentWithSubmission,
  AssignmentStats,
  Rubric,
} from '../types/assignment';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_V1_PREFIX = '/api/v1';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API] Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`[API] Response ${response.status}:`, response.data);
    return response;
  },
  (error: AxiosError<ApiError>) => {
    console.error('[API] Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Helper function to handle API errors
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    if (axiosError.message) {
      return axiosError.message;
    }
  }
  return 'An unexpected error occurred';
};

// ============ Health & Info Endpoints ============

export const getApiInfo = async (): Promise<ApiInfo> => {
  const response = await apiClient.get<ApiInfo>('/');
  return response.data;
};

export const getHealthStatus = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};

// ============ Code Analysis Endpoints ============

export const analyzeCode = async (request: CodeAnalysisRequest): Promise<CodeAnalysisResponse> => {
  const response = await apiClient.post<CodeAnalysisResponse>(
    `${API_V1_PREFIX}/assignments/analyze-code`,
    request
  );
  return response.data;
};

// ============ Assignment Grading Endpoints ============

export const gradeAssignment = async (submission: AssignmentSubmission): Promise<GradingResult> => {
  const response = await apiClient.post<GradingResult>(
    `${API_V1_PREFIX}/assignments/grade`,
    submission
  );
  return response.data;
};

// ============ Q&A Endpoints ============

export const askQuestion = async (request: QuestionRequest): Promise<QuestionResponse> => {
  const response = await apiClient.post<QuestionResponse>(
    `${API_V1_PREFIX}/qa/ask`,
    request
  );
  return response.data;
};

// ============ Plagiarism Detection Endpoints ============

export const checkPlagiarism = async (request: PlagiarismRequest): Promise<PlagiarismResponse> => {
  const response = await apiClient.post<PlagiarismResponse>(
    `${API_V1_PREFIX}/assignments/plagiarism/check`,
    request
  );
  return response.data;
};

// ============ Authentication Endpoints ============

export const login = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  const response = await apiClient.post<LoginResponse>(
    `${API_V1_PREFIX}/auth/login`,
    credentials
  );
  return response.data;
};

export const register = async (data: RegisterData): Promise<RegisterResponse> => {
  const response = await apiClient.post<RegisterResponse>(
    `${API_V1_PREFIX}/auth/register`,
    data
  );
  return response.data;
};

export const refreshToken = async (refresh_token: string): Promise<AuthTokens> => {
  const response = await apiClient.post<AuthTokens>(
    `${API_V1_PREFIX}/auth/refresh`,
    { refresh_token }
  );
  return response.data;
};

export const logout = async (): Promise<void> => {
  await apiClient.post(`${API_V1_PREFIX}/auth/logout`);
};

export const getCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get<User>(`${API_V1_PREFIX}/auth/me`);
  return response.data;
};

// ============ Auth Token Management ============

// Function to set auth token in request headers
export const setAuthToken = (token: string | null) => {
  if (token) {
    apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete apiClient.defaults.headers.common['Authorization'];
  }
};

// ============ Student Endpoints ============

export const getStudentProfile = async (): Promise<StudentProfile> => {
  const response = await apiClient.get<StudentProfile>(`${API_V1_PREFIX}/students/profile`);
  return response.data;
};

export const updateStudentProfile = async (data: UpdateProfileData): Promise<StudentProfile> => {
  const response = await apiClient.put<StudentProfile>(
    `${API_V1_PREFIX}/students/profile`,
    data
  );
  return response.data;
};

export const getStudentStats = async (): Promise<StudentStats> => {
  const response = await apiClient.get<StudentStats>(`${API_V1_PREFIX}/students/stats`);
  return response.data;
};

export const getEnrolledCourses = async (): Promise<Course[]> => {
  const response = await apiClient.get<Course[]>(`${API_V1_PREFIX}/students/courses`);
  return response.data;
};

export const enrollInCourse = async (courseId: string): Promise<void> => {
  await apiClient.post(`${API_V1_PREFIX}/students/courses/${courseId}/enroll`);
};

export const dropCourse = async (courseId: string): Promise<void> => {
  await apiClient.delete(`${API_V1_PREFIX}/students/courses/${courseId}/drop`);
};

// ============ Submission Endpoints ============

export const createSubmission = async (data: CreateSubmissionRequest): Promise<Submission> => {
  const formData = new FormData();
  formData.append('assignment_id', data.assignment_id);
  formData.append('content', data.content);
  if (data.file) {
    formData.append('file', data.file);
  }

  const response = await apiClient.post<Submission>(
    `${API_V1_PREFIX}/submissions`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

export const getSubmission = async (submissionId: string): Promise<Submission> => {
  const response = await apiClient.get<Submission>(
    `${API_V1_PREFIX}/submissions/${submissionId}`
  );
  return response.data;
};

export const getSubmissions = async (filters?: SubmissionFilters): Promise<SubmissionListResponse> => {
  const params = new URLSearchParams();
  if (filters?.assignment_id) params.append('assignment_id', filters.assignment_id);
  if (filters?.course_id) params.append('course_id', filters.course_id);
  if (filters?.status) params.append('status', filters.status);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.page_size) params.append('page_size', filters.page_size.toString());

  const response = await apiClient.get<SubmissionListResponse>(
    `${API_V1_PREFIX}/submissions?${params.toString()}`
  );
  return response.data;
};

export const updateSubmission = async (
  submissionId: string,
  content: string
): Promise<Submission> => {
  const response = await apiClient.put<Submission>(
    `${API_V1_PREFIX}/submissions/${submissionId}`,
    { content }
  );
  return response.data;
};

export const deleteSubmission = async (submissionId: string): Promise<void> => {
  await apiClient.delete(`${API_V1_PREFIX}/submissions/${submissionId}`);
};

export const getSubmissionStats = async (): Promise<SubmissionStats> => {
  const response = await apiClient.get<SubmissionStats>(
    `${API_V1_PREFIX}/submissions/stats`
  );
  return response.data;
};

// ============ Assignment Endpoints ============

export const getAssignment = async (assignmentId: string): Promise<Assignment> => {
  const response = await apiClient.get<Assignment>(
    `${API_V1_PREFIX}/assignments/${assignmentId}`
  );
  return response.data;
};

export const getAssignments = async (filters?: AssignmentFilters): Promise<AssignmentListResponse> => {
  const params = new URLSearchParams();
  if (filters?.course_id) params.append('course_id', filters.course_id);
  if (filters?.assignment_type) params.append('assignment_type', filters.assignment_type);
  if (filters?.is_published !== undefined) params.append('is_published', filters.is_published.toString());
  if (filters?.due_before) params.append('due_before', filters.due_before);
  if (filters?.due_after) params.append('due_after', filters.due_after);
  if (filters?.page) params.append('page', filters.page.toString());
  if (filters?.page_size) params.append('page_size', filters.page_size.toString());

  const response = await apiClient.get<AssignmentListResponse>(
    `${API_V1_PREFIX}/assignments?${params.toString()}`
  );
  return response.data;
};

export const getAssignmentsWithSubmissions = async (
  courseId?: string
): Promise<AssignmentWithSubmission[]> => {
  const params = courseId ? `?course_id=${courseId}` : '';
  const response = await apiClient.get<AssignmentWithSubmission[]>(
    `${API_V1_PREFIX}/assignments/with-submissions${params}`
  );
  return response.data;
};

export const getAssignmentStats = async (courseId?: string): Promise<AssignmentStats> => {
  const params = courseId ? `?course_id=${courseId}` : '';
  const response = await apiClient.get<AssignmentStats>(
    `${API_V1_PREFIX}/assignments/stats${params}`
  );
  return response.data;
};

export const getAssignmentRubric = async (assignmentId: string): Promise<Rubric> => {
  const response = await apiClient.get<Rubric>(
    `${API_V1_PREFIX}/assignments/${assignmentId}/rubric`
  );
  return response.data;
};

// Export the axios instance for custom requests
export default apiClient;

