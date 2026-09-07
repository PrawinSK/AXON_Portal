import React, { useState } from 'react';
import {
  BarChart3,
  PlusCircle,
  CheckCircle2,
  X
} from 'lucide-react';

interface StudentSkillRecord {
  id: string;
  name: string;
  rollNumber: string;
  department: string;
  scores: Record<string, number>;
}

const INITIAL_STUDENTS: StudentSkillRecord[] = [
  {
    id: '1',
    name: 'Rahul Sharma',
    rollNumber: '21CS042',
    department: 'Computer Science',
    scores: {
      'Redis & Caching': 4.5,
      'SQL & Indexing': 8.5,
      'System Architecture': 5.0,
      'Concurrency & Async': 7.5,
      'Docker & CI/CD': 8.0,
    },
  },
  {
    id: '2',
    name: 'Priya Sundaram',
    rollNumber: '21CS058',
    department: 'Computer Science',
    scores: {
      'Redis & Caching': 8.0,
      'SQL & Indexing': 4.0,
      'System Architecture': 7.5,
      'Concurrency & Async': 6.0,
      'Docker & CI/CD': 8.5,
    },
  },
  {
    id: '3',
    name: 'Ananya Verma',
    rollNumber: '21CS014',
    department: 'Computer Science',
    scores: {
      'Redis & Caching': 7.5,
      'SQL & Indexing': 8.0,
      'System Architecture': 8.5,
      'Concurrency & Async': 8.5,
      'Docker & CI/CD': 9.0,
    },
  },
  {
    id: '4',
    name: 'Karthik Raja',
    rollNumber: '21CS033',
    department: 'Computer Science',
    scores: {
      'Redis & Caching': 3.5,
      'SQL & Indexing': 5.5,
      'System Architecture': 4.0,
      'Concurrency & Async': 5.0,
      'Docker & CI/CD': 6.5,
    },
  },
  {
    id: '5',
    name: 'Sneha Patel',
    rollNumber: '21CS077',
    department: 'Computer Science',
    scores: {
      'Redis & Caching': 8.5,
      'SQL & Indexing': 7.5,
      'System Architecture': 4.5,
      'Concurrency & Async': 8.0,
      'Docker & CI/CD': 7.5,
    },
  },
];

const SKILLS = [
  'Redis & Caching',
  'SQL & Indexing',
  'System Architecture',
  'Concurrency & Async',
  'Docker & CI/CD',
];

