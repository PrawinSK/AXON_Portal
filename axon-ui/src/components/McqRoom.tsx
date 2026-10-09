import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ChevronLeft,
  ChevronRight,
  Send,
  RotateCcw,
  BookOpen,
  Loader2,
  Clock
} from 'lucide-react';
import { api } from '../services/api';
import type {
  MCQSessionStartResponse,
  MCQSubmitResponse,
  MCQQuestion,
} from '../types';

interface McqRoomProps {
  studentName: string;
  onConcluded?: (result: MCQSubmitResponse) => void;
  onAbort: () => void;
}

export const McqRoom: React.FC<McqRoomProps> = ({
  studentName,
  onConcluded,
  onAbort,
}) => {
  const [session, setSession] = useState<MCQSessionStartResponse | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [selectedAnswers, setSelectedAnswers] = useState<Record<string, string>>({});
  const [strikes, setStrikes] = useState<number>(0);
  const [isDisqualified, setIsDisqualified] = useState<boolean>(false);
  const [strikeWarning, setStrikeWarning] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [result, setResult] = useState<MCQSubmitResponse | null>(null);
  const [timeElapsed, setTimeElapsed] = useState<number>(0);

  // Debounce strikes so multiple events within 1 second count as a single strike
  const lastStrikeTimeRef = useRef<number>(0);

  // Start new MCQ assessment session
  const initSession = useCallback(async () => {
    setIsLoading(true);
    setSubmitError(null);
    setResult(null);
    setSelectedAnswers({});
    setCurrentQuestionIndex(0);
    setStrikes(0);
    setIsDisqualified(false);
    setStrikeWarning(null);
    setTimeElapsed(0);

    try {
      const data = await api.startMCQSession();
      setSession(data);
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to initialize MCQ session. Ensure question bank is loaded.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    initSession();
  }, [initSession]);

  // Elapsed timer
  useEffect(() => {
    if (!session || result || isDisqualified) return;
    const interval = setInterval(() => {
      setTimeElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [session, result, isDisqualified]);

  // Handle focus loss / cursor out-of-focus violation
  const triggerStrike = useCallback(async (reason: string) => {
    if (!session || result || isDisqualified) return;

    const now = Date.now();
    if (now - lastStrikeTimeRef.current < 1500) {
      return; // Ignore duplicate events fired in rapid succession
    }
    lastStrikeTimeRef.current = now;

    try {
      const res = await api.recordMCQStrike(session.session_id);
      setStrikes(res.strikes);
      if (res.is_disqualified) {
        setIsDisqualified(true);
        setStrikeWarning(null);
      } else {
        setStrikeWarning(`Warning: ${reason}! Strike ${res.strikes} of 3. Leaving the proctored window again will forfeit your submission.`);
      }
    } catch (e) {
      console.error('Failed to record proctoring strike:', e);
    }
  }, [session, result, isDisqualified]);

  // Window Focus, Visibility & Cursor Blur Listeners
  useEffect(() => {
    if (!session || result || isDisqualified) return;

    const handleBlur = () => {
      triggerStrike('Assessment window lost focus');
    };

    const handleVisibilityChange = () => {
      if (document.hidden) {
        triggerStrike('Tab switch / backgrounding detected');
      }
    };

    const handleMouseLeave = (e: MouseEvent) => {
      // Check if mouse genuinely left the browser viewport (top or sides)
      if (e.clientY <= 0 || e.clientX <= 0 || e.clientX >= window.innerWidth || e.clientY >= window.innerHeight) {
        triggerStrike('Cursor left proctored test viewport');
      }
    };

    window.addEventListener('blur', handleBlur);
    document.addEventListener('visibilitychange', handleVisibilityChange);
    document.addEventListener('mouseleave', handleMouseLeave);

    return () => {
      window.removeEventListener('blur', handleBlur);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      document.removeEventListener('mouseleave', handleMouseLeave);
    };
  }, [session, result, isDisqualified, triggerStrike]);

  const handleSelectChoice = (questionId: string, choiceText: string) => {
    if (isDisqualified || result) return;
    setSelectedAnswers((prev) => ({
      ...prev,
      [questionId]: choiceText,
    }));
  };

  const handleSubmit = async () => {
    if (!session || isDisqualified || isSubmitting) return;

    const unansweredCount = session.total_questions - Object.keys(selectedAnswers).length;
    if (unansweredCount > 0) {
      const confirmed = window.confirm(
        `You have ${unansweredCount} unanswered question(s). Are you sure you want to finalize and submit?`
      );
      if (!confirmed) return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const subResult = await api.submitMCQAnswers(session.session_id, selectedAnswers);
      setResult(subResult);
      if (onConcluded) {
        onConcluded(subResult);
      }
    } catch (err: any) {
      setSubmitError(err.message || 'Submission failed. Please check network connection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // 1. Loading State
  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center">
        <Loader2 className="w-10 h-10 animate-spin text-blue-600 dark:text-cyan-400 mx-auto mb-4" />
        <h3 className="text-base font-bold text-slate-800 dark:text-slate-100">
          Generating Shuffled Proctored Assessment...
        </h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
          Calibrating randomized 20-question pool and configuring anti-cheat cursor monitors.
        </p>
      </div>
    );
  }

  // Error State during session initialization
  if (!session && submitError) {
    return (
      <div className="max-w-2xl mx-auto p-8 rounded-3xl bg-rose-50 dark:bg-rose-950/30 border border-rose-200 dark:border-rose-900 text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-rose-600 dark:text-rose-400 mx-auto" />
        <h3 className="text-lg font-bold text-rose-900 dark:text-rose-200">Unable to Start MCQ Assessment</h3>
        <p className="text-xs text-rose-700 dark:text-rose-300">{submitError}</p>
        <div className="flex justify-center gap-3 pt-2">
          <button
            onClick={initSession}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-rose-600 hover:bg-rose-700 text-white cursor-pointer shadow-md"
          >
            Retry Initialization
          </button>
          <button
            onClick={onAbort}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-slate-700 dark:text-slate-300 cursor-pointer"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (!session) return null;

  const questions = session.questions;
  const currentQ: MCQQuestion = questions[currentQuestionIndex];
  const totalCount = session.total_questions;
  const answeredCount = Object.keys(selectedAnswers).length;

  // 2. Disqualified Modal / Overlay
  if (isDisqualified) {
    return (
      <div className="max-w-2xl mx-auto my-8 p-8 rounded-3xl bg-rose-50 dark:bg-[#120808] border-2 border-rose-500 shadow-2xl text-center space-y-6 animate-shake">
        <div className="w-16 h-16 rounded-2xl bg-rose-600/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-400 flex items-center justify-center mx-auto border border-rose-300 dark:border-rose-800">
          <ShieldAlert className="w-10 h-10" />
        </div>

        <div>
          <span className="px-3 py-1 rounded-full text-xs font-extrabold uppercase bg-rose-200 dark:bg-rose-900 text-rose-900 dark:text-rose-200 tracking-wider">
            Assessment Terminated
          </span>
          <h2 className="text-2xl font-black text-rose-950 dark:text-rose-100 mt-2">
            3 Proctoring Strikes Incurred
          </h2>
          <p className="text-xs text-rose-800 dark:text-rose-300 max-w-md mx-auto mt-2 leading-relaxed">
            Your session was locked because your cursor or active window lost focus 3 times.
            Per Axon Assessment Integrity Rules, this attempt cannot be submitted.
          </p>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-[#1f1010] border border-rose-200 dark:border-rose-900/60 text-xs text-slate-700 dark:text-slate-300 font-medium">
          You must restart the MCQ assessment from Question 1 to generate a clean proctored record.
        </div>

        <div className="flex flex-col sm:flex-row justify-center gap-3 pt-2">
          <button
            onClick={initSession}
            className="flex items-center justify-center space-x-2 px-6 py-3 rounded-xl font-bold text-xs bg-rose-600 hover:bg-rose-700 text-white shadow-lg shadow-rose-600/20 cursor-pointer transition-all"
          >
            <RotateCcw className="w-4 h-4" />
            <span>Restart Assessment From Question 1</span>
          </button>
          <button
            onClick={onAbort}
            className="px-6 py-3 rounded-xl font-bold text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-slate-700 dark:text-slate-300 cursor-pointer"
          >
            Exit to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // 3. Scorecard / Concluded View
  if (result) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Banner */}
        <div className={`p-8 rounded-3xl border shadow-lg ${
          result.passed
            ? 'bg-gradient-to-br from-emerald-500/10 via-teal-500/10 to-transparent border-emerald-300 dark:border-emerald-800'
            : 'bg-gradient-to-br from-amber-500/10 via-rose-500/10 to-transparent border-amber-300 dark:border-amber-800'
        }`}>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <div className="flex items-center space-x-2 mb-2">
                <span className={`px-3 py-1 rounded-full text-xs font-extrabold uppercase ${
                  result.passed
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                    : 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 border border-amber-300 dark:border-amber-800'
                }`}>
                  {result.passed ? 'Assessment Passed' : 'Remediation Recommended'}
                </span>
                <span className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                  Time: {formatTimer(timeElapsed)}
                </span>
              </div>
              <h2 className="text-3xl font-black text-slate-900 dark:text-white">
                MCQ Scorecard: {result.score} / {result.total_questions}
              </h2>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                Candidate: <span className="font-bold">{result.student_name}</span> • Proctoring Strikes: <span className={`font-bold ${result.strikes > 0 ? 'text-amber-600' : 'text-emerald-600'}`}>{result.strikes} / 3</span>
              </p>
            </div>

            <div className="flex items-center space-x-4">
              <div className="text-center p-4 rounded-2xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-slate-800 shadow-sm min-w-28">
                <div className="text-3xl font-black text-blue-600 dark:text-cyan-400">
                  {result.percentage}%
                </div>
                <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mt-0.5">
                  Accuracy
                </div>
              </div>
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <button
              onClick={initSession}
              className="flex items-center space-x-2 px-5 py-2.5 rounded-xl font-bold text-xs bg-blue-600 hover:bg-blue-700 text-white cursor-pointer shadow-md transition-all"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Take Another Test</span>
            </button>
            <button
              onClick={onAbort}
              className="px-5 py-2.5 rounded-xl font-bold text-xs bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-800 text-slate-700 dark:text-slate-300 cursor-pointer"
            >
              Back to Portal
            </button>
          </div>
        </div>

        {/* Detailed Question Review */}
        <div className="space-y-4">
          <h3 className="text-base font-extrabold text-slate-900 dark:text-white flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-blue-600 dark:text-cyan-400" />
            <span>Comprehensive Question Review & Explanations</span>
          </h3>

          <div className="space-y-3">
            {result.breakdown.map((item, idx) => (
              <div
                key={item.question_id || idx}
                className={`p-5 rounded-2xl border transition-all ${
                  item.is_correct
                    ? 'bg-white dark:bg-[#080d19] border-emerald-200 dark:border-emerald-950/60'
                    : 'bg-white dark:bg-[#080d19] border-rose-200 dark:border-rose-950/60'
                }`}
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="w-6 h-6 rounded-lg bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-xs font-bold text-slate-600 dark:text-slate-300">
                      {idx + 1}
                    </span>
                    <span className="font-bold text-sm text-slate-900 dark:text-white">
                      {item.question_text}
                    </span>
                  </div>
                  {item.is_correct ? (
                    <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800 shrink-0">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Correct</span>
                    </span>
                  ) : (
                    <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300 border border-rose-300 dark:border-rose-800 shrink-0">
                      <XCircle className="w-3.5 h-3.5" />
                      <span>Incorrect</span>
                    </span>
                  )}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs mt-3">
                  <div className={`p-3 rounded-xl border ${
                    item.is_correct
                      ? 'bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/40 text-emerald-900 dark:text-emerald-200'
                      : 'bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/40 text-rose-900 dark:text-rose-200'
                  }`}>
                    <span className="font-bold block text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-0.5">
                      Your Selected Answer:
                    </span>
                    <span className="font-semibold">{item.selected_answer}</span>
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-slate-200">
                    <span className="font-bold block text-[10px] uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-0.5">
                      Correct Institutional Answer:
                    </span>
                    <span className="font-semibold text-emerald-600 dark:text-emerald-400">{item.correct_answer}</span>
                  </div>
                </div>

                {item.explanation && (
                  <div className="mt-3 p-3 rounded-xl bg-blue-50/50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/40 text-xs text-slate-700 dark:text-slate-300">
                    <span className="font-bold text-blue-700 dark:text-cyan-300 mr-1">Explanation:</span>
                    {item.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // 4. Active Proctored Assessment Room
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Strike Warning Banner */}
      {strikeWarning && (
        <div className="p-4 rounded-2xl bg-amber-500/10 border-2 border-amber-500 flex items-center justify-between gap-4 text-xs font-bold text-amber-800 dark:text-amber-200 animate-pulse">
          <div className="flex items-center space-x-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 dark:text-amber-400 shrink-0" />
            <span>{strikeWarning}</span>
          </div>
          <button
            onClick={() => setStrikeWarning(null)}
            className="px-3 py-1 rounded-lg bg-amber-600 text-white text-[11px] font-bold cursor-pointer hover:bg-amber-700"
          >
            Acknowledge
          </button>
        </div>
      )}

      {/* Proctoring HUD Topbar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-sm flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md shadow-blue-500/20">
            MCQ
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-sm text-slate-900 dark:text-white">
                Proctored Technical Assessment
              </span>
              <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-cyan-300 border border-blue-200 dark:border-blue-900">
                20 Questions
              </span>
            </div>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Candidate: <span className="font-semibold text-slate-700 dark:text-slate-300">{studentName}</span>
            </p>
          </div>
        </div>

        {/* Live Proctoring Strike Indicators & Timer */}
        <div className="flex items-center space-x-3">
          {/* Strikes Badge */}
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#0B0F19]">
            <ShieldAlert className={`w-4 h-4 ${strikes > 0 ? 'text-amber-500' : 'text-slate-400'}`} />
            <span className="text-xs font-bold text-slate-600 dark:text-slate-300">
              Strikes: <span className={strikes > 0 ? 'text-amber-600 dark:text-amber-400 font-extrabold' : ''}>{strikes} / 3</span>
            </span>
          </div>

          {/* Timer */}
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-[#0B0F19] text-xs font-mono font-bold text-slate-700 dark:text-slate-300">
            <Clock className="w-3.5 h-3.5 text-blue-600 dark:text-cyan-400" />
            <span>{formatTimer(timeElapsed)}</span>
          </div>

          <button
            onClick={onAbort}
            className="px-3 py-1.5 rounded-xl border border-rose-200 dark:border-rose-900/60 text-xs font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 cursor-pointer transition-all"
          >
            Quit
          </button>
        </div>
      </div>

      {/* Question Palette Pill Selector */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-2">
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-medium">
          <span>Question Navigator</span>
          <span>Answered: <strong>{answeredCount}</strong> of <strong>{totalCount}</strong></span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {questions.map((q, idx) => {
            const isAnswered = Boolean(selectedAnswers[q.id]);
            const isCurrent = idx === currentQuestionIndex;
            return (
              <button
                key={q.id}
                onClick={() => setCurrentQuestionIndex(idx)}
                className={`w-8 h-8 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                  isCurrent
                    ? 'ring-2 ring-blue-500 bg-blue-600 text-white shadow-md'
                    : isAnswered
                    ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-800'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-slate-900 dark:text-slate-400 dark:hover:bg-slate-800'
                }`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Main Question Card */}
      {currentQ && (
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-lg space-y-6">
          <div className="flex items-center justify-between gap-4 border-b border-slate-100 dark:border-slate-800/80 pb-4">
            <span className="text-xs font-extrabold uppercase px-3 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-cyan-300 border border-blue-200 dark:border-blue-900">
              Question {currentQuestionIndex + 1} of {totalCount}
            </span>
            <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">
              Topic: {currentQ.topic || 'Computer Science'}
            </span>
          </div>

          <h3 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white leading-relaxed">
            {currentQ.question}
          </h3>

          {/* Choices Options */}
          <div className="space-y-3 pt-2">
            {currentQ.choices.map((choice) => {
              const isSelected = selectedAnswers[currentQ.id] === choice.text || selectedAnswers[currentQ.id] === choice.label;
              return (
                <button
                  key={choice.label}
                  type="button"
                  onClick={() => handleSelectChoice(currentQ.id, choice.text)}
                  className={`w-full text-left p-4 rounded-2xl border-2 transition-all flex items-start space-x-3 cursor-pointer ${
                    isSelected
                      ? 'border-blue-600 bg-blue-50/70 dark:border-cyan-400 dark:bg-blue-950/40 shadow-sm'
                      : 'border-slate-200 hover:border-slate-300 bg-slate-50/50 dark:border-slate-800/80 dark:hover:border-slate-700 dark:bg-[#080d19]'
                  }`}
                >
                  <div className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 transition-colors ${
                    isSelected
                      ? 'bg-blue-600 text-white dark:bg-cyan-400 dark:text-slate-950'
                      : 'bg-slate-200 text-slate-700 dark:bg-slate-800 dark:text-slate-300'
                  }`}>
                    {choice.label}
                  </div>
                  <span className="text-xs sm:text-sm font-semibold text-slate-800 dark:text-slate-200 pt-0.5 leading-relaxed">
                    {choice.text}
                  </span>
                </button>
              );
            })}
          </div>

          {submitError && (
            <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-800 dark:text-rose-300">
              {submitError}
            </div>
          )}

          {/* Navigation and Final Submit Footer */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-100 dark:border-slate-800/80">
            <button
              onClick={() => setCurrentQuestionIndex((prev) => Math.max(0, prev - 1))}
              disabled={currentQuestionIndex === 0}
              className="flex items-center space-x-1 px-4 py-2 rounded-xl text-xs font-bold border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer w-full sm:w-auto justify-center"
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>

            <div className="flex items-center space-x-2 w-full sm:w-auto">
              {currentQuestionIndex < totalCount - 1 ? (
                <button
                  onClick={() => setCurrentQuestionIndex((prev) => Math.min(totalCount - 1, prev + 1))}
                  className="flex-1 sm:flex-initial flex items-center justify-center space-x-1 px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white cursor-pointer shadow-sm transition-all"
                >
                  <span>Next Question</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              ) : null}

              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="flex-1 sm:flex-initial flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl text-xs font-extrabold bg-blue-600 hover:bg-blue-700 text-white dark:bg-cyan-500 dark:text-slate-950 dark:hover:bg-cyan-400 shadow-md shadow-blue-500/20 cursor-pointer transition-all disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Grading Assessment...</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Submit Assessment</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
