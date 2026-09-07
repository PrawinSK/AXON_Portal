import React, { useEffect, useState } from 'react';
import { ClipboardList, CheckCircle2, Clock, UserCheck, RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../services/api';
import type { TaskItem } from '../types';

export const DepartmentTasksView: React.FC = () => {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getAllTasks();
      setTasks(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch department remediation tasks.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const pending = tasks.filter((t) => t.status !== 'completed').length;
  const completed = tasks.filter((t) => t.status === 'completed').length;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-600/10 via-cyan-500/10 to-transparent border border-blue-200 dark:border-blue-900/60 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-blue-600 dark:text-cyan-400 font-bold text-xs uppercase tracking-wider mb-1">
            <ClipboardList className="w-4 h-4" />
            <span>Faculty Oversight</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">
            Department Remediation Tasks
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 max-w-xl">
            Live log of all skill interventions assigned by faculty and HOD. Tasks auto-close when candidates score ≥ 7.0 in graded assessments.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-4 py-2 rounded-2xl bg-white dark:bg-[#0B0F19] border border-blue-100 dark:border-blue-900/60 shadow-sm text-center">
            <span className="block text-xl font-black text-amber-600 dark:text-amber-400">{pending}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">In Progress</span>
          </div>
          <div className="px-4 py-2 rounded-2xl bg-white dark:bg-[#0B0F19] border border-blue-100 dark:border-blue-900/60 shadow-sm text-center">
            <span className="block text-xl font-black text-emerald-600 dark:text-emerald-400">{completed}</span>
            <span className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">Resolved</span>
          </div>
          <button
            onClick={fetchTasks}
            disabled={isLoading}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-blue-900 bg-white dark:bg-[#0B0F19] text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 transition-all shadow-sm"
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

      {isLoading ? (
        <div className="text-center py-16">
          <RefreshCw className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-sm font-semibold text-slate-600 dark:text-slate-400">Loading department tasks...</p>
        </div>
      ) : tasks.length === 0 ? (
        <div className="p-12 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 text-center">
          <CheckCircle2 className="w-12 h-12 text-emerald-500 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-slate-900 dark:text-white">No Assigned Tasks</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-sm mx-auto">
            No remediation tasks have been created yet.
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {tasks.map((task) => {
            const isCompleted = task.status === 'completed';
            return (
              <div
                key={task.id}
                className="p-5 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-sm"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4 mb-2">
                  <div>
                    <div className="flex items-center space-x-2 mb-1.5">
                      <span className="font-extrabold text-sm text-slate-900 dark:text-white">
                        {task.student_name}
                      </span>
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-cyan-300 border border-blue-200 dark:border-blue-800">
                        {task.target_skill}
                      </span>
                      {isCompleted ? (
                        <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Cleared</span>
                        </span>
                      ) : (
                        <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300">
                          <Clock className="w-3 h-3" />
                          <span>Pending</span>
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 dark:text-slate-400 leading-relaxed">
                      {task.description}
                    </p>
                  </div>
                </div>

                <div className="pt-3 mt-3 border-t border-slate-100 dark:border-blue-950/60 flex flex-wrap items-center justify-between gap-2 text-xs text-slate-500 dark:text-slate-400">
                  <div className="flex items-center space-x-1.5">
                    <UserCheck className="w-3.5 h-3.5 text-blue-500" />
                    <span>Instructor: <strong className="text-slate-700 dark:text-slate-200">{task.assigned_by_name}</strong></span>
                  </div>
                  {task.due_date && (
                    <div className="flex items-center space-x-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-400" />
                      <span>Target Due: <strong>{task.due_date}</strong></span>
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
