import React, { useState } from 'react';
import { Sparkles, GraduationCap, Briefcase, ShieldAlert, ShieldCheck } from 'lucide-react';
import { StudentLogin } from './StudentLogin';
import { StaffLogin } from './StaffLogin';
import { HODLogin } from './HODLogin';
import type { UserRole } from '../../types';

interface LoginPortalProps {
  initialRole?: UserRole;
  onSuccess?: () => void;
}

export const LoginPortal: React.FC<LoginPortalProps> = ({ initialRole = 'student', onSuccess }) => {
  const [selectedRole, setSelectedRole] = useState<UserRole>(initialRole);

  return (
    <div className="min-h-[85vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full">
        {/* Institutional Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-tr from-blue-600 via-blue-500 to-cyan-400 text-white shadow-xl shadow-blue-500/25 mb-4">
            <Sparkles className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white tracking-tight">
            Axon Institutional Portal
          </h2>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400 font-medium">
            Department of Information Technology
          </p>
        </div>

        {/* Surface Switcher Tabs */}
        <div className="grid grid-cols-3 gap-1.5 p-1.5 bg-slate-100 dark:bg-[#0B0F19] rounded-2xl border border-slate-200 dark:border-blue-900/50 mb-6 shadow-sm">
          <button
            type="button"
            onClick={() => setSelectedRole('student')}
            className={`flex flex-col sm:flex-row items-center justify-center py-2.5 px-3 rounded-xl text-xs font-bold transition-all ${
              selectedRole === 'student'
                ? 'bg-white dark:bg-blue-600 text-blue-600 dark:text-white shadow-md shadow-blue-500/10'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <GraduationCap className="w-4 h-4 sm:mr-1.5 mb-1 sm:mb-0" />
            <span>Student</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedRole('staff')}
            className={`flex flex-col sm:flex-row items-center justify-center py-2.5 px-3 rounded-xl text-xs font-bold transition-all ${
              selectedRole === 'staff'
                ? 'bg-white dark:bg-indigo-600 text-indigo-600 dark:text-white shadow-md shadow-indigo-500/10'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <Briefcase className="w-4 h-4 sm:mr-1.5 mb-1 sm:mb-0" />
            <span>Staff</span>
          </button>

          <button
            type="button"
            onClick={() => setSelectedRole('hod')}
            className={`flex flex-col sm:flex-row items-center justify-center py-2.5 px-3 rounded-xl text-xs font-bold transition-all ${
              selectedRole === 'hod'
                ? 'bg-white dark:bg-amber-600 text-amber-600 dark:text-white shadow-md shadow-amber-500/10'
                : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200'
            }`}
          >
            <ShieldAlert className="w-4 h-4 sm:mr-1.5 mb-1 sm:mb-0" />
            <span>HOD</span>
          </button>
        </div>

        {/* Active Surface Form Card */}
        <div className="p-8 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-xl shadow-blue-950/5 dark:shadow-blue-950/20">
          {selectedRole === 'student' && <StudentLogin onSuccess={onSuccess} />}
          {selectedRole === 'staff' && <StaffLogin onSuccess={onSuccess} />}
          {selectedRole === 'hod' && <HODLogin onSuccess={onSuccess} />}
        </div>

        {/* Security & Integrity Footer */}
        <div className="mt-6 flex items-center justify-center space-x-2 text-[11px] text-slate-400 dark:text-slate-500">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          <span>Institutional JWT Role-Based Security Verified</span>
        </div>
      </div>
    </div>
  );
};
