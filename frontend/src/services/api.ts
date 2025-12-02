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
import {
  BatchAnalysisRequest,
  BatchAnalysisResponse,
  OriginalityReport,
  SimilarityMatrix,
  PlagiarismSettings,
} from '../types/plagiarism';
import {
  ReportAnalysisRequest,
  ReportAnalysisResponse,
} from '../types/reportAnalysis';

// 扩展 Axios 配置类型以支持 metadata
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

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

// Enhanced request interceptor with detailed logging and performance tracking
apiClient.interceptors.request.use(
  (config) => {
    // Add request timestamp for performance tracking
    config.metadata = { startTime: Date.now() };

    // Add unique request ID for tracking
    const requestId = Math.random().toString(36).substr(2, 9);
    config.headers['X-Request-ID'] = requestId;

    // Enhanced logging
    const isDebugMode = process.env.REACT_APP_DEBUG_MODE === 'true';
    const enableApiLogging = process.env.REACT_APP_ENABLE_API_LOGGING === 'true';

    if (isDebugMode && enableApiLogging) {
      console.group(`🚀 [API Request] ${config.method?.toUpperCase()} ${config.url}`);
      console.log('📋 Request ID:', requestId);
      console.log('🔗 URL:', (config.baseURL || '') + (config.url || ''));
      console.log('📤 Method:', config.method?.toUpperCase());
      console.log('📋 Headers:', config.headers);
      if (config.data) {
        console.log('📦 Data:', config.data);
      }
      if (config.params) {
        console.log('🔍 Params:', config.params);
      }
      console.log('⏰ Timestamp:', new Date().toISOString());
      console.groupEnd();
    }

    return config;
  },
  (error) => {
    console.error('❌ [API] Request error:', error);
    return Promise.reject(error);
  }
);

// Enhanced response interceptor with performance tracking and detailed error handling
apiClient.interceptors.response.use(
  (response) => {
    // Calculate response time
    const startTime = response.config.metadata?.startTime;
    const responseTime = startTime ? Date.now() - startTime : 0;

    // Add response time to headers for debugging
    response.headers['X-Response-Time'] = `${responseTime}ms`;

    const isDebugMode = process.env.REACT_APP_DEBUG_MODE === 'true';
    const enableApiLogging = process.env.REACT_APP_ENABLE_API_LOGGING === 'true';
    const enablePerformanceMonitoring = process.env.REACT_APP_ENABLE_PERFORMANCE_MONITORING === 'true';

    if (isDebugMode && enableApiLogging) {
      const requestId = response.config.headers['X-Request-ID'];
      const statusColor = response.status >= 200 && response.status < 300 ? '✅' : '⚠️';

      console.group(`${statusColor} [API Response] ${response.status} ${response.config.method?.toUpperCase()} ${response.config.url}`);
      console.log('📋 Request ID:', requestId);
      console.log('📊 Status:', response.status, response.statusText);
      console.log('⏱️ Response Time:', `${responseTime}ms`);
      console.log('📥 Headers:', response.headers);
      console.log('📦 Data:', response.data);
      console.log('⏰ Timestamp:', new Date().toISOString());
      console.groupEnd();
    }

    // Performance monitoring
    if (enablePerformanceMonitoring && responseTime > 0) {
      // Store performance data for monitoring dashboard
      const performanceData = {
        url: response.config.url,
        method: response.config.method?.toUpperCase(),
        responseTime,
        status: response.status,
        timestamp: Date.now()
      };

      // Store in sessionStorage for debug panel
      const existingData = JSON.parse(sessionStorage.getItem('api_performance') || '[]');
      existingData.push(performanceData);
      // Keep only last 100 entries
      if (existingData.length > 100) {
        existingData.shift();
      }
      sessionStorage.setItem('api_performance', JSON.stringify(existingData));
    }

    return response;
  },
  (error: AxiosError<ApiError>) => {
    // Calculate response time for failed requests
    const startTime = error.config?.metadata?.startTime;
    const responseTime = startTime ? Date.now() - startTime : 0;

    const isDebugMode = process.env.REACT_APP_DEBUG_MODE === 'true';
    const enableApiLogging = process.env.REACT_APP_ENABLE_API_LOGGING === 'true';

    // Enhanced error logging
    if (isDebugMode && enableApiLogging) {
      const requestId = error.config?.headers?.['X-Request-ID'];

      console.group(`❌ [API Error] ${error.response?.status || 'Network'} ${error.config?.method?.toUpperCase()} ${error.config?.url}`);
      console.log('📋 Request ID:', requestId);
      console.log('⏱️ Response Time:', `${responseTime}ms`);
      console.log('🔥 Error Type:', error.name);
      console.log('💬 Error Message:', error.message);
      if (error.response) {
        console.log('📊 Status:', error.response.status, error.response.statusText);
        console.log('📥 Response Headers:', error.response.headers);
        console.log('📦 Response Data:', error.response.data);
      }
      console.log('⏰ Timestamp:', new Date().toISOString());
      console.groupEnd();
    }

    // Store error data for debugging
    const errorData = {
      url: error.config?.url,
      method: error.config?.method?.toUpperCase(),
      status: error.response?.status,
      message: error.message,
      responseTime,
      timestamp: Date.now(),
      requestId: error.config?.headers?.['X-Request-ID']
    };

    const existingErrors = JSON.parse(sessionStorage.getItem('api_errors') || '[]');
    existingErrors.push(errorData);
    // Keep only last 50 errors
    if (existingErrors.length > 50) {
      existingErrors.shift();
    }
    sessionStorage.setItem('api_errors', JSON.stringify(existingErrors));

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

// ============ Project Report Analysis Endpoints ============

export const analyzeProjectReport = async (
  request: ReportAnalysisRequest
): Promise<ReportAnalysisResponse> => {
  const response = await apiClient.post<ReportAnalysisResponse>(
    `${API_V1_PREFIX}/report-analysis/analyze`,
    request
  );
  return response.data;
};

// 批量分析查重（增强版）
export const batchAnalyzePlagiarism = async (
  request: BatchAnalysisRequest
): Promise<BatchAnalysisResponse> => {
  const response = await apiClient.post<BatchAnalysisResponse>(
    `${API_V1_PREFIX}/assignments/plagiarism/batch-analyze`,
    request
  );
  return response.data;
};

// 获取原创性报告
export const getOriginalityReport = async (
  submissionId: string,
  assignmentId: string
): Promise<OriginalityReport> => {
  const response = await apiClient.get<OriginalityReport>(
    `${API_V1_PREFIX}/assignments/plagiarism/originality-report/${submissionId}`,
    { params: { assignment_id: assignmentId } }
  );
  return response.data;
};

// 获取查重设置
export const getPlagiarismSettings = async (): Promise<PlagiarismSettings> => {
  const response = await apiClient.get<PlagiarismSettings>(
    `${API_V1_PREFIX}/assignments/plagiarism/settings`
  );
  return response.data;
};

// 更新查重设置
export const updatePlagiarismSettings = async (
  settings: PlagiarismSettings
): Promise<PlagiarismSettings> => {
  const response = await apiClient.put<PlagiarismSettings>(
    `${API_V1_PREFIX}/assignments/plagiarism/settings`,
    settings
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

