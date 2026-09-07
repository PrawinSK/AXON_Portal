import React, { useState, useEffect } from 'react';
import {
  Send,
  Sparkles,
  AlertTriangle,
  HelpCircle,
  Clock,
  ArrowRight,
  ShieldAlert,
  BookOpen
} from 'lucide-react';
import { api } from '../services/api';
import type {
  StartInterviewResponse,
  TurnEvaluation,
  SynthesisResponse,
} from '../types';

interface InterviewRoomProps {
  session: StartInterviewResponse;
  candidateName: string;
  onConcluded: (synthesis: SynthesisResponse) => void;
  onAbort: () => void;
}

export const InterviewRoom: React.FC<InterviewRoomProps> = ({
  session,
  candidateName,
  onConcluded,
  onAbort,
}) => {
  const [currentTurn, setCurrentTurn] = useState(session.current_turn);
  const [currentQuestion, setCurrentQuestion] = useState(session.first_question);
  const [answer, setAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastEvaluation, setLastEvaluation] = useState<TurnEvaluation | null>(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [nextQuestionPending, setNextQuestionPending] = useState<string | null>(null);

  // Proctoring / Anti-Malpractice States
  const [strikeCount, setStrikeCount] = useState(0);
  const [showStrikeWarning, setShowStrikeWarning] = useState(false);
  const [strikeReason, setStrikeReason] = useState('');

  // Elapsed interview timer
  const [secondsElapsed, setSecondsElapsed] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsElapsed((prev) => prev + 1);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Window Focus Tracking (Tab switch detection)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden) {
        handleTriggerStrike('Tab switch or minimized window detected.');
      }
    };

    const handleBlur = () => {
      handleTriggerStrike('Browser window lost focus.');
    };

    window.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('blur', handleBlur);

    return () => {
      window.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('blur', handleBlur);
    };
  }, []);

  const handleTriggerStrike = (reason: string) => {
    setStrikeCount((prev) => {
      const next = prev + 1;
      setStrikeReason(reason);
      setShowStrikeWarning(true);
      return next;
    });
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleSubmitAnswer = async () => {
    if (!answer.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      const res = await api.submitAnswer(session.session_id, answer);

      if (res.evaluation) {
        setLastEvaluation(res.evaluation);
      }

      if (res.is_completed) {
        // Conclude interview immediately
        const synthesis = await api.concludeInterview(session.session_id);
        onConcluded(synthesis);
      } else {
        if (session.mode === 'practice' && res.evaluation) {
          // In practice mode, show instant feedback and hold until candidate clicks Continue
          setNextQuestionPending(res.next_question || null);
          setShowFeedbackModal(true);
        } else {
          // In graded mode, advance immediately
          setCurrentTurn((prev) => prev + 1);
          setCurrentQuestion(res.next_question || '');
          setAnswer('');
        }
      }
    } catch (err: any) {
      alert(`Submission failed: ${err.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProceedToNextQuestion = () => {
    if (nextQuestionPending) {
      setCurrentTurn((prev) => prev + 1);
      setCurrentQuestion(nextQuestionPending);
      setAnswer('');
      setNextQuestionPending(null);
      setShowFeedbackModal(false);
      setLastEvaluation(null);
    }
  };

  const progressPercentage = Math.round(((currentTurn - 1) / session.max_questions) * 100);

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6">
      
      {/* Top Header Bar: Progress & Focus Monitor */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm mb-6">
        <div className="flex items-center space-x-3">
          <div className="flex flex-col">
            <span className="text-xs text-slate-500 dark:text-slate-400">Candidate</span>
            <span className="font-bold text-sm text-slate-900 dark:text-white">{candidateName}</span>
          </div>
          <span className="text-slate-300 dark:text-slate-700">|</span>
          <div className="flex items-center space-x-1.5 text-xs font-semibold px-2.5 py-1 rounded-full bg-blue-50 text-blue-700 dark:bg-blue-950/80 dark:text-cyan-300">
            {session.mode === 'practice' ? (
              <>
                <BookOpen className="w-3.5 h-3.5" />
                <span>Practice Mode</span>
              </>
            ) : (
              <>
                <ShieldAlert className="w-3.5 h-3.5 text-emerald-500" />
                <span>Graded Proctored</span>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-1.5 text-xs font-mono text-slate-600 dark:text-slate-400">
            <Clock className="w-4 h-4 text-blue-500" />
            <span>{formatTime(secondsElapsed)}</span>
          </div>

          {/* Proctoring Strikes Counter */}
          <div className="flex items-center space-x-1">
            <span className="text-xs text-slate-500 dark:text-slate-400">Strikes:</span>
            <div className="flex space-x-1">
              {[1, 2, 3].map((num) => (
                <span
                  key={num}
                  className={`w-2.5 h-2.5 rounded-full ${
                    strikeCount >= num
                      ? 'bg-rose-500 shadow-sm shadow-rose-500/50'
                      : 'bg-slate-200 dark:bg-slate-800'
                  }`}
                />
              ))}
            </div>
          </div>

          <button
            onClick={onAbort}
            className="text-xs font-medium text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 transition-colors"
          >
            Exit Session
          </button>
        </div>
      </div>

      {/* Subtle Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between items-center text-xs font-medium text-slate-600 dark:text-slate-400 mb-1.5">
          <span>Question {currentTurn} of {session.max_questions}</span>
          <span>{progressPercentage}% Complete</span>
        </div>
        <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-900 overflow-hidden border border-slate-200/60 dark:border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-400 transition-all duration-500"
            style={{ width: `${Math.max(5, progressPercentage)}%` }}
          />
        </div>
      </div>

      {/* Main Question Card */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#0B0F19] border border-blue-100 dark:border-blue-950/80 shadow-md dark:shadow-blue-950/20 mb-6">
        <div className="flex items-center space-x-2 text-xs font-bold text-blue-600 dark:text-cyan-400 uppercase tracking-wider mb-3">
          <Sparkles className="w-4 h-4" />
          <span>Interviewer Prompt (Turn {currentTurn})</span>
        </div>

        <h2 className="text-xl sm:text-2xl font-semibold text-slate-900 dark:text-slate-100 leading-relaxed">
          {currentQuestion}
        </h2>
      </div>

      {/* Response Box */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-4">
        <div className="flex justify-between items-center">
          <label className="text-xs font-bold text-slate-700 dark:text-slate-300">
            Your Technical Response
          </label>
          <span className="text-[11px] text-slate-400 font-mono">
            {answer.trim().split(/\s+/).filter(Boolean).length} words
          </span>
        </div>

        <textarea
          rows={6}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          onKeyDown={(e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
              e.preventDefault();
              handleSubmitAnswer();
            }
          }}
          disabled={isSubmitting || showFeedbackModal}
          placeholder="Type your structured answer here. Cover architectural patterns, mechanics, edge-cases, and trade-offs... (Ctrl + Enter to submit)"
          className="w-full p-4 rounded-2xl text-sm leading-relaxed bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50 resize-y"
        />

        <div className="flex flex-wrap items-center justify-between gap-4 pt-2">
          <div className="text-[11px] text-slate-400 flex items-center space-x-1">
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Pro tip: Press <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">Ctrl</kbd> + <kbd className="px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-300">Enter</kbd> to submit</span>
          </div>

          <button
            onClick={handleSubmitAnswer}
            disabled={!answer.trim() || isSubmitting || showFeedbackModal}
            className="py-3 px-6 rounded-xl font-bold text-sm bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500 transition-all shadow-md shadow-blue-500/20 flex items-center space-x-2 disabled:opacity-50 cursor-pointer"
          >
            {isSubmitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Evaluating Technical Depth...</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Submit Answer</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Practice Mode Turn Feedback Modal / Drawer */}
      {showFeedbackModal && lastEvaluation && (
        <div className="mt-6 p-6 rounded-3xl bg-blue-50/80 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 shadow-lg animate-in fade-in slide-in-from-bottom-3 duration-300">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <span className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center font-black text-sm">
                {lastEvaluation.score.toFixed(1)}
              </span>
              <div>
                <h4 className="font-bold text-sm text-slate-900 dark:text-white">
                  Turn {currentTurn} Evaluation
                </h4>
                <p className="text-[11px] text-slate-500 dark:text-slate-400">
                  Instant coaching feedback (Practice Mode)
                </p>
              </div>
            </div>

            <button
              onClick={handleProceedToNextQuestion}
              className="py-2 px-4 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white flex items-center space-x-1 shadow-sm transition-all"
            >
              <span>Continue to Question {currentTurn + 1}</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3 rounded-xl bg-white/80 dark:bg-slate-900/60 border border-blue-100 dark:border-blue-900/40">
              <span className="font-bold text-slate-900 dark:text-white block mb-1">Technical Accuracy:</span>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{lastEvaluation.technical_accuracy}</p>
            </div>

            <div className="p-3 rounded-xl bg-white/80 dark:bg-slate-900/60 border border-blue-100 dark:border-blue-900/40">
              <span className="font-bold text-slate-900 dark:text-white block mb-1">Areas for Improvement:</span>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{lastEvaluation.areas_for_improvement}</p>
            </div>

            <div className="p-3 rounded-xl bg-white/80 dark:bg-slate-900/60 border border-blue-100 dark:border-blue-900/40">
              <span className="font-bold text-slate-900 dark:text-white block mb-1">Interviewer Coaching Hint:</span>
              <p className="text-slate-600 dark:text-slate-300 leading-relaxed">{lastEvaluation.feedback}</p>
            </div>
          </div>
        </div>
      )}

      {/* Proctoring Warning Strike Alert */}
      {showStrikeWarning && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-md w-full p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-rose-200 dark:border-rose-900 shadow-2xl space-y-4 text-center">
            <div className="w-12 h-12 rounded-full bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 mx-auto flex items-center justify-center">
              <AlertTriangle className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-black text-slate-900 dark:text-white">
              Focus Loss Warning (Strike {strikeCount}/3)
            </h3>
            <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
              {strikeReason} Axon monitors window focus and clipboard events to maintain assessment integrity. Accumulating 3 strikes flags the session for administrative review.
            </p>
            <button
              onClick={() => setShowStrikeWarning(false)}
              className="w-full py-2.5 rounded-xl font-bold text-xs bg-rose-600 hover:bg-rose-700 text-white transition-all shadow-md"
            >
              I Understand, Return to Interview
            </button>
          </div>
        </div>
      )}

    </div>
  );
};
