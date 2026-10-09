import React, { useEffect, useState } from 'react';
import {
  CheckSquare,
  CheckCircle2,
  Clock,
  AlertCircle,
  Search,
  Trash2,
  Edit3,
  X,
  Loader2,
  AlertTriangle,
  HelpCircle,
  Filter,
} from 'lucide-react';
import { api } from '../services/api';
import type { MCQAdminQuestion, MCQUploadBatch } from '../types';

export const MCQQuestionVerifyView: React.FC = () => {
  const [questions, setQuestions] = useState<MCQAdminQuestion[]>([]);
  const [batches, setBatches] = useState<MCQUploadBatch[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedBatch, setSelectedBatch] = useState<string>('all');
  const [approvalFilter, setApprovalFilter] = useState<string>('all');

  // Edit Question Modal State
  const [editingQuestion, setEditingQuestion] = useState<MCQAdminQuestion | null>(null);
  const [editPrompt, setEditPrompt] = useState<string>('');
  const [editOptions, setEditOptions] = useState<string[]>(['', '', '', '']);
  const [editCorrectAnswer, setEditCorrectAnswer] = useState<string>('');
  const [editExplanation, setEditExplanation] = useState<string>('');
  const [editTopic, setEditTopic] = useState<string>('');
  const [editIsApproved, setEditIsApproved] = useState<boolean>(true);
  const [isSavingEdit, setIsSavingEdit] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  // Status Banners
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [qData, bData] = await Promise.all([
        api.getMCQAdminQuestions(selectedBatch, approvalFilter),
        api.getMCQBatches(),
      ]);
      setQuestions(qData || []);
      setBatches(bData || []);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to load question pool.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedBatch, approvalFilter]);

  const handleToggleApproval = async (q: MCQAdminQuestion) => {
    const nextApproved = !q.is_approved;
    try {
      await api.toggleMCQApproval(q.id, nextApproved);
      setQuestions((prev) =>
        prev.map((item) => (item.id === q.id ? { ...item, is_approved: nextApproved } : item))
      );
      setStatusMessage(
        nextApproved
          ? `Question "${q.question_text.slice(0, 30)}..." verified & approved for student exams!`
          : `Question "${q.question_text.slice(0, 30)}..." moved back to pending verification.`
      );
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err: any) {
      alert(`Could not toggle approval: ${err.message || 'Error'}`);
    }
  };

  const handleDeleteQuestion = async (q: MCQAdminQuestion) => {
    const confirmed = window.confirm(
      `Delete question: "${q.question_text.slice(0, 50)}..."? This cannot be undone.`
    );
    if (!confirmed) return;

    try {
      await api.deleteMCQQuestion(q.id);
      setQuestions((prev) => prev.filter((item) => item.id !== q.id));
      setStatusMessage('Question deleted successfully.');
      setTimeout(() => setStatusMessage(null), 3000);
    } catch (err: any) {
      alert(`Failed to delete question: ${err.message || 'Error'}`);
    }
  };

  const handleDeleteBatch = async (batchId: string) => {
    const targetBatch = batches.find((b) => b.batch_id === batchId);
    const label = targetBatch ? `${targetBatch.source} (${targetBatch.upload_time})` : batchId;
    const confirmed = window.confirm(
      `DELETE ENTIRE BATCH: "${label}"?\nThis will permanently delete all questions uploaded in this batch.`
    );
    if (!confirmed) return;

    try {
      const res = await api.deleteMCQBatch(batchId);
      setStatusMessage(res.message || `Deleted upload batch.`);
      setSelectedBatch('all');
      fetchData();
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err: any) {
      alert(`Failed to delete upload batch: ${err.message || 'Error'}`);
    }
  };

  const handleOpenEdit = (q: MCQAdminQuestion) => {
    setEditingQuestion(q);
    setEditPrompt(q.question_text);
    setEditOptions(q.options && q.options.length ? [...q.options] : ['', '', '', '']);
    setEditCorrectAnswer(q.correct_answer);
    setEditExplanation(q.explanation || '');
    setEditTopic(q.topic || 'General IT / Computer Science');
    setEditIsApproved(q.is_approved);
    setSaveError(null);
  };

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingQuestion) return;

    const filteredOptions = editOptions.map((o) => o.trim()).filter(Boolean);
    if (filteredOptions.length < 2) {
      setSaveError('Please provide at least 2 distinct options.');
      return;
    }

    if (!editCorrectAnswer.trim()) {
      setSaveError('Please select or specify the correct answer.');
      return;
    }

    setIsSavingEdit(true);
    setSaveError(null);
    try {
      const updated = await api.updateMCQQuestion(editingQuestion.id, {
        question_text: editPrompt.trim(),
        options: filteredOptions,
        correct_answer: editCorrectAnswer.trim(),
        explanation: editExplanation.trim(),
        topic: editTopic.trim(),
        is_approved: editIsApproved,
      });

      setQuestions((prev) =>
        prev.map((item) => (item.id === updated.id ? { ...item, ...updated } : item))
      );
      setEditingQuestion(null);
      setStatusMessage('Question updated and verified successfully.');
      setTimeout(() => setStatusMessage(null), 4000);
    } catch (err: any) {
      setSaveError(err.message || 'Failed to update question.');
    } finally {
      setIsSavingEdit(false);
    }
  };

  const cleanSearch = searchTerm.toLowerCase().trim();
  const filteredQuestions = questions.filter((q) => {
    if (!cleanSearch) return true;
    const prompt = (q.question_text || '').toLowerCase();
    const ans = (q.correct_answer || '').toLowerCase();
    const topic = (q.topic || '').toLowerCase();
    const source = (q.source || '').toLowerCase();
    return prompt.includes(cleanSearch) || ans.includes(cleanSearch) || topic.includes(cleanSearch) || source.includes(cleanSearch);
  });

  const totalCount = questions.length;
  const approvedCount = questions.filter((q) => q.is_approved).length;
  const pendingCount = questions.filter((q) => !q.is_approved).length;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-amber-600/10 via-indigo-500/10 to-transparent border border-amber-200 dark:border-amber-900/60 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 font-bold text-xs uppercase tracking-wider mb-1">
            <CheckSquare className="w-4 h-4" />
            <span>Institutional Examination Quality Control</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">
            MCQ Question Verification & Pool Management
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
            Staff & HOD verification console: Inspect uploaded questions & automated answers, edit options, approve verified questions for candidate exams, and manage bulk upload batches by timestamp.
          </p>
        </div>

        {/* Exam Readiness Badges */}
        <div className="flex items-center space-x-3">
          <div className="px-4 py-2.5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-emerald-200 dark:border-emerald-900 shadow-sm text-center">
            <span className="block text-xl font-black text-emerald-600 dark:text-emerald-400">{approvedCount}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Exam Ready</span>
          </div>
          <div className="px-4 py-2.5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-amber-200 dark:border-amber-900 shadow-sm text-center">
            <span className="block text-xl font-black text-amber-600 dark:text-amber-400">{pendingCount}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Pending Verify</span>
          </div>
          <div className="px-4 py-2.5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-slate-800 shadow-sm text-center">
            <span className="block text-xl font-black text-slate-800 dark:text-slate-200">{totalCount}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Total Pool</span>
          </div>
        </div>
      </div>

      {/* Status Notifications */}
      {statusMessage && (
        <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 flex items-center justify-between text-xs text-emerald-800 dark:text-emerald-200">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400 flex-shrink-0" />
            <span>{statusMessage}</span>
          </div>
          <button
            onClick={() => setStatusMessage(null)}
            className="text-emerald-700 dark:text-emerald-400 hover:opacity-75 cursor-pointer text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-3.5 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 flex items-center justify-between text-xs text-rose-800 dark:text-rose-200">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button
            onClick={() => setErrorMessage(null)}
            className="text-rose-700 dark:text-rose-400 hover:opacity-75 cursor-pointer text-xs font-bold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Filter & Batch Controls Bar */}
      <div className="p-4 rounded-2xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-3">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          
          {/* Batch Selector & Timestamp Option */}
          <div className="flex flex-wrap items-center gap-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 dark:text-slate-300">
              <Clock className="w-4 h-4 text-amber-500" />
              <span>Upload Batch:</span>
            </div>
            <select
              value={selectedBatch}
              onChange={(e) => setSelectedBatch(e.target.value)}
              className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <option value="all">All Upload Batches ({batches.length} batches)</option>
              {batches.map((b) => (
                <option key={b.batch_id} value={b.batch_id}>
                  {b.upload_time ? `🕒 ${b.upload_time}` : 'System Seed'} • {b.source} ({b.total_questions} Qs, {b.approved_count} approved)
                </option>
              ))}
            </select>

            {/* Delete Batch Button (Enabled when specific batch is selected) */}
            {selectedBatch !== 'all' && (
              <button
                onClick={() => handleDeleteBatch(selectedBatch)}
                className="flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 hover:bg-rose-100 transition-all cursor-pointer"
                title="Delete all questions in this selected upload batch"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Delete Entire Batch</span>
              </button>
            )}

            {/* Approval Filter */}
            <div className="flex items-center space-x-1 ml-2">
              <Filter className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={approvalFilter}
                onChange={(e) => setApprovalFilter(e.target.value)}
                className="px-3 py-2 rounded-xl text-xs font-semibold bg-slate-50 dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-900 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500"
              >
                <option value="all">All Statuses</option>
                <option value="approved">Approved for Exams Only</option>
                <option value="pending">Pending Verification Only</option>
              </select>
            </div>
          </div>

          {/* Search Bar */}
          <div className="relative w-full lg:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search questions, answers, topics..."
              className="w-full pl-10 pr-9 py-2 text-xs rounded-xl border border-slate-200 dark:border-blue-900 bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Questions List */}
      {isLoading ? (
        <div className="text-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-amber-600 mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">Loading MCQ question bank...</p>
        </div>
      ) : filteredQuestions.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 text-center space-y-3">
          <HelpCircle className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto" />
          <h3 className="font-extrabold text-lg text-slate-800 dark:text-slate-200">No Questions Found</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
            {cleanSearch
              ? `No questions matched "${searchTerm}".`
              : "No questions in this batch or filter selection."}
          </p>
          {cleanSearch && (
            <button
              onClick={() => setSearchTerm('')}
              className="px-4 py-2 rounded-xl text-xs font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/60 border border-amber-200 dark:border-amber-800 hover:bg-amber-100 cursor-pointer"
            >
              Clear Search Filter
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500 px-1">
            <span>Showing <strong>{filteredQuestions.length}</strong> question(s)</span>
            <span className="text-[11px]">Approved questions are served to students in proctored exams</span>
          </div>

          <div className="grid grid-cols-1 gap-4">
            {filteredQuestions.map((q, idx) => {
              const isApproved = q.is_approved;
              return (
                <div
                  key={q.id}
                  className={`p-5 rounded-2xl bg-white dark:bg-[#030712] border shadow-sm transition-all flex flex-col justify-between ${
                    isApproved
                      ? 'border-emerald-200 dark:border-emerald-950/80'
                      : 'border-amber-300 dark:border-amber-900/60 bg-amber-50/10'
                  }`}
                >
                  <div>
                    {/* Header: Topic, Timestamp & Status Badge */}
                    <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-cyan-300 border border-blue-200 dark:border-blue-900">
                          {q.topic}
                        </span>
                        <span className="text-[11px] text-slate-400 flex items-center space-x-1">
                          <Clock className="w-3 h-3 text-slate-400" />
                          <span>{q.upload_time || 'Pre-seeded'}</span>
                        </span>
                        <span className="text-[10px] text-slate-400 font-mono">
                          ID: {q.id}
                        </span>
                      </div>

                      <div className="flex items-center space-x-2">
                        {isApproved ? (
                          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950/70 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                            <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                            <span>Verified & Approved</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-950/70 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                            <AlertTriangle className="w-3 h-3 text-amber-500" />
                            <span>Pending Verification</span>
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Question Prompt */}
                    <h4 className="text-sm font-bold text-slate-900 dark:text-white leading-relaxed mb-3">
                      {idx + 1}. {q.question_text}
                    </h4>

                    {/* Options List with Highlighted Correct Answer */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-3">
                      {q.options.map((opt, oIdx) => {
                        const letter = ['A', 'B', 'C', 'D', 'E'][oIdx] || `${oIdx + 1}`;
                        const isCorrect = opt.trim().toLowerCase() === q.correct_answer.trim().toLowerCase();
                        return (
                          <div
                            key={oIdx}
                            className={`p-2.5 rounded-xl text-xs flex items-center space-x-2 border ${
                              isCorrect
                                ? 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200 font-bold'
                                : 'bg-slate-50 dark:bg-[#0B0F19] border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
                            }`}
                          >
                            <span className={`w-5 h-5 rounded-lg flex items-center justify-center text-[10px] font-black ${
                              isCorrect
                                ? 'bg-emerald-500 text-white'
                                : 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
                            }`}>
                              {letter}
                            </span>
                            <span className="flex-1">{opt}</span>
                            {isCorrect && (
                              <span className="text-[10px] uppercase font-black text-emerald-600 dark:text-emerald-400">
                                Verified Answer
                              </span>
                            )}
                          </div>
                        );
                      })}
                    </div>

                    {/* Explanation */}
                    {q.explanation && (
                      <div className="p-2.5 rounded-xl bg-slate-50 dark:bg-[#0B0F19] border border-slate-100 dark:border-blue-950 text-[11px] text-slate-600 dark:text-slate-400 mb-3">
                        <span className="font-bold text-slate-700 dark:text-slate-300">Explanation: </span>
                        {q.explanation}
                      </div>
                    )}
                  </div>

                  {/* Card Actions Footer */}
                  <div className="pt-3 border-t border-slate-100 dark:border-blue-950/80 flex flex-wrap items-center justify-between gap-2">
                    <span className="text-[11px] text-slate-400">
                      Source: {q.source}
                    </span>

                    <div className="flex items-center space-x-2">
                      {/* One-click Toggle Approval */}
                      <button
                        onClick={() => handleToggleApproval(q)}
                        className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 cursor-pointer ${
                          isApproved
                            ? 'bg-amber-50 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-900 hover:bg-amber-100'
                            : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm'
                        }`}
                      >
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        <span>{isApproved ? 'Unapprove' : 'Verify & Approve'}</span>
                      </button>

                      {/* Edit Question */}
                      <button
                        onClick={() => handleOpenEdit(q)}
                        className="px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-900 hover:bg-slate-200 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 transition-all flex items-center space-x-1.5 cursor-pointer"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                        <span>Edit</span>
                      </button>

                      {/* Delete Question */}
                      <button
                        onClick={() => handleDeleteQuestion(q)}
                        className="px-3 py-1.5 rounded-xl text-xs font-bold text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 hover:bg-rose-100 transition-all flex items-center space-x-1.5 cursor-pointer"
                        title="Delete Question"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        <span>Delete</span>
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Edit Question Modal */}
      {editingQuestion && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-xl w-full p-6 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200 max-h-[90vh] overflow-y-auto">
            <button
              onClick={() => setEditingQuestion(null)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-5">
              <div className="w-10 h-10 rounded-2xl bg-amber-100 dark:bg-amber-950 flex items-center justify-center text-amber-600 dark:text-amber-400">
                <Edit3 className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">
                  Edit MCQ & Verify Answer
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Update question text, choices, correct answer, and approval status
                </p>
              </div>
            </div>

            {saveError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{saveError}</span>
              </div>
            )}

            <form onSubmit={handleSaveEdit} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Question Prompt *
                </label>
                <textarea
                  rows={3}
                  value={editPrompt}
                  onChange={(e) => setEditPrompt(e.target.value)}
                  required
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Option Choices (A, B, C, D) *
                </label>
                <div className="space-y-2">
                  {editOptions.map((opt, i) => (
                    <div key={i} className="flex items-center space-x-2">
                      <span className="w-6 h-6 rounded-lg bg-slate-100 dark:bg-slate-900 text-slate-700 dark:text-slate-300 flex items-center justify-center text-xs font-bold">
                        {['A', 'B', 'C', 'D', 'E'][i] || `${i + 1}`}
                      </span>
                      <input
                        type="text"
                        value={opt}
                        onChange={(e) => {
                          const updated = [...editOptions];
                          updated[i] = e.target.value;
                          setEditOptions(updated);
                        }}
                        placeholder={`Option ${['A', 'B', 'C', 'D', 'E'][i] || i + 1}`}
                        required={i < 2}
                        className="flex-1 px-3 py-2 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Correct Answer *
                </label>
                <select
                  value={editCorrectAnswer}
                  onChange={(e) => setEditCorrectAnswer(e.target.value)}
                  required
                  className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs font-bold text-emerald-600 focus:ring-2 focus:ring-amber-500 focus:outline-none"
                >
                  <option value="">Select the verified correct answer...</option>
                  {editOptions.filter(Boolean).map((opt, i) => (
                    <option key={i} value={opt}>
                      {['A', 'B', 'C', 'D', 'E'][i]}: {opt}
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                    Topic / Domain
                  </label>
                  <input
                    type="text"
                    value={editTopic}
                    onChange={(e) => setEditTopic(e.target.value)}
                    placeholder="e.g. Data Structures, Networking"
                    className="w-full px-3 py-2 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                    Approval State
                  </label>
                  <div className="flex items-center space-x-2 pt-1.5">
                    <input
                      type="checkbox"
                      id="editIsApproved"
                      checked={editIsApproved}
                      onChange={(e) => setEditIsApproved(e.target.checked)}
                      className="w-4 h-4 rounded text-emerald-600 focus:ring-emerald-500"
                    />
                    <label htmlFor="editIsApproved" className="text-xs text-slate-800 dark:text-slate-200 font-semibold cursor-pointer">
                      Verify & Approve for Exams
                    </label>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Explanation
                </label>
                <textarea
                  rows={2}
                  value={editExplanation}
                  onChange={(e) => setEditExplanation(e.target.value)}
                  placeholder="Reasoning or reference for the correct answer..."
                  className="w-full p-3 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-amber-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setEditingQuestion(null)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSavingEdit}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-amber-600 hover:bg-amber-700 transition-all shadow-md shadow-amber-500/25 flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {isSavingEdit ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Saving Changes...</span>
                    </>
                  ) : (
                    <span>Save & Verify</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
