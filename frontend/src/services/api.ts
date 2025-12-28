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
  QALogCreate,
  QALogResponse,
  QALogStats,
  QAAnalyticsReport,
  StudentWeaknessReport,
} from '../types/api';
import {
  LoginCredentials,
  RegisterData,
  LoginResponse,
  RegisterResponse,
  User,
  RefreshTokenResponse,
  ChangePasswordResponse,
  RevokeAllTokensResponse,
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
  PlagiarismSettings,
} from '../types/plagiarism';
import {
  ReportAnalysisRequest,
  ReportAnalysisResponse,
} from '../types/reportAnalysis';
import {
  KnowledgeBaseEntry,
  KnowledgeBaseCreateRequest,
  KnowledgeBaseUpdateRequest,
  KnowledgeBaseSearchRequest,
  KnowledgeBaseSearchResponse,
  KnowledgeBaseListResponse,
  KnowledgeBaseStats,
  CategoriesResponse,
} from '../types/knowledgeBase';
import {
  TriageRequest,
  TriageResponse,
  PendingQueueResponse,
  TeacherTakeoverRequest,
  TeacherAnswerRequest,
  TeacherAnswerResponse,
  TriageStats,
  DifficultyLevelsResponse,
} from '../types/triage';
import {
  GradingResultCreate,
  GradingResultResponse,
  GradingResultWithSubmission,
  GradingResultListResponse,
  GradingResultOverride,
  GradingStatistics,
} from '../types/grading';

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
      try {
        const rawData = sessionStorage.getItem('api_performance');
        const existingData = rawData ? JSON.parse(rawData) : [];
        existingData.push(performanceData);
        // Keep only last 100 entries
        if (existingData.length > 100) {
          existingData.shift();
        }
        sessionStorage.setItem('api_performance', JSON.stringify(existingData));
      } catch (parseError) {
        console.warn('[API] Failed to parse performance data, resetting:', parseError);
        sessionStorage.setItem('api_performance', JSON.stringify([performanceData]));
      }
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

    try {
      const rawErrors = sessionStorage.getItem('api_errors');
      const existingErrors = rawErrors ? JSON.parse(rawErrors) : [];
      existingErrors.push(errorData);
      // Keep only last 50 errors
      if (existingErrors.length > 50) {
        existingErrors.shift();
      }
      sessionStorage.setItem('api_errors', JSON.stringify(existingErrors));
    } catch (parseError) {
      console.warn('[API] Failed to parse error data, resetting:', parseError);
      sessionStorage.setItem('api_errors', JSON.stringify([errorData]));
    }

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

// 智能问答（持久化版本）
export const smartAskQuestion = async (request: QALogCreate): Promise<QALogResponse> => {
  const response = await apiClient.post<QALogResponse>(
    `${API_V1_PREFIX}/qa/smart-ask`,
    request
  );
  return response.data;
};

// 获取 Q&A 统计信息
export const getQAStats = async (): Promise<QALogStats> => {
  const response = await apiClient.get<QALogStats>(
    `${API_V1_PREFIX}/qa/stats`
  );
  return response.data;
};

// 获取学生问答历史
export const getStudentQAHistory = async (
  studentId: string,
  limit: number = 50
): Promise<QALogResponse[]> => {
  const response = await apiClient.get<QALogResponse[]>(
    `${API_V1_PREFIX}/qa/history/${studentId}`,
    { params: { limit } }
  );
  return response.data;
};

// 获取学生知识薄弱点报告
export const getStudentWeaknessReport = async (
  studentId: string
): Promise<StudentWeaknessReport> => {
  const response = await apiClient.get<StudentWeaknessReport>(
    `${API_V1_PREFIX}/qa/weakness/${studentId}`
  );
  return response.data;
};

// 获取课程 Q&A 分析报告
export const getCourseQAAnalytics = async (
  courseId: string,
  days: number = 30
): Promise<QAAnalyticsReport> => {
  const response = await apiClient.get<QAAnalyticsReport>(
    `${API_V1_PREFIX}/qa/analytics/${courseId}`,
    { params: { days } }
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
    `${API_V1_PREFIX}/analysis/report/analyze`,
    request
  );
  return response.data;
};

