import type {
  UploadResponse,
  StartInterviewRequest,
  StartInterviewResponse,
  SubmitAnswerResponse,
  InterviewStateResponse,
  SynthesisResponse,
  AuthUser,
  TaskItem,
  DepartmentStudentProfile,
  MCQSessionStartResponse,
  MCQStrikeResponse,
  MCQSubmitResponse,
  MCQResultSummary,
  BulkUploadResult,
  MCQUploadResult,
  MCQAdminQuestion,
  MCQUploadBatch,
} from '../types';

const getBaseUrl = (): string => {
  if (typeof window !== 'undefined') {
    const stored = localStorage.getItem('axon_api_url');
    if (stored && stored.trim()) {
      return stored.trim().replace(/\/+$/, '');
    }
  }
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl && envUrl.trim()) {
    return envUrl.trim().replace(/\/+$/, '');
  }
  if (typeof window !== 'undefined') {
    // If hosted together on port 8000 or on Render, use the same origin automatically
    if (window.location.port === '8000' || window.location.hostname.includes('onrender.com')) {
      return window.location.origin;
    }
  }
  return 'http://127.0.0.1:8000';
};


class ApiService {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('axon_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('axon_token', token);
    } else {
      localStorage.removeItem('axon_token');
    }
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem('axon_token');
    }
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const baseUrl = getBaseUrl();
    const url = `${baseUrl}${endpoint}`;
    const token = this.getToken();
    
    const headers: Record<string, string> = {
      ...(options.headers as Record<string, string> || {}),
    };

    if (token && !headers['Authorization']) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.error) {
          errorMessage = typeof errorData.error === 'string' ? errorData.error : JSON.stringify(errorData.error);
        } else if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        }
      } catch {
        // fallback
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  async checkBackendHealth(): Promise<{ message: string; status: string; pool_capacity?: string }> {
    return this.request('/');
  }

  // --- Authentication Endpoints ---

  async loginStudent(rollNumber: string, password: string): Promise<AuthUser> {
    const res = await this.request<AuthUser>('/auth/student/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ roll_number: rollNumber, password }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async loginStaff(email: string, password: string): Promise<AuthUser> {
    const res = await this.request<AuthUser>('/auth/staff/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async loginHOD(email: string, password: string): Promise<AuthUser> {
    const res = await this.request<AuthUser>('/auth/hod/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<any> {
    return this.request('/auth/me');
  }

  async createStudent(payload: {
    roll_number: string;
    name: string;
    password: string;
    department?: string;
    email?: string;
  }): Promise<any> {
    return this.request('/auth/students/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async createStaff(payload: {
    name: string;
    email: string;
    password: string;
    department?: string;
  }): Promise<any> {
    return this.request('/auth/staff/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async getAllStaff(): Promise<any[]> {
    return this.request<any[]>('/auth/staff/all');
  }

  logout() {
    this.setToken(null);
  }

  // --- Task & Student Management Endpoints ---

  async getMyTasks(): Promise<TaskItem[]> {
    return this.request<TaskItem[]>('/tasks/my-tasks');
  }

  async getAllTasks(): Promise<TaskItem[]> {
    return this.request<TaskItem[]>('/tasks/all');
  }

  async assignTask(payload: {
    student_id: string;
    target_skill: string;
    description: string;
    due_date?: string;
  }): Promise<TaskItem> {
    return this.request<TaskItem>('/tasks/assign', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async getDepartmentStudents(): Promise<DepartmentStudentProfile[]> {
    return this.request<DepartmentStudentProfile[]>('/tasks/students');
  }

  // --- Resume & Interview Endpoints ---

  async uploadResume(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.request('/resume/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async startInterview(payload: StartInterviewRequest): Promise<StartInterviewResponse> {
    return this.request('/interview/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async submitAnswer(sessionId: string, answer: string): Promise<SubmitAnswerResponse> {
    return this.request(`/interview/${sessionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer }),
    });
  }

  async getInterviewState(sessionId: string): Promise<InterviewStateResponse> {
    return this.request(`/interview/${sessionId}/state`);
  }

  async concludeInterview(sessionId: string): Promise<SynthesisResponse> {
    return this.request(`/interview/${sessionId}/conclude`, {
      method: 'POST',
    });
  }

  // --- Bulk Student & Roster Management ---

  async bulkUploadStudents(file: File): Promise<BulkUploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/auth/students/bulk-upload', {
      method: 'POST',
      body: formData,
    });
  }

  async cleanupStudents(): Promise<{ status: string; message: string }> {
    return this.request('/auth/students/cleanup', {
      method: 'POST',
    });
  }

  // --- MCQ Assessment Proctored Endpoints ---

  async uploadMCQBank(file: File): Promise<MCQUploadResult> {
    const formData = new FormData();
    formData.append('file', file);
    return this.request('/mcq/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async startMCQSession(): Promise<MCQSessionStartResponse> {
    return this.request('/mcq/session/start', {
      method: 'POST',
    });
  }

  async recordMCQStrike(sessionId: string): Promise<MCQStrikeResponse> {
    return this.request(`/mcq/session/${sessionId}/strike`, {
      method: 'POST',
    });
  }

  async submitMCQAnswers(sessionId: string, answers: Record<string, string>): Promise<MCQSubmitResponse> {
    return this.request(`/mcq/session/${sessionId}/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answers }),
    });
  }

  async getAllMCQResults(): Promise<MCQResultSummary[]> {
    return this.request<MCQResultSummary[]>('/mcq/results/all');
  }

  async getMyMCQResults(): Promise<MCQResultSummary[]> {
    return this.request<MCQResultSummary[]>('/mcq/results/my');
  }

  // --- MCQ Question Verification & Batch Management (Staff & HOD) ---

  async getMCQAdminQuestions(batchId: string = 'all', approvalStatus: string = 'all'): Promise<MCQAdminQuestion[]> {
    return this.request<MCQAdminQuestion[]>(`/mcq/questions?batch_id=${encodeURIComponent(batchId)}&approval_status=${encodeURIComponent(approvalStatus)}`);
  }

  async getMCQBatches(): Promise<MCQUploadBatch[]> {
    return this.request<MCQUploadBatch[]>('/mcq/batches');
  }

  async updateMCQQuestion(
    questionId: string,
    payload: {
      question_text: string;
      options: string[];
      correct_answer: string;
      explanation?: string;
      topic?: string;
      is_approved?: boolean;
    }
  ): Promise<MCQAdminQuestion> {
    return this.request<MCQAdminQuestion>(`/mcq/questions/${encodeURIComponent(questionId)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  }

  async toggleMCQApproval(questionId: string, isApproved: boolean): Promise<{ id: string; is_approved: boolean }> {
    return this.request(`/mcq/questions/${encodeURIComponent(questionId)}/approve`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_approved: isApproved }),
    });
  }

  async deleteMCQQuestion(questionId: string): Promise<{ status: string; message: string }> {
    return this.request(`/mcq/questions/${encodeURIComponent(questionId)}`, {
      method: 'DELETE',
    });
  }

  async deleteMCQBatch(batchId: string): Promise<{ status: string; deleted_count: number; message: string }> {
    return this.request(`/mcq/batches/${encodeURIComponent(batchId)}`, {
      method: 'DELETE',
    });
  }
}

export const api = new ApiService();
