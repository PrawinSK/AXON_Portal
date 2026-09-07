import React, { useEffect, useState } from 'react';
import {
  Sun,
  Moon,
  Sparkles,
  Cpu,
  BarChart3,
  Activity,
  ShieldCheck,
  LogOut,
  Users,
  BookOpen,
  ClipboardList,
  GraduationCap,
  Briefcase,
  ShieldAlert
} from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { AppTab } from '../types';

interface NavbarProps {
  activeTab: AppTab;
  onSelectTab: (tab: AppTab) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, onSelectTab }) => {
  const { theme, toggleTheme } = useTheme();
  const { user, role, logout } = useAuth();
  const [backendStatus, setBackendStatus] = useState<{ online: boolean; capacity: string }>({
    online: false,
    capacity: 'Checking...',
  });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const res = await api.checkBackendHealth();
        setBackendStatus({
          online: true,
          capacity: role === 'hod' ? (res.pool_capacity || '50 Keys / 750 RPM') : 'Institutional Node Online',
        });
      } catch {
        setBackendStatus({
          online: false,
          capacity: 'Backend Offline',
        });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, [role]);

  const getRoleBadge = () => {
    if (role === 'hod') {
      return (
        <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
          <ShieldAlert className="w-3 h-3" />
          <span>HOD Admin</span>
        </span>
      );
    }
    if (role === 'staff') {
      return (
        <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-indigo-100 dark:bg-indigo-950 text-indigo-800 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">
          <Briefcase className="w-3 h-3" />
          <span>Faculty Staff</span>
        </span>
      );
    }
    return (
      <span className="flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-cyan-300 border border-blue-200 dark:border-blue-800">
        <GraduationCap className="w-3 h-3" />
        <span>Student</span>
      </span>
    );
  };

  return (
    <header className="sticky top-0 z-50 transition-colors duration-200 backdrop-blur-md bg-white/90 dark:bg-[#030712]/90 border-b border-blue-100 dark:border-blue-950/60 shadow-sm dark:shadow-blue-950/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo & Node Status Indicator */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-blue-500 to-cyan-400 flex items-center justify-center shadow-md shadow-blue-500/20">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">
                Axon<span className="text-blue-600 dark:text-cyan-400">.ai</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950/80 dark:text-cyan-300 border border-blue-200 dark:border-blue-800/60">
                Institutional
              </span>
            </div>
            <div className="flex items-center space-x-1.5 text-xs text-slate-500 dark:text-slate-400">
              <span className={`w-2 h-2 rounded-full ${backendStatus.online ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'}`} />
              <span className="font-medium text-[11px]">{backendStatus.capacity}</span>
            </div>
          </div>
        </div>

        {/* Dynamic Role-Based Navigation Tabs */}
        <nav className="hidden md:flex items-center space-x-1 p-1 bg-slate-100/80 dark:bg-[#0B0F19] rounded-xl border border-slate-200/60 dark:border-blue-900/40">
          {/* STUDENT TABS */}
          {role === 'student' && (
            <>
              <button
                onClick={() => onSelectTab('interview')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'interview'
                    ? 'bg-white text-blue-600 shadow-sm dark:bg-blue-600 dark:text-white dark:shadow-blue-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Cpu className="w-4 h-4" />
                <span>Interview Room</span>
              </button>

              <button
                onClick={() => onSelectTab('my-tasks')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'my-tasks'
                    ? 'bg-white text-blue-600 shadow-sm dark:bg-blue-600 dark:text-white dark:shadow-blue-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>My Remediation Tasks</span>
              </button>
            </>
          )}

          {/* STAFF TABS */}
          {role === 'staff' && (
            <>
              <button
                onClick={() => onSelectTab('students')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'students'
                    ? 'bg-white text-indigo-600 shadow-sm dark:bg-indigo-600 dark:text-white dark:shadow-indigo-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>Student Profiles</span>
              </button>

              <button
                onClick={() => onSelectTab('tasks')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'tasks'
                    ? 'bg-white text-indigo-600 shadow-sm dark:bg-indigo-600 dark:text-white dark:shadow-indigo-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <ClipboardList className="w-4 h-4" />
                <span>Remediation Tasks</span>
              </button>
            </>
          )}

          {/* HOD TABS (Strictly holds 50-Key Pool and Full Department Heatmap) */}
          {role === 'hod' && (
            <>
              <button
                onClick={() => onSelectTab('students')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'students'
                    ? 'bg-white text-amber-600 shadow-sm dark:bg-amber-600 dark:text-white dark:shadow-amber-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Users className="w-4 h-4" />
                <span>Student Profiles</span>
              </button>

              <button
                onClick={() => onSelectTab('hod')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'hod'
                    ? 'bg-white text-amber-600 shadow-sm dark:bg-amber-600 dark:text-white dark:shadow-amber-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Department Heatmap</span>
              </button>

              <button
                onClick={() => onSelectTab('pool')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'pool'
                    ? 'bg-white text-amber-600 shadow-sm dark:bg-amber-600 dark:text-white dark:shadow-amber-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <Activity className="w-4 h-4" />
                <span>50-Key Pool (Live)</span>
              </button>

              <button
                onClick={() => onSelectTab('tasks')}
                className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  activeTab === 'tasks'
                    ? 'bg-white text-amber-600 shadow-sm dark:bg-amber-600 dark:text-white dark:shadow-amber-500/20'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
                }`}
              >
                <ClipboardList className="w-4 h-4" />
                <span>Remediation Tasks</span>
              </button>
            </>
          )}
        </nav>

        {/* User Badge, Theme Toggle & Logout */}
        <div className="flex items-center space-x-3">
          {user && (
            <div className="flex items-center space-x-2.5">
              <div className="hidden sm:block text-right">
                <div className="text-xs font-extrabold text-slate-900 dark:text-white leading-tight">
                  {user.name}
                </div>
                <div className="text-[10px] text-slate-500 dark:text-slate-400 font-mono">
                  {user.roll_number || user.email || user.department}
                </div>
              </div>

              {getRoleBadge()}

              <button
                onClick={logout}
                title="Sign Out"
                className="p-2 rounded-xl border border-slate-200 dark:border-blue-900/60 bg-slate-50 dark:bg-[#0B0F19] text-slate-500 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-all shadow-sm"
              >
                <LogOut className="w-4 h-4" />
              </button>
            </div>
          )}

          <div className="hidden sm:flex items-center space-x-1.5 px-2.5 py-1.5 rounded-xl bg-slate-50 dark:bg-slate-900/60 border border-slate-200 dark:border-slate-800 text-[11px] text-slate-600 dark:text-slate-300">
            <ShieldCheck className="w-3.5 h-3.5 text-blue-600 dark:text-cyan-400" />
            <span>Proctored</span>
          </div>

          <button
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="p-2 rounded-xl border transition-all duration-200 bg-white hover:bg-slate-50 text-slate-700 border-slate-200 shadow-sm dark:bg-[#0B0F19] dark:hover:bg-slate-900 dark:text-cyan-300 dark:border-blue-900/60 dark:hover:border-blue-700"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-amber-400 animate-spin-slow" />
            ) : (
              <Moon className="w-4 h-4 text-blue-600" />
            )}
          </button>
        </div>

      </div>
    </header>
  );
};