export const HODHeatmap: React.FC = () => {
  const [students] = useState<StudentSkillRecord[]>(INITIAL_STUDENTS);
  const [selectedCell, setSelectedCell] = useState<{ student: StudentSkillRecord; skill: string; score: number } | null>(null);
  const [taskDescription, setTaskDescription] = useState('');
  const [assignedSuccess, setAssignedSuccess] = useState<string | null>(null);

  // Compute column averages
  const skillAverages: Record<string, number> = {};
  SKILLS.forEach((skill) => {
    const total = students.reduce((acc, s) => acc + (s.scores[skill] || 0), 0);
    skillAverages[skill] = Number((total / students.length).toFixed(1));
  });

  const getScoreColor = (score: number) => {
    if (score >= 7.5) {
      return 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800';
    }
    if (score >= 5.0) {
      return 'bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800';
    }
    return 'bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300 border-rose-200 dark:border-rose-800';
  };

  const handleOpenAssignModal = (student: StudentSkillRecord, skill: string, score: number) => {
    setSelectedCell({ student, skill, score });
    setTaskDescription(`Complete deep-dive remediation module on ${skill}. Practice implementation and pass a graded assessment interview.`);
  };

  const handleAssignTask = () => {
    if (!selectedCell) return;
    setAssignedSuccess(`Remediation task on '${selectedCell.skill}' assigned to ${selectedCell.student.name} (${selectedCell.student.rollNumber}).`);
    setSelectedCell(null);
    setTimeout(() => setAssignedSuccess(null), 5000);
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-blue-600 dark:text-cyan-400 uppercase tracking-wider mb-1">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>HOD Analytics & Placement Readiness</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            Department Skill Competency Heatmap
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Department of Computer Science & Engineering | {students.length} Evaluated Candidates
          </p>
        </div>

        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-emerald-500" />
            <span className="text-slate-600 dark:text-slate-400 font-medium">Proficient (≥7.5)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-amber-500" />
            <span className="text-slate-600 dark:text-slate-400 font-medium">Moderate (5.0–7.4)</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded bg-rose-500" />
            <span className="text-slate-600 dark:text-slate-400 font-medium">Weak (&lt;5.0)</span>
          </div>
        </div>
      </div>

      {assignedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200 flex items-center space-x-3 text-xs font-semibold">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <span>{assignedSuccess}</span>
        </div>
      )}

      {/* Heatmap Table */}
      <div className="rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400">
                <th className="p-4 font-bold">Student Name</th>
                <th className="p-4 font-bold">Roll No</th>
                {SKILLS.map((skill) => (
                  <th key={skill} className="p-4 font-bold text-center">
                    {skill}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60">
              {students.map((student) => (
                <tr key={student.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/30 transition-colors">
                  <td className="p-4 font-bold text-slate-900 dark:text-white whitespace-nowrap">
                    {student.name}
                  </td>
                  <td className="p-4 text-slate-500 dark:text-slate-400 font-mono text-[11px]">
                    {student.rollNumber}
                  </td>
                  {SKILLS.map((skill) => {
                    const score = student.scores[skill] || 0;
                    return (
                      <td key={skill} className="p-3 text-center">
                        <button
                          onClick={() => handleOpenAssignModal(student, skill, score)}
                          title="Click to assign remediation task"
                          className={`w-14 py-1.5 rounded-xl font-bold font-mono text-xs border transition-transform hover:scale-105 cursor-pointer ${getScoreColor(score)}`}
                        >
                          {score.toFixed(1)}
                        </button>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-blue-50/60 dark:bg-blue-950/30 font-bold border-t-2 border-blue-200 dark:border-blue-900">
                <td className="p-4 text-blue-900 dark:text-cyan-300">Department Average</td>
                <td className="p-4 text-blue-700 dark:text-cyan-400 text-[11px]">AVG</td>
                {SKILLS.map((skill) => {
                  const avg = skillAverages[skill];
                  return (
                    <td key={skill} className="p-4 text-center font-mono text-xs text-blue-900 dark:text-cyan-300">
                      {avg.toFixed(1)}
                    </td>
                  );
                })}
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Click-to-Assign Remediation Modal */}
      {selectedCell && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-md w-full p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-900 shadow-2xl space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2 text-xs font-bold text-blue-600 dark:text-cyan-400 uppercase tracking-wider">
                <PlusCircle className="w-4 h-4" />
                <span>Assign Remediation Task</span>
              </div>
              <button
                onClick={() => setSelectedCell(null)}
                className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div>
              <h3 className="text-base font-black text-slate-900 dark:text-white">
                {selectedCell.student.name} ({selectedCell.student.rollNumber})
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Target Skill: <span className="font-semibold text-slate-700 dark:text-slate-200">{selectedCell.skill}</span> (Current: <span className="font-mono">{selectedCell.score.toFixed(1)}/10</span>)
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 mb-1">
                Task Description & Deliverable
              </label>
              <textarea
                rows={4}
                value={taskDescription}
                onChange={(e) => setTaskDescription(e.target.value)}
                className="w-full p-3 rounded-xl text-xs leading-relaxed bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
              />
            </div>

            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setSelectedCell(null)}
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleAssignTask}
                className="px-4 py-2 rounded-xl text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white shadow-md shadow-blue-500/20 transition-all"
              >
                Confirm Assignment
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
