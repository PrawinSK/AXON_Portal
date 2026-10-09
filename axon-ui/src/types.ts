export type ThemeMode = 'light' | 'dark';

export type UserRole = 'student' | 'staff' | 'hod';

export type AppTab = 'interview' | 'my-tasks' | 'students' | 'tasks' | 'hod' | 'mcq-verify';

export interface AuthUser {
  user_id: string;
  name: string;
  role: UserRole;
  department: string;
  roll_number?: string;
  email?: string;
  access_token: string;
}

export interface TaskItem {
  id: string;
  student_id: string;
  student_name: string;
  assigned_by_name: string;
  assigned_by_role: string;
  target_skill: string;
  description: string;
  status: 'assigned' | 'in_progress' | 'completed';
  due_date?: string;
  created_at: string;
}

export interface DepartmentStudentProfile {
  id: string;
  name: string;
  roll_number: string;
  department: string;
  email?: string;
  metrics: {
    overall_score: number;
    readiness_band: string;
    radar: {
      depth: number;
      logic: number;
      communication: number;
    };
    weak_skills: string[];
    interviews_completed: number;
  };
  tasks_count: number;
  pending_tasks_count: number;
}

export interface StaffProfile {
  id: string;
  name: string;
  email: string;
  department: string;
  role: string;
}

export interface UploadResponse {
  candidate_id: string;
  message: string;
  chunks_created: number;
  sections_found: string[];
}

export interface StartInterviewRequest {
  candidate_id: string;
  student_name: string;
  mode: 'practice' | 'graded';
  role_track: string;
  target_skill?: string;
  max_questions: number;
}

export interface StartInterviewResponse {
  session_id: string;
  mode: 'practice' | 'graded';
  status: string;
  current_turn: number;
  max_questions: number;
  first_question: string;
  based_on_topic: string;
}

export interface TurnEvaluation {
  score: number;
  technical_accuracy: string;
  areas_for_improvement: string;
  feedback: string;
  difficulty_level: number;
}

export interface SubmitAnswerResponse {
  session_id: string;
  turn_completed: number;
  max_questions: number;
  is_completed: boolean;
  evaluation?: TurnEvaluation;
  next_question?: string;
}

export interface SessionHistoryItem {
  turn: number;
  question: string;
  answer?: string;
  evaluation?: TurnEvaluation;
  difficulty_level: number;
}

export interface InterviewStateResponse {
  session_id: string;
  candidate_id: string;
  student_name: string;
  mode: 'practice' | 'graded';
  status: string;
  current_turn: number;
  max_questions: number;
  difficulty_level: number;
  history: SessionHistoryItem[];
}

export interface RoadmapItem {
  week: number;
  focus: string;
  action_items: string[];
}

export interface SynthesisResponse {
  session_id: string;
  mode: 'practice' | 'graded';
  overall_score: number;
  technical_depth: number;
  logical_reasoning: number;
  communication_clarity: number;
  domain_scores: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  roadmap: RoadmapItem[];
  tasks_auto_closed: string[];
}

// --- MCQ Assessment Interfaces ---

export interface MCQChoice {
  label: string;
  text: string;
}

export interface MCQQuestion {
  id: string;
  question: string;
  choices: MCQChoice[];
  topic: string;
}

export interface MCQSessionStartResponse {
  session_id: string;
  student_id: string;
  student_name: string;
  status: string;
  strikes: number;
  total_questions: number;
  questions: MCQQuestion[];
}

export interface MCQStrikeResponse {
  session_id: string;
  strikes: number;
  is_disqualified: boolean;
  status: string;
  message: string;
}

export interface MCQQuestionBreakdown {
  question_id: string;
  question_text: string;
  selected_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
}

export interface MCQSubmitResponse {
  session_id: string;
  student_id: string;
  student_name: string;
  status: string;
  score: number;
  total_questions: number;
  percentage: number;
  passed: boolean;
  strikes: number;
  completed_at: string;
  breakdown: MCQQuestionBreakdown[];
}

export interface MCQResultSummary {
  session_id: string;
  student_id: string;
  student_name: string;
  status: string;
  strikes: number;
  score: number;
  total_questions: number;
  percentage: number;
  passed: boolean;
  created_at: string;
  completed_at?: string;
}

export interface BulkUploadResult {
  total_extracted: number;
  added_count: number;
  skipped_count: number;
  errors_count: number;
  added_students: any[];
  skipped: any[];
  errors: any[];
}

export interface MCQUploadResult {
  status: string;
  uploaded_file: string;
  batch_id?: string;
  upload_time?: string;
  questions_parsed: number;
  questions_inserted: number;
  total_pool_count: number;
  approved_pool_count?: number;
}

export interface MCQAdminQuestion {
  id: string;
  question_text: string;
  options: string[];
  correct_answer: string;
  explanation: string;
  topic: string;
  source: string;
  upload_batch_id: string;
  upload_time: string;
  is_approved: boolean;
  created_at: string;
}

export interface MCQUploadBatch {
  batch_id: string;
  source: string;
  upload_time: string;
  total_questions: number;
  approved_count: number;
}
