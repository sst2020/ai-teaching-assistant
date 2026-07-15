import axios, { AxiosError, type AxiosInstance, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import type { User, LoginCredentials, RegisterData, Assignment, Submission, QAQuestion, StudentRecord, StudentRecordCreate, StudentRecordUpdate } from '@/types'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 30000
})

// Request interceptor - add auth token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    // Handle 401 - try to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      const refreshTokenValue = localStorage.getItem('refreshToken')

      if (refreshTokenValue) {
        try {
          const response = await authApi.refreshToken(refreshTokenValue)
          localStorage.setItem('token', response.access_token)

          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${response.access_token}`
          }
          return apiClient(originalRequest)
        } catch (refreshError) {
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  async login(credentials: LoginCredentials) {
    const response = await apiClient.post('/auth/login', {
      student_id: credentials.username,
      password: credentials.password
    })
    return response.data
  },

  async register(data: RegisterData) {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get('/auth/me')
    return response.data
  },

  async refreshToken(refreshToken: string) {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
    return response.data
  },

  async logout() {
    const response = await apiClient.post('/auth/logout')
    return response.data
  }
}

// Assignments API
export const assignmentsApi = {
  async getAll(signal?: AbortSignal) {
    const response = await apiClient.get('/assignments/', { signal })
    return response.data
  },

  async getById(id: string) {
    const response = await apiClient.get(`/assignments/${id}`)
    return response.data
  },

  async create(data: Partial<Assignment>) {
    const response = await apiClient.post('/assignments/', data)
    return response.data
  },

  async update(id: string, data: Partial<Assignment>) {
    const response = await apiClient.put(`/assignments/${id}`, data)
    return response.data
  },

  async delete(id: string) {
    const response = await apiClient.delete(`/assignments/${id}`)
    return response.data
  }
}

// Submissions API
export const submissionsApi = {
  async getStudentSubmissions(studentId: string) {
    const response = await apiClient.get(`/submissions/student/${studentId}`)
    return response.data
  },

  async getByAssignment(assignmentId: string) {
    const response = await apiClient.get(`/submissions/assignment/${assignmentId}`)
    return response.data
  },

  async create(data: { student_id: string; assignment_id: string; content?: string }) {
    const response = await apiClient.post('/submissions', data)
    return response.data
  }
}

// QA API
export const qaApi = {
  async askQuestion(question: string, studentId: string = 'anonymous', courseId: string = 'general') {
    const response = await apiClient.post('/qa/ask', {
      student_id: studentId,
      course_id: courseId,
      question
    })
    return response.data
  },

  /**
   * 流式问答 — 返回 EventSource 式的 ReadableStream
   * 调用方通过 onChunk 回调逐步接收文本片段
   */
  askStream(
    question: string,
    options: {
      studentId?: string
      courseId?: string
      onChunk: (text: string) => void
      onDone?: (meta: { confidence: number; needs_review: boolean }) => void
      onError?: (msg: string) => void
    }
  ): AbortController {
    const controller = new AbortController()
    const baseURL = apiClient.defaults.baseURL || '/api/v1'
    const token = localStorage.getItem('token')

    fetch(`${baseURL}/qa/ask-stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        student_id: options.studentId || 'anonymous',
        course_id: options.courseId || 'general',
        question
      }),
      signal: controller.signal
    })
      .then(async (res) => {
        if (!res.ok || !res.body) {
          options.onError?.(`HTTP ${res.status}`)
          return
        }
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buffer = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })

          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'chunk') {
                options.onChunk(data.content)
              } else if (data.type === 'done') {
                options.onDone?.({ confidence: data.confidence, needs_review: data.needs_review })
              } else if (data.type === 'error') {
                options.onError?.(data.message)
              }
            } catch { /* skip malformed */ }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          options.onError?.(err.message)
        }
      })

    return controller
  },

  async getQuestions(): Promise<QAQuestion[]> {
    const response = await apiClient.get('/qa/pending-questions')
    return response.data
  },

  async getKnowledgeBase(category?: string) {
    const response = await apiClient.get('/knowledge-base', {
      params: { category }
    })
    return (response.data as { entries: unknown[] }).entries ?? response.data
  }
}

// Analysis API
export const analysisApi = {
  async analyzeCode(code: string, language: string) {
    const response = await apiClient.post('/analysis/analyze', {
      code,
      language,
      include_suggestions: true,
    })
    return response.data
  },

  async checkPlagiarism(submissionId: string) {
    const response = await apiClient.post('/assignments/plagiarism/check', {
      submission_id: submissionId,
    })
    return response.data
  },

  async analyzeReport(file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const response = await apiClient.post('/report-analysis/analyze-file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data
  }
}

// Grading API
export const gradingApi = {
  async getByAssignment(assignmentId: string) {
    const response = await apiClient.get(`/grading/assignment/${assignmentId}`)
    return response.data
  },

  async gradeSubmission(submissionId: number, feedback: Record<string, any>, overallScore: number) {
    const response = await apiClient.post('/grading', {
      submission_id: submissionId,
      overall_score: overallScore,
      feedback,
      graded_by: 'teacher',
    })
    return response.data
  },

  async autoGrade(submissionId: number) {
    const response = await apiClient.post('/grading', {
      submission_id: submissionId,
      overall_score: 0,
      graded_by: 'AI',
    })
    return response.data
  }
}

// Task Queue API (for RabbitMQ integration)
export const tasksApi = {
  async getTaskStatus(taskId: string) {
    const response = await apiClient.get(`/tasks/status/${taskId}`)
    return response.data
  },

  async submitBatchTask(type: string, data: any) {
    const response = await apiClient.post('/tasks/batch', { type, data })
    return response.data
  }
}

// Student Records API
export const studentRecordsApi = {
  async getAll(params?: { page?: number; page_size?: number; assignment_number?: string }) {
    const response = await apiClient.get('/student-records', { params })
    return response.data
  },

  async getByStudentId(studentId: string): Promise<StudentRecord> {
    const response = await apiClient.get(`/student-records/${studentId}`)
    return response.data
  },

  async create(data: StudentRecordCreate): Promise<StudentRecord> {
    const response = await apiClient.post('/student-records', data)
    return response.data
  },

  async update(studentId: string, data: StudentRecordUpdate): Promise<StudentRecord> {
    const response = await apiClient.put(`/student-records/${studentId}`, data)
    return response.data
  },

  async delete(studentId: string) {
    const response = await apiClient.delete(`/student-records/${studentId}`)
    return response.data
  }
}

export default apiClient