// 获取支持的报告文件类型
export const getReportFileTypes = async (): Promise<{
  file_types: string[];
  languages: string[];
  reference_formats: string[];
}> => {
  const response = await apiClient.get(
    `${API_V1_PREFIX}/analysis/report/file-types`
  );
  return response.data;
};

// 批量分析项目报告
export const batchAnalyzeReports = async (
  requests: ReportAnalysisRequest[]
): Promise<{
  total: number;
  successful_count: number;
  failed_count: number;
  results: ReportAnalysisResponse[];
  errors: Array<{ file_name: string; error: string }>;
}> => {
  const response = await apiClient.post(
    `${API_V1_PREFIX}/analysis/report/batch-analyze`,
    requests
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

export const refreshToken = async (refresh_token: string): Promise<RefreshTokenResponse> => {
  const response = await apiClient.post<RefreshTokenResponse>(
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

export const changePassword = async (
  oldPassword: string,
  newPassword: string
): Promise<ChangePasswordResponse> => {
  const response = await apiClient.post<ChangePasswordResponse>(
    `${API_V1_PREFIX}/auth/change-password`,
    {
      old_password: oldPassword,
      new_password: newPassword,
    }
  );
  return response.data;
};

export const revokeAllTokens = async (): Promise<RevokeAllTokensResponse> => {
  const response = await apiClient.post<RevokeAllTokensResponse>(
    `${API_V1_PREFIX}/auth/revoke-all`
  );
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

// ============ Knowledge Base Endpoints ============

export const getKnowledgeBaseEntries = async (
  page: number = 1,
  pageSize: number = 20,
  category?: string,
  difficultyLevel?: number
): Promise<KnowledgeBaseListResponse> => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());
  if (category) params.append('category', category);
  if (difficultyLevel) params.append('difficulty_level', difficultyLevel.toString());

  const response = await apiClient.get<KnowledgeBaseListResponse>(
    `${API_V1_PREFIX}/knowledge-base?${params.toString()}`
  );
  return response.data;
};

export const getKnowledgeBaseEntry = async (entryId: string): Promise<KnowledgeBaseEntry> => {
  const response = await apiClient.get<KnowledgeBaseEntry>(
    `${API_V1_PREFIX}/knowledge-base/${entryId}`
  );
  return response.data;
};

export const createKnowledgeBaseEntry = async (
  data: KnowledgeBaseCreateRequest
): Promise<KnowledgeBaseEntry> => {
  const response = await apiClient.post<KnowledgeBaseEntry>(
    `${API_V1_PREFIX}/knowledge-base`,
    data
  );
  return response.data;
};

export const updateKnowledgeBaseEntry = async (
  entryId: string,
  data: KnowledgeBaseUpdateRequest
): Promise<KnowledgeBaseEntry> => {
  const response = await apiClient.put<KnowledgeBaseEntry>(
    `${API_V1_PREFIX}/knowledge-base/${entryId}`,
    data
  );
  return response.data;
};

export const deleteKnowledgeBaseEntry = async (entryId: string): Promise<void> => {
  await apiClient.delete(`${API_V1_PREFIX}/knowledge-base/${entryId}`);
};

export const searchKnowledgeBase = async (
  request: KnowledgeBaseSearchRequest
): Promise<KnowledgeBaseSearchResponse> => {
  const response = await apiClient.post<KnowledgeBaseSearchResponse>(
    `${API_V1_PREFIX}/knowledge-base/search`,
    request
  );
  return response.data;
};

export const getKnowledgeBaseCategories = async (): Promise<CategoriesResponse> => {
  const response = await apiClient.get<CategoriesResponse>(
    `${API_V1_PREFIX}/knowledge-base/categories/list`
  );
  return response.data;
};

export const getKnowledgeBaseStats = async (): Promise<KnowledgeBaseStats> => {
  const response = await apiClient.get<KnowledgeBaseStats>(
    `${API_V1_PREFIX}/knowledge-base/stats/overview`
  );
  return response.data;
};

export const markKnowledgeBaseEntryHelpful = async (entryId: string): Promise<void> => {
  await apiClient.post(`${API_V1_PREFIX}/knowledge-base/${entryId}/helpful`);
};

// ============ Triage Endpoints ============

export const askTriageQuestion = async (request: TriageRequest): Promise<TriageResponse> => {
  const response = await apiClient.post<TriageResponse>(
    `${API_V1_PREFIX}/triage/ask`,
    request
  );
  return response.data;
};

export const getPendingQueue = async (
  role?: string,
  handlerId?: string,
  page: number = 1,
  pageSize: number = 20
): Promise<PendingQueueResponse> => {
  const params = new URLSearchParams();
  if (role) params.append('role', role);
  if (handlerId) params.append('handler_id', handlerId);
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());

  const response = await apiClient.get<PendingQueueResponse>(
    `${API_V1_PREFIX}/triage/queue?${params.toString()}`
  );
  return response.data;
};

export const teacherTakeover = async (
  request: TeacherTakeoverRequest
): Promise<{ message: string; log_id: string }> => {
  const response = await apiClient.post<{ message: string; log_id: string }>(
    `${API_V1_PREFIX}/triage/takeover`,
    request
  );
  return response.data;
};

export const teacherAnswer = async (
  request: TeacherAnswerRequest
): Promise<TeacherAnswerResponse> => {
  const response = await apiClient.post<TeacherAnswerResponse>(
    `${API_V1_PREFIX}/triage/answer`,
    request
  );
  return response.data;
};

export const getTriageStats = async (): Promise<TriageStats> => {
  const response = await apiClient.get<TriageStats>(
    `${API_V1_PREFIX}/triage/stats`
  );
  return response.data;
};

export const getDifficultyLevels = async (): Promise<DifficultyLevelsResponse> => {
  const response = await apiClient.get<DifficultyLevelsResponse>(
    `${API_V1_PREFIX}/triage/difficulty-levels`
  );
  return response.data;
};

// ============ Grading Result Endpoints ============

// 创建评分结果
export const createGradingResult = async (
  data: GradingResultCreate
): Promise<GradingResultResponse> => {
  const response = await apiClient.post<GradingResultResponse>(
    `${API_V1_PREFIX}/grading`,
    data
  );
  return response.data;
};

// 获取单个评分结果（包含提交详情）
export const getGradingResult = async (
  gradingId: number
): Promise<GradingResultWithSubmission> => {
  const response = await apiClient.get<GradingResultWithSubmission>(
    `${API_V1_PREFIX}/grading/${gradingId}`
  );
  return response.data;
};

// 按提交 ID 获取评分结果
export const getGradingBySubmission = async (
  submissionId: number
): Promise<GradingResultResponse> => {
  const response = await apiClient.get<GradingResultResponse>(
    `${API_V1_PREFIX}/grading/submission/${submissionId}`
  );
  return response.data;
};

// 按学生 ID 获取评分结果列表
export const getGradingByStudent = async (
  studentId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<GradingResultListResponse> => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());

  const response = await apiClient.get<GradingResultListResponse>(
    `${API_V1_PREFIX}/grading/student/${studentId}?${params.toString()}`
  );
  return response.data;
};

// 按作业 ID 获取评分结果列表
export const getGradingByAssignment = async (
  assignmentId: string,
  page: number = 1,
  pageSize: number = 20
): Promise<GradingResultListResponse> => {
  const params = new URLSearchParams();
  params.append('page', page.toString());
  params.append('page_size', pageSize.toString());

  const response = await apiClient.get<GradingResultListResponse>(
    `${API_V1_PREFIX}/grading/assignment/${assignmentId}?${params.toString()}`
  );
  return response.data;
};

// 获取作业评分统计
export const getGradingStatistics = async (
  assignmentId: string
): Promise<GradingStatistics> => {
  const response = await apiClient.get<GradingStatistics>(
    `${API_V1_PREFIX}/grading/assignment/${assignmentId}/statistics`
  );
  return response.data;
};

// 教师覆盖评分
export const overrideGradingResult = async (
  gradingId: number,
  data: GradingResultOverride
): Promise<GradingResultResponse> => {
  const response = await apiClient.put<GradingResultResponse>(
    `${API_V1_PREFIX}/grading/${gradingId}/override`,
    data
  );
  return response.data;
};

// 删除评分结果
export const deleteGradingResult = async (gradingId: number): Promise<void> => {
  await apiClient.delete(`${API_V1_PREFIX}/grading/${gradingId}`);
};

// Export the axios instance for custom requests
export default apiClient;
