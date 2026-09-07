import React, { useState } from 'react';
import {
  UploadCloud,
  CheckCircle2,
  AlertCircle,
  Play,
  Layers,
  Sparkles,
  BookOpen,
  Award
} from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import type { StartInterviewResponse, UploadResponse } from '../types';

interface SetupScreenProps {
  onInterviewStarted: (session: StartInterviewResponse, candidateName: string) => void;
  initialTargetSkill?: string;
}

export const SetupScreen: React.FC<SetupScreenProps> = ({ onInterviewStarted, initialTargetSkill }) => {
  const { user } = useAuth();
  const [studentName, setStudentName] = useState(user?.name || 'Arjun Kumar');
  const [rollNumber, setRollNumber] = useState(user?.roll_number || '21CS042');
  const [roleTrack, setRoleTrack] = useState('Backend Systems Engineer');
  const [mode, setMode] = useState<'practice' | 'graded'>(initialTargetSkill ? 'graded' : 'practice');
  const [targetSkill, setTargetSkill] = useState(initialTargetSkill || 'Redis Caching & Invalidation');
  const [maxQuestions, setMaxQuestions] = useState(3); // default 3 for quick demo, configurable up to 25

  // File Upload State
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [candidateId, setCandidateId] = useState<string>('candidate123');

  // Start Session State
  const [isStarting, setIsStarting] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF resume files are accepted.');
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const res = await api.uploadResume(file);
      setUploadResult(res);
      setCandidateId(res.candidate_id);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to parse resume PDF.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleStartInterview = async () => {
    if (!studentName.trim()) {
      setStartError('Please enter your full student name.');
      return;
    }

    setIsStarting(true);
    setStartError(null);

    try {
      const res = await api.startInterview({
        candidate_id: candidateId,
        student_name: studentName,
        mode,
        role_track: roleTrack,
        target_skill: targetSkill.trim() || undefined,
        max_questions: maxQuestions,
      });

      onInterviewStarted(res, studentName);
    } catch (err: any) {
      setStartError(err.message || 'Could not initialize interview session.');
    } finally {
      setIsStarting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      {/* Header Banner */}
      <div className="text-center mb-10">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/60 dark:text-cyan-300 border border-blue-200 dark:border-blue-900/60 text-xs font-semibold mb-4">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Resume-Grounded & Adaptive AI Recruiter</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 dark:text-white tracking-tight">
          AI Technical Interview Portal
        </h1>
        <p className="mt-2 text-sm sm:text-base text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
          Experience realistic, adaptive technical interviews grounded in your actual projects, skills, and coursework.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        
        {/* Left Column: Candidate & Setup */}
        <div className="md:col-span-7 space-y-6">
          
          {/* Identity Card */}
          <div className="p-6 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4">
              <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-cyan-400 flex items-center justify-center text-xs font-black">1</span>
              <span>Student Profile</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Full Name
                </label>
                <input
                  type="text"
                  value={studentName}
                  onChange={(e) => setStudentName(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl text-sm bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  placeholder="e.g. Arjun Kumar"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  ERP Roll Number
                </label>
                <input
                  type="text"
                  value={rollNumber}
                  onChange={(e) => setRollNumber(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl text-sm bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  placeholder="e.g. 21CS042"
                />
              </div>
            </div>
          </div>

          {/* Mode Selection */}
          <div className="p-6 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4">
              <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-cyan-400 flex items-center justify-center text-xs font-black">2</span>
              <span>Interview Mode</span>
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setMode('practice')}
                className={`p-4 rounded-xl border text-left transition-all ${
                  mode === 'practice'
                    ? 'border-blue-600 bg-blue-50/50 dark:border-cyan-500/80 dark:bg-blue-950/30 ring-2 ring-blue-500/20'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 text-blue-600 dark:text-cyan-400 font-bold text-sm">
                  <BookOpen className="w-4 h-4" />
                  <span>Practice Mode</span>
                </div>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  Zero stakes, instant answer coaching & feedback per turn. Does not affect official scorecard.
                </p>
              </button>

              <button
                type="button"
                onClick={() => setMode('graded')}
                className={`p-4 rounded-xl border text-left transition-all ${
                  mode === 'graded'
                    ? 'border-blue-600 bg-blue-50/50 dark:border-cyan-500/80 dark:bg-blue-950/30 ring-2 ring-blue-500/20'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700'
                }`}
              >
                <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 font-bold text-sm">
                  <Award className="w-4 h-4" />
                  <span>Graded Mode</span>
                </div>
                <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                  Official proctored evaluation. Updates HOD heatmap & auto-closes assigned remediation tasks.
                </p>
              </button>
            </div>
          </div>

          {/* Role Track & Focus */}
          <div className="p-6 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-4">
              <span className="w-6 h-6 rounded-lg bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-cyan-400 flex items-center justify-center text-xs font-black">3</span>
              <span>Role Track & Remediation</span>
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Target Technical Role
                </label>
                <select
                  value={roleTrack}
                  onChange={(e) => setRoleTrack(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl text-sm bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                >
                  <option value="Backend Systems Engineer">Backend Systems Engineer (Python / FastAPI / Go)</option>
                  <option value="Fullstack Web Developer">Fullstack Web Developer (Next.js / React / Node)</option>
                  <option value="AI & Machine Learning Engineer">AI & Machine Learning Engineer (LLMs / PyTorch)</option>
                  <option value="Cloud & DevOps Architect">Cloud & DevOps Architect (Docker / K8s / AWS)</option>
                  <option value="Data Engineer">Data Engineer (PostgreSQL / Spark / Kafka)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Target Remediation Skill (Optional)
                </label>
                <input
                  type="text"
                  value={targetSkill}
                  onChange={(e) => setTargetSkill(e.target.value)}
                  className="w-full px-3.5 py-2 rounded-xl text-sm bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  placeholder="e.g. Redis Caching, System Design, SQL Joins"
                />
                <p className="text-[11px] text-slate-400 mt-1">
                  Assigned by staff/HOD. In Graded mode, scoring $\ge 7.0$ on this skill auto-closes the task.
                </p>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="text-xs font-medium text-slate-600 dark:text-slate-400">
                    Interview Length
                  </label>
                  <span className="text-xs font-bold text-blue-600 dark:text-cyan-400">
                    {maxQuestions} Questions
                  </span>
                </div>
                <input
                  type="range"
                  min={2}
                  max={25}
                  value={maxQuestions}
                  onChange={(e) => setMaxQuestions(Number(e.target.value))}
                  className="w-full h-2 bg-slate-200 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-600 dark:accent-cyan-400"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                  <span>2 (Quick Test)</span>
                  <span>10 (Standard)</span>
                  <span>25 (Comprehensive)</span>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* Right Column: Resume Uploader & Summary */}
        <div className="md:col-span-5 space-y-6">
          
          {/* Resume Upload Box */}
          <div className="p-6 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm">
            <h3 className="text-base font-bold text-slate-900 dark:text-white flex items-center space-x-2 mb-2">
              <UploadCloud className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
              <span>Resume Ingestion</span>
            </h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">
              Upload candidate PDF. The parser breaks it into sections and creates dense vector chunks in ChromaDB.
            </p>

            <label className="border-2 border-dashed border-slate-300 dark:border-blue-950 hover:border-blue-500 dark:hover:border-cyan-500 rounded-2xl p-6 flex flex-col items-center justify-center cursor-pointer transition-colors bg-slate-50/50 dark:bg-slate-900/40">
              <UploadCloud className={`w-10 h-10 mb-2 ${isUploading ? 'animate-bounce text-blue-500' : 'text-slate-400 dark:text-slate-600'}`} />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                {isUploading ? 'Parsing & Vectorizing...' : 'Click to Upload Resume (PDF)'}
              </span>
              <span className="text-[10px] text-slate-400 mt-1">Max 10MB</span>
              <input
                type="file"
                accept=".pdf"
                onChange={handleFileUpload}
                disabled={isUploading}
                className="hidden"
              />
            </label>

            {uploadError && (
              <div className="mt-3 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{uploadError}</span>
              </div>
            )}

            {uploadResult && (
              <div className="mt-4 p-4 rounded-xl bg-emerald-50 dark:bg-emerald-950/30 border border-emerald-200 dark:border-emerald-900">
                <div className="flex items-center space-x-2 text-emerald-700 dark:text-emerald-400 text-xs font-bold mb-2">
                  <CheckCircle2 className="w-4 h-4" />
                  <span>Resume Ingested Successfully</span>
                </div>
                <div className="text-[11px] text-slate-600 dark:text-slate-300 space-y-1">
                  <div>Chunks Stored: <span className="font-semibold text-slate-900 dark:text-white">{uploadResult.chunks_created}</span></div>
                  <div>Candidate ID: <code className="text-[10px] bg-slate-200/60 dark:bg-slate-800 px-1 py-0.5 rounded">{uploadResult.candidate_id.slice(0, 12)}...</code></div>
                </div>
                <div className="mt-2.5 flex flex-wrap gap-1">
                  {uploadResult.sections_found.map((sec) => (
                    <span key={sec} className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-300">
                      {sec}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {!uploadResult && !isUploading && (
              <div className="mt-3 text-[11px] text-slate-400 text-center">
                * If no resume is uploaded, Axon will use standard technical context.
              </div>
            )}
          </div>

          {/* Launch Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white shadow-lg shadow-blue-500/20">
            <div className="flex items-center space-x-2 text-cyan-200 text-xs font-bold uppercase tracking-wider mb-2">
              <Layers className="w-4 h-4" />
              <span>Ready for Assessment</span>
            </div>
            <h4 className="text-lg font-black tracking-tight">
              {mode === 'practice' ? 'Start Practice Session' : 'Begin Graded Assessment'}
            </h4>
            <p className="text-xs text-blue-100 mt-1 mb-6">
              AI persona will calibrate difficulty in real-time. Make sure your browser focus is maintained.
            </p>

            {startError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-500/20 border border-rose-300/40 text-white text-xs">
                {startError}
              </div>
            )}

            <button
              onClick={handleStartInterview}
              disabled={isStarting}
              className="w-full py-3.5 px-6 rounded-xl font-bold text-sm bg-white text-blue-700 hover:bg-blue-50 transition-all shadow-md flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isStarting ? 'Assembling Context & AI Model...' : 'Launch Interview'}</span>
            </button>
          </div>

        </div>

      </div>
    </div>
  );
};
