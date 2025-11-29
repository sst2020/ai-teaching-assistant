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

// Export the axios instance for custom requests
export default apiClient;

