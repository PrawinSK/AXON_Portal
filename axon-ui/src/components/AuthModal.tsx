import React from 'react';
import { Key, UserCheck, ShieldCheck, Award, X, Copy, Check } from 'lucide-react';
import type { AppTab } from '../types';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectRole: (role: 'student' | 'staff' | 'hod', tab: AppTab) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onSelectRole }) => {
  const [copiedField, setCopiedField] = React.useState<string | null>(null);

  if (!isOpen) return null;

  const handleCopy = (text: string, fieldId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldId);
    setTimeout(() => setCopiedField(null), 2000);
  };

  const credentials = [
    {
      roleName: 'Student Portal (ERP Access)',
      icon: Award,
      badge: 'Student Role',
      badgeColor: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-cyan-300',
      loginField: 'Roll Number',
      loginValue: '21CS042',
      passwordValue: 'student@123',
      tab: 'interview' as AppTab,
      role: 'student' as const,
      description: 'Take adaptive, resume-grounded interviews, receive coaching, and view skill roadmaps.',
    },
    {
      roleName: 'Staff Portal (Faculty Access)',
      icon: UserCheck,
      badge: 'Faculty Role',
      badgeColor: 'bg-purple-100 text-purple-800 dark:bg-purple-950 dark:text-purple-300',
      loginField: 'Faculty Email',
      loginValue: 'staff@axon.edu',
      passwordValue: 'staff@123',
      tab: 'interview' as AppTab,
      role: 'staff' as const,
      description: 'Seed curriculum question banks, inspect student answers, and assign remediation tasks.',
    },
    {
      roleName: 'HOD Executive Portal (Admin Access)',
      icon: ShieldCheck,
      badge: 'HOD Executive',
      badgeColor: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300',
      loginField: 'HOD Email',
      loginValue: 'hod.cs@axon.edu',
      passwordValue: 'hod@123',
      tab: 'hod' as AppTab,
      role: 'hod' as const,
      description: 'Department-wide skill competency heatmap and 1-click batch remediation assignment.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="max-w-xl w-full p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-2xl space-y-6">
        
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-cyan-400 flex items-center justify-center">
              <Key className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-black text-slate-900 dark:text-white">
                Official Access Credentials & Passwords
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Pre-configured authentication credentials for institutional testing
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-4">
          {credentials.map((c) => {
            const Icon = c.icon;
            return (
              <div
                key={c.role}
                className="p-4 rounded-2xl bg-slate-50 dark:bg-slate-900/50 border border-slate-200/80 dark:border-slate-800/80 space-y-2.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className="w-4 h-4 text-blue-600 dark:text-cyan-400" />
                    <span className="font-bold text-xs text-slate-900 dark:text-white">
                      {c.roleName}
                    </span>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${c.badgeColor}`}>
                    {c.badge}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="p-2 rounded-xl bg-white dark:bg-[#030712] border border-slate-200/60 dark:border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-slate-400 block">{c.loginField}:</span>
                      <span className="font-mono font-bold text-slate-800 dark:text-slate-200">{c.loginValue}</span>
                    </div>
                    <button
                      onClick={() => handleCopy(c.loginValue, `${c.role}-user`)}
                      className="p-1 text-slate-400 hover:text-blue-600 dark:hover:text-cyan-400"
                      title="Copy"
                    >
                      {copiedField === `${c.role}-user` ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>

                  <div className="p-2 rounded-xl bg-white dark:bg-[#030712] border border-slate-200/60 dark:border-slate-800 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] text-slate-400 block">Password:</span>
                      <span className="font-mono font-bold text-emerald-600 dark:text-emerald-400">{c.passwordValue}</span>
                    </div>
                    <button
                      onClick={() => handleCopy(c.passwordValue, `${c.role}-pwd`)}
                      className="p-1 text-slate-400 hover:text-blue-600 dark:hover:text-cyan-400"
                      title="Copy Password"
                    >
                      {copiedField === `${c.role}-pwd` ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1">
                  <span className="text-[11px] text-slate-500 dark:text-slate-400 truncate max-w-[280px]">
                    {c.description}
                  </span>
                  <button
                    onClick={() => {
                      onSelectRole(c.role, c.tab);
                      onClose();
                    }}
                    className="px-3 py-1 rounded-lg text-xs font-bold bg-blue-600 hover:bg-blue-700 text-white dark:bg-blue-600 dark:hover:bg-blue-500 transition-all shadow-sm"
                  >
                    Quick Switch
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        <div className="text-center">
          <p className="text-[11px] text-slate-400">
            Click any <strong>Quick Switch</strong> button above to immediately load that view with valid credentials.
          </p>
        </div>

      </div>
    </div>
  );
};
