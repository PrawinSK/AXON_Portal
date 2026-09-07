import React, { useEffect, useState } from 'react';
import { CheckCircle2, Clock, PlayCircle, BookOpen, AlertCircle, RefreshCw, UserCheck } from 'lucide-react';
import { api } from '../services/api';
import type { TaskItem } from '../types';

interface StudentTasksProps {
  onStartTargetedInterview?: (skill: string) => void;
}

export const StudentTasks: React.FC<StudentTasksProps> = ({ onStartTargetedInterview }) => {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getMyTasks();
      setTasks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch assigned tasks.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const pendingCount = tasks.filter((t) => t.status !== 'completed').length;
  const completedCount = tasks.filter((t) => t.status === 'completed').length;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-600/10 via-cyan-500/10 to-transparent border border-blue-200 dark:border-blue-900/60 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-blue-600 dark:text-cyan-400 font-bold text-xs uppercase tracking-wider mb-1">
            <BookOpen className="w-4 h-4" />
            <span>Remediation Roadmap</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">
            Assigned Skill Tasks
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 max-w-xl">
            Remediation assignments created by Faculty & HOD to address interview skill gaps. Clear tasks by completing a targeted graded assessment with a score ≥ 7.0.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-4 py-2 rounded-2xl bg-white dark:bg-[#0B0F19] border border-blue-100 dark:border-blue-900/60 shadow-sm text-center">
            <span className="block text-xl font-black text-amber-600 dark:text-amber-400">{pendingCount}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Pending</span>
          </div>
          <div className="px-4 py-2 rounded-2xl bg-white dark:bg-[#0B0F19] border border-blue-100 dark:border-blue-900/60 shadow-sm text-center">
            <span className="block text-xl font-black text-emerald-600 dark:text-emerald-400">{completedCount}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Cleared</span>
          </div>
          <button
            onClick={fetchTasks}
            disabled={isLoading}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-blue-900 bg-white dark:bg-[#0B0F19] text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 transition-all shadow-sm"
            title="Refresh tasks"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-blue-600' : ''}`} />
          </button>
        </div>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-center space-x-2 text-rose-700 dark:text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Task List */}
      {isLoading ? (
        <div className="text-center py-16">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">Loading your remediation tasks...</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 text-center">
          <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">All Clear! No Pending Tasks</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
            You have no outstanding remediation assignments from your instructors. Continue taking practice interviews to sharpen your skills.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {tasks.map((task) => {
            const isCompleted = task.status === 'completed';
            return (
              <div
                key={task.id}
                className={`p-6 rounded-3xl border transition-all duration-200 ${
                  isCompleted
                    ? 'bg-emerald-50/40 dark:bg-emerald-950/10 border-emerald-200 dark:border-emerald-900/40'
                    : 'bg-white dark:bg-[#030712] border-slate-200 dark:border-blue-950/80 hover:border-blue-300 dark:hover:border-blue-800 shadow-sm'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-3">
                  <div>
                    <div className="flex items-center space-x-2 mb-1.5">
                      <span className="px-2.5 py-0.5 rounded-full text-[11px] font-extrabold tracking-wide uppercase bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-cyan-300 border border-blue-200 dark:border-blue-800">
                        {task.target_skill}
                      </span>
                      {isCompleted ? (
                        <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Cleared</span>
                        </span>
                      ) : (
                        <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
                          <Clock className="w-3 h-3" />
                          <span>Action Required</span>
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-700 dark:text-slate-300 font-medium leading-relaxed">
                      {task.description}
                    </p>
                  </div>

                  {!isCompleted && onStartTargetedInterview && (
                    <button
                      onClick={() => onStartTargetedInterview(task.target_skill)}
                      className="inline-flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-500 shadow-md shadow-blue-500/20 transition-all flex-shrink-0"
                    >
                      <PlayCircle className="w-4 h-4" />
                      <span>Take Practice Assessment</span>
                    </button>
                  )}
                </div>

                <div className="pt-3 mt-3 border-t border-slate-100 dark:border-blue-950/60 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center space-x-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-500" />
                    <span>Assigned by: <strong className="text-slate-700 dark:text-slate-200">{task.assigned_by_name}</strong></span>
                  </div>
                  {task.due_date && (
                    <div className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>Due: <strong>{task.due_date}</strong></span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
