import React, { useEffect, useState } from 'react';
import {
  Search,
  PlusCircle,
  CheckCircle2,
  Clock,
  BookOpen,
  X,
  Loader2,
  UserPlus,
  GraduationCap,
  KeyRound,
  AlertCircle,
  Briefcase,
  Mail,
  ShieldCheck,
  Building2,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import type { DepartmentStudentProfile, TaskItem, StaffProfile } from '../types';

interface StudentProfilesViewProps {
  userRole: 'staff' | 'hod';
}

export const StudentProfilesView: React.FC<StudentProfilesViewProps> = ({ userRole }) => {
  const [students, setStudents] = useState<DepartmentStudentProfile[]>([]);
  const [staffList, setStaffList] = useState<StaffProfile[]>([]);
  const [allTasks, setAllTasks] = useState<TaskItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [directoryTab, setDirectoryTab] = useState<'students' | 'staff'>('students');
  const [searchTerm, setSearchTerm] = useState<string>('');

  // Assign Task Modal State
  const [isAssignModalOpen, setIsAssignModalOpen] = useState<boolean>(false);
  const [assignStudentId, setAssignStudentId] = useState<string>('');
  const [targetSkill, setTargetSkill] = useState<string>('');
  const [taskDescription, setTaskDescription] = useState<string>('');
  const [dueDate, setDueDate] = useState<string>('2026-10-30');
  const [isSubmittingTask, setIsSubmittingTask] = useState<boolean>(false);
  const [assignmentSuccess, setAssignmentSuccess] = useState<string | null>(null);

  // Add New Student Modal State (Staff & HOD)
  const [isCreateStudentModalOpen, setIsCreateStudentModalOpen] = useState<boolean>(false);
  const [newRollNumber, setNewRollNumber] = useState<string>('');
  const [newName, setNewName] = useState<string>('');
  const [newPassword, setNewPassword] = useState<string>('student@123');
  const [newDepartment, setNewDepartment] = useState<string>('Information Technology');
  const [isCreatingStudent, setIsCreatingStudent] = useState<boolean>(false);
  const [createStudentSuccess, setCreateStudentSuccess] = useState<string | null>(null);
  const [createStudentError, setCreateStudentError] = useState<string | null>(null);

  // Add New Staff Modal State (Strictly HOD Only)
  const [isCreateStaffModalOpen, setIsCreateStaffModalOpen] = useState<boolean>(false);
  const [newStaffEmail, setNewStaffEmail] = useState<string>('');
  const [newStaffName, setNewStaffName] = useState<string>('');
  const [newStaffPassword, setNewStaffPassword] = useState<string>('staff@123');
  const [newStaffDepartment, setNewStaffDepartment] = useState<string>('Information Technology');
  const [isCreatingStaff, setIsCreatingStaff] = useState<boolean>(false);
  const [createStaffSuccess, setCreateStaffSuccess] = useState<string | null>(null);
  const [createStaffError, setCreateStaffError] = useState<string | null>(null);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [studentData, taskData, staffData] = await Promise.all([
        api.getDepartmentStudents(),
        api.getAllTasks(),
        api.getAllStaff().catch(() => []),
      ]);
      setStudents(studentData || []);
      setAllTasks(taskData || []);
      setStaffList(staffData || []);
    } catch (err) {
      console.error('Failed to load institutional directory data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleOpenAssignModal = (studentId?: string, defaultSkill?: string) => {
    setAssignStudentId(studentId || (students[0]?.id ?? ''));
    setTargetSkill(defaultSkill || '');
    setTaskDescription('');
    setDueDate('2026-10-30');
    setAssignmentSuccess(null);
    setIsAssignModalOpen(true);
  };

  const handleAssignTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignStudentId || !targetSkill.trim() || !taskDescription.trim()) return;

    setIsSubmittingTask(true);
    try {
      await api.assignTask({
        student_id: assignStudentId,
        target_skill: targetSkill.trim(),
        description: taskDescription.trim(),
        due_date: dueDate,
      });
      setAssignmentSuccess(`Remediation task successfully assigned!`);
      await fetchData();
      setTimeout(() => {
        setIsAssignModalOpen(false);
        setAssignmentSuccess(null);
      }, 1200);
    } catch (err: any) {
      alert(`Assignment failed: ${err.message || 'Unknown error'}`);
    } finally {
      setIsSubmittingTask(false);
    }
  };

  const handleCreateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateStudentError(null);
    setCreateStudentSuccess(null);

    const roll = newRollNumber.trim().toUpperCase();
    const name = newName.trim();
    const pwd = newPassword.trim();
    const dept = newDepartment.trim() || 'Information Technology';

    if (!roll || !name || !pwd) {
      setCreateStudentError('Please fill in all required fields.');
      return;
    }

    setIsCreatingStudent(true);
    try {
      await api.createStudent({
        roll_number: roll,
        name: name,
        password: pwd,
        department: dept,
      });
      setCreateStudentSuccess(`Student profile for ${name} (${roll}) created on Axon!`);
      await fetchData();
      setDirectoryTab('students');
      setSearchTerm(roll); // Highlight the newly created student immediately in search
      setTimeout(() => {
        setIsCreateStudentModalOpen(false);
        setNewRollNumber('');
        setNewName('');
        setNewPassword('student@123');
        setCreateStudentSuccess(null);
      }, 1400);
    } catch (err: any) {
      setCreateStudentError(err.message || 'Failed to create student profile.');
    } finally {
      setIsCreatingStudent(false);
    }
  };

  const handleCreateStaff = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateStaffError(null);
    setCreateStaffSuccess(null);

    const email = newStaffEmail.trim().toLowerCase();
    const name = newStaffName.trim();
    const pwd = newStaffPassword.trim();
    const dept = newStaffDepartment.trim() || 'Information Technology';

    if (!email || !name || !pwd) {
      setCreateStaffError('Please fill in all required fields.');
      return;
    }

    setIsCreatingStaff(true);
    try {
      await api.createStaff({
        email: email,
        name: name,
        password: pwd,
        department: dept,
      });
      setCreateStaffSuccess(`Faculty profile for ${name} (${email}) registered on Axon!`);
      await fetchData();
      setDirectoryTab('staff');
      setSearchTerm(name); // Highlight the newly registered faculty immediately in search
      setTimeout(() => {
        setIsCreateStaffModalOpen(false);
        setNewStaffEmail('');
        setNewStaffName('');
        setNewStaffPassword('staff@123');
        setCreateStaffSuccess(null);
      }, 1400);
    } catch (err: any) {
      setCreateStaffError(err.message || 'Failed to create faculty profile.');
    } finally {
      setIsCreatingStaff(false);
    }
  };

  // Safe search queries
  const cleanSearch = searchTerm.toLowerCase().trim();

  const filteredStudents = students.filter((s) => {
    if (!cleanSearch) return true;
    const name = (s.name || '').toLowerCase();
    const roll = (s.roll_number || '').toLowerCase();
    const dept = (s.department || '').toLowerCase();
    const email = (s.email || '').toLowerCase();
    return name.includes(cleanSearch) || roll.includes(cleanSearch) || dept.includes(cleanSearch) || email.includes(cleanSearch);
  });

  const filteredStaff = staffList.filter((m) => {
    if (!cleanSearch) return true;
    const name = (m.name || '').toLowerCase();
    const email = (m.email || '').toLowerCase();
    const dept = (m.department || '').toLowerCase();
    const role = (m.role || '').toLowerCase();
    return name.includes(cleanSearch) || email.includes(cleanSearch) || dept.includes(cleanSearch) || role.includes(cleanSearch);
  });

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header Banner */}
      <div className="p-6 rounded-3xl bg-gradient-to-r from-blue-600/10 via-indigo-500/10 to-transparent border border-blue-200 dark:border-blue-900/60 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-blue-600 dark:text-cyan-400 font-bold text-xs uppercase tracking-wider mb-1">
            <Building2 className="w-4 h-4" />
            <span>Department of Information Technology</span>
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">
            {userRole === 'hod' ? 'Institutional Directory & Oversight (Dr. Selvi, HOD)' : 'Department Directory & Grading (Miss. Ramya Tamizharasi)'}
          </h2>
          <p className="text-xs text-slate-600 dark:text-slate-400 mt-1 max-w-2xl">
            {userRole === 'hod'
              ? 'Complete institutional authority: register faculty staff, enroll candidates, inspect multi-dimensional readiness, and assign remediation tasks.'
              : 'Faculty portal: enroll new candidates, monitor student cohort readiness, and assign remediation tasks.'}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          {/* HOD-Only: Add Faculty / Staff Button */}
          {userRole === 'hod' && (
            <button
              onClick={() => setIsCreateStaffModalOpen(true)}
              className="flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-500/20 transition-all cursor-pointer"
            >
              <Briefcase className="w-4 h-4" />
              <span>Add Faculty Staff</span>
            </button>
          )}

          {/* Both Staff & HOD can add students */}
          <button
            onClick={() => setIsCreateStudentModalOpen(true)}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-emerald-600 hover:bg-emerald-700 shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
          >
            <UserPlus className="w-4 h-4" />
            <span>Add Student to Axon</span>
          </button>

          <button
            onClick={() => handleOpenAssignModal()}
            className="flex items-center space-x-2 px-4 py-2.5 rounded-xl font-bold text-xs text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all cursor-pointer"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Assign Remediation Task</span>
          </button>
        </div>
      </div>

      {/* Directory Tab Switcher & Search Bar */}
      <div className="space-y-3">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 rounded-2xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-sm">
          {/* Tab Switcher Buttons */}
          <div className="flex items-center p-1 rounded-xl bg-slate-100 dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-900/60 w-full sm:w-auto">
            <button
              onClick={() => setDirectoryTab('students')}
              className={`flex-1 sm:flex-initial flex items-center justify-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                directoryTab === 'students'
                  ? 'bg-white dark:bg-blue-600 text-blue-600 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <GraduationCap className="w-4 h-4" />
              <span>Student Cohort</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                directoryTab === 'students'
                  ? 'bg-blue-100 dark:bg-blue-700 text-blue-700 dark:text-blue-100'
                  : 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
              }`}>
                {filteredStudents.length}
              </span>
            </button>

            <button
              onClick={() => setDirectoryTab('staff')}
              className={`flex-1 sm:flex-initial flex items-center justify-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                directoryTab === 'staff'
                  ? 'bg-white dark:bg-indigo-600 text-indigo-600 dark:text-white shadow-sm'
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
              }`}
            >
              <Briefcase className="w-4 h-4" />
              <span>Faculty & Staff</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold ${
                directoryTab === 'staff'
                  ? 'bg-indigo-100 dark:bg-indigo-700 text-indigo-700 dark:text-indigo-100'
                  : 'bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400'
              }`}>
                {filteredStaff.length}
              </span>
            </button>
          </div>

          {/* Search Input Bar */}
          <div className="relative w-full sm:w-96">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder={
                directoryTab === 'students'
                  ? "Search by student name or roll number (e.g. 21IT001)..."
                  : "Search faculty by name, email, or department..."
              }
              className="w-full pl-10 pr-9 py-2 text-xs rounded-xl border border-slate-200 dark:border-blue-900 bg-slate-50 dark:bg-[#0B0F19] text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/50"
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

        {/* Cross-Tab Search Suggestions */}
        {cleanSearch && directoryTab === 'students' && filteredStudents.length === 0 && filteredStaff.length > 0 && (
          <div className="p-3 rounded-xl bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-900 flex items-center justify-between text-xs text-indigo-800 dark:text-indigo-200">
            <span>Found <strong>{filteredStaff.length}</strong> matching result(s) in <strong>Faculty & Staff</strong>.</span>
            <button
              onClick={() => setDirectoryTab('staff')}
              className="font-bold underline hover:text-indigo-600 dark:hover:text-indigo-400 cursor-pointer"
            >
              View Faculty Results →
            </button>
          </div>
        )}
        {cleanSearch && directoryTab === 'staff' && filteredStaff.length === 0 && filteredStudents.length > 0 && (
          <div className="p-3 rounded-xl bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900 flex items-center justify-between text-xs text-blue-800 dark:text-blue-200">
            <span>Found <strong>{filteredStudents.length}</strong> matching candidate(s) in <strong>Student Cohort</strong>.</span>
            <button
              onClick={() => setDirectoryTab('students')}
              className="font-bold underline hover:text-blue-600 dark:hover:text-cyan-400 cursor-pointer"
            >
              View Student Results →
            </button>
          </div>
        )}
      </div>

      {/* DIRECTORY CONTENT */}
      {isLoading ? (
        <div className="text-center py-20">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600 mx-auto mb-3" />
          <p className="text-xs font-semibold text-slate-500 dark:text-slate-400">Loading institutional directory...</p>
        </div>
      ) : directoryTab === 'students' ? (
        /* TAB 1: STUDENT COHORT GRID */
        filteredStudents.length === 0 ? (
          <div className="p-12 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 text-center space-y-3">
            <GraduationCap className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto" />
            <h3 className="font-extrabold text-lg text-slate-800 dark:text-slate-200">No Students Found</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              {cleanSearch
                ? `No candidate roll numbers or names matched "${searchTerm}".`
                : "No student profiles are currently enrolled in the department."}
            </p>
            {cleanSearch ? (
              <button
                onClick={() => setSearchTerm('')}
                className="px-4 py-2 rounded-xl text-xs font-bold text-blue-600 dark:text-cyan-400 bg-blue-50 dark:bg-blue-950/60 border border-blue-200 dark:border-blue-800 hover:bg-blue-100 cursor-pointer"
              >
                Clear Search Filter
              </button>
            ) : (
              <button
                onClick={() => setIsCreateStudentModalOpen(true)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm cursor-pointer"
              >
                Add First Student
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredStudents.map((s) => {
              const studentTasks = allTasks.filter((t) => t.student_id === s.id);
              const pendingTasks = studentTasks.filter((t) => t.status !== 'completed');

              const score = s.metrics?.overall_score ?? 7.5;
              const scoreColor =
                score >= 8.0
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : score >= 7.0
                  ? 'text-blue-600 dark:text-cyan-400'
                  : 'text-amber-600 dark:text-amber-400';

              const radar = s.metrics?.radar ?? { depth: 7.5, logic: 7.8, communication: 8.0 };
              const weakSkills = s.metrics?.weak_skills ?? ['System Architecture', 'API Caching'];
              const readiness = s.metrics?.readiness_band ?? 'Enrolled Candidate';

              return (
                <div
                  key={s.id}
                  className="p-5 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 shadow-sm hover:border-blue-300 dark:hover:border-blue-800 transition-all flex flex-col justify-between"
                >
                  <div>
                    {/* Top Bar: Name, Roll Number, Readiness Badge */}
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <div>
                        <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                          {s.name}
                        </h3>
                        <div className="flex items-center space-x-2 mt-0.5">
                          <span className="font-mono text-xs font-bold text-blue-600 dark:text-cyan-400 bg-blue-50 dark:bg-blue-950/60 px-2 py-0.5 rounded-md border border-blue-200 dark:border-blue-900">
                            {s.roll_number}
                          </span>
                          <span className="text-[11px] text-slate-500 dark:text-slate-400">
                            {s.department}
                          </span>
                        </div>
                      </div>

                      <div className="text-right">
                        <div className={`text-2xl font-black ${scoreColor}`}>{score.toFixed(1)}</div>
                        <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">
                          {readiness}
                        </span>
                      </div>
                    </div>

                    {/* Multi-Dimensional Metrics Bar */}
                    <div className="grid grid-cols-3 gap-2 p-2.5 rounded-2xl bg-slate-50 dark:bg-[#0B0F19] border border-slate-100 dark:border-blue-950 mb-4 text-center">
                      <div>
                        <span className="block text-xs font-bold text-slate-700 dark:text-slate-300">
                          {radar.depth}
                        </span>
                        <span className="text-[9px] uppercase font-bold text-slate-400">Tech Depth</span>
                      </div>
                      <div>
                        <span className="block text-xs font-bold text-slate-700 dark:text-slate-300">
                          {radar.logic}
                        </span>
                        <span className="text-[9px] uppercase font-bold text-slate-400">Logic</span>
                      </div>
                      <div>
                        <span className="block text-xs font-bold text-slate-700 dark:text-slate-300">
                          {radar.communication}
                        </span>
                        <span className="text-[9px] uppercase font-bold text-slate-400">Comms</span>
                      </div>
                    </div>

                    {/* Weak Skills Section */}
                    <div className="mb-4">
                      <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                        Identified Skill Deficiencies
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        {weakSkills.map((skill, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleOpenAssignModal(s.id, skill)}
                            title="Click to assign targeted remediation task for this skill"
                            className="px-2 py-0.5 rounded-lg text-[10px] font-semibold bg-rose-50 dark:bg-rose-950/50 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900/60 hover:bg-rose-100 dark:hover:bg-rose-900/80 transition-all flex items-center space-x-1 cursor-pointer"
                          >
                            <span>{skill}</span>
                            <PlusCircle className="w-2.5 h-2.5 text-rose-500" />
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Card Footer: Pending Tasks & Action */}
                  <div className="pt-3 border-t border-slate-100 dark:border-blue-950 flex items-center justify-between">
                    <div className="flex items-center space-x-1 text-xs text-slate-500 dark:text-slate-400">
                      <Clock className="w-3.5 h-3.5 text-amber-500" />
                      <span>{pendingTasks.length} pending tasks</span>
                    </div>

                    <button
                      onClick={() => handleOpenAssignModal(s.id)}
                      className="px-3 py-1.5 rounded-xl font-bold text-xs bg-slate-100 dark:bg-blue-950 hover:bg-blue-50 dark:hover:bg-blue-900/60 text-blue-700 dark:text-cyan-300 border border-slate-200 dark:border-blue-800 transition-all cursor-pointer"
                    >
                      Assign Task
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )
      ) : (
        /* TAB 2: FACULTY & STAFF GRID */
        filteredStaff.length === 0 ? (
          <div className="p-12 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950/80 text-center space-y-3">
            <Briefcase className="w-12 h-12 text-slate-300 dark:text-slate-700 mx-auto" />
            <h3 className="font-extrabold text-lg text-slate-800 dark:text-slate-200">No Faculty Members Found</h3>
            <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto">
              {cleanSearch
                ? `No faculty accounts matched "${searchTerm}".`
                : "No faculty accounts are registered in the directory."}
            </p>
            {cleanSearch ? (
              <button
                onClick={() => setSearchTerm('')}
                className="px-4 py-2 rounded-xl text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-200 dark:border-indigo-800 hover:bg-indigo-100 cursor-pointer"
              >
                Clear Search Filter
              </button>
            ) : userRole === 'hod' && (
              <button
                onClick={() => setIsCreateStaffModalOpen(true)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm cursor-pointer"
              >
                Register Faculty Member
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredStaff.map((staff) => {
              const isHOD = staff.role === 'hod';
              return (
                <div
                  key={staff.id}
                  className={`p-6 rounded-3xl bg-white dark:bg-[#030712] border shadow-sm transition-all flex flex-col justify-between ${
                    isHOD
                      ? 'border-indigo-300 dark:border-indigo-800/80 bg-gradient-to-b from-indigo-500/5 to-transparent'
                      : 'border-slate-200 dark:border-blue-950/80 hover:border-indigo-200'
                  }`}
                >
                  <div>
                    {/* Header with Role Tag */}
                    <div className="flex items-start justify-between gap-2 mb-3">
                      <div>
                        <h3 className="font-extrabold text-base text-slate-900 dark:text-white">
                          {staff.name}
                        </h3>
                        <div className="flex items-center space-x-1.5 mt-1 text-slate-500 dark:text-slate-400 text-xs">
                          <Mail className="w-3.5 h-3.5 text-indigo-500" />
                          <span className="font-mono text-[11px]">{staff.email}</span>
                        </div>
                      </div>

                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${
                        isHOD
                          ? 'bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800'
                          : 'bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-cyan-300 border border-blue-200 dark:border-blue-800'
                      }`}>
                        {isHOD ? 'Head of Department' : 'Faculty Staff'}
                      </span>
                    </div>

                    {/* Department & ID Details */}
                    <div className="p-3 rounded-2xl bg-slate-50 dark:bg-[#0B0F19] border border-slate-100 dark:border-blue-950 space-y-2 mb-4 text-xs">
                      <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                        <span className="text-[11px] font-semibold">Department</span>
                        <span className="font-bold text-slate-900 dark:text-slate-200">{staff.department}</span>
                      </div>
                      <div className="flex items-center justify-between text-slate-600 dark:text-slate-400">
                        <span className="text-[11px] font-semibold">Institutional UID</span>
                        <span className="font-mono text-[10px] text-slate-500 dark:text-slate-400">{staff.id}</span>
                      </div>
                    </div>

                    {/* System Access Badges */}
                    <div className="space-y-1.5 text-[11px] text-slate-600 dark:text-slate-400">
                      <span className="block text-[10px] font-bold uppercase tracking-wider text-slate-400">
                        Institutional Privileges
                      </span>
                      <div className="flex flex-wrap gap-1.5">
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 text-[10px]">
                          <ShieldCheck className="w-3 h-3 text-emerald-500" />
                          <span>Student Enrollment</span>
                        </span>
                        <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-slate-100 dark:bg-slate-900 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 text-[10px]">
                          <BookOpen className="w-3 h-3 text-blue-500" />
                          <span>Task Assignment</span>
                        </span>
                        {isHOD && (
                          <span className="inline-flex items-center space-x-1 px-2 py-0.5 rounded-md bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-900 text-[10px]">
                            <Sparkles className="w-3 h-3 text-indigo-500" />
                            <span>Staff Registration</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Footer: Node Status */}
                  <div className="pt-3 mt-4 border-t border-slate-100 dark:border-blue-950 flex items-center justify-between text-xs">
                    <div className="flex items-center space-x-1.5 text-emerald-600 dark:text-emerald-400 font-semibold text-[11px]">
                      <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                      <span>Active Institutional Member</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">Verified Node</span>
                  </div>
                </div>
              );
            })}
          </div>
        )
      )}

      {/* MODAL 1: Add New Student Modal (Staff & HOD) */}
      {isCreateStudentModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-md w-full p-6 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
            <button
              onClick={() => setIsCreateStudentModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-5">
              <div className="w-10 h-10 rounded-2xl bg-emerald-100 dark:bg-emerald-950 flex items-center justify-center text-emerald-600 dark:text-emerald-400">
                <GraduationCap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">
                  Add Student to Axon
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Create an institutional student profile with login access
                </p>
              </div>
            </div>

            {createStudentError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{createStudentError}</span>
              </div>
            )}

            {createStudentSuccess && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-emerald-700 dark:text-emerald-300 text-xs flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>{createStudentSuccess}</span>
              </div>
            )}

            <form onSubmit={handleCreateStudent} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Student Roll Number / Register ID *
                </label>
                <input
                  type="text"
                  value={newRollNumber}
                  onChange={(e) => setNewRollNumber(e.target.value.toUpperCase())}
                  placeholder="e.g. 21IT105"
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Student Full Name *
                </label>
                <input
                  type="text"
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="e.g. Suresh Kumar M."
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>Student Initial Password *</span>
                  <span className="text-[10px] text-slate-400 font-normal lowercase">student uses this to sign in</span>
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="student@123"
                    required
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs font-mono focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Department
                </label>
                <input
                  type="text"
                  value={newDepartment}
                  onChange={(e) => setNewDepartment(e.target.value)}
                  placeholder="Information Technology"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-emerald-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsCreateStudentModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreatingStudent}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 transition-all shadow-md shadow-emerald-500/25 flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {isCreatingStudent ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Creating Profile...</span>
                    </>
                  ) : (
                    <span>Create Student Profile</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 2: Add Faculty / Staff Modal (Strictly HOD Only) */}
      {isCreateStaffModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-md w-full p-6 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
            <button
              onClick={() => setIsCreateStaffModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-5">
              <div className="w-10 h-10 rounded-2xl bg-indigo-100 dark:bg-indigo-950 flex items-center justify-center text-indigo-600 dark:text-indigo-400">
                <Briefcase className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">
                  Add Faculty / Staff Member
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Register official faculty account with grading & student creation access
                </p>
              </div>
            </div>

            {createStaffError && (
              <div className="mb-4 p-3 rounded-xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center space-x-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                <span>{createStaffError}</span>
              </div>
            )}

            {createStaffSuccess && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-emerald-700 dark:text-emerald-300 text-xs flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>{createStaffSuccess}</span>
              </div>
            )}

            <form onSubmit={handleCreateStaff} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Faculty Official Email *
                </label>
                <input
                  type="email"
                  value={newStaffEmail}
                  onChange={(e) => setNewStaffEmail(e.target.value)}
                  placeholder="e.g. anbarasan.staff@axon.edu"
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Faculty Full Name *
                </label>
                <input
                  type="text"
                  value={newStaffName}
                  onChange={(e) => setNewStaffName(e.target.value)}
                  placeholder="e.g. Mr. K. Anbarasan"
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5 flex items-center justify-between">
                  <span>Faculty Initial Password *</span>
                  <span className="text-[10px] text-slate-400 font-normal lowercase">faculty uses this to sign in</span>
                </label>
                <div className="relative">
                  <KeyRound className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    value={newStaffPassword}
                    onChange={(e) => setNewStaffPassword(e.target.value)}
                    placeholder="staff@123"
                    required
                    className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs font-mono focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Department
                </label>
                <input
                  type="text"
                  value={newStaffDepartment}
                  onChange={(e) => setNewStaffDepartment(e.target.value)}
                  placeholder="Information Technology"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsCreateStaffModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isCreatingStaff}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 transition-all shadow-md shadow-indigo-500/25 flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {isCreatingStaff ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Registering Faculty...</span>
                    </>
                  ) : (
                    <span>Register Faculty Member</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL 3: Assign Task Modal */}
      {isAssignModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="max-w-md w-full p-6 rounded-3xl bg-white dark:bg-[#030712] border border-slate-200 dark:border-blue-950 shadow-2xl relative animate-in fade-in zoom-in-95 duration-200">
            <button
              onClick={() => setIsAssignModalOpen(false)}
              className="absolute top-5 right-5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex items-center space-x-2.5 mb-5">
              <div className="w-10 h-10 rounded-2xl bg-blue-100 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-cyan-400">
                <BookOpen className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-lg text-slate-900 dark:text-white">
                  Assign Remediation Task
                </h3>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Targeted learning assignment for student
                </p>
              </div>
            </div>

            {assignmentSuccess && (
              <div className="mb-4 p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-900 text-emerald-700 dark:text-emerald-300 text-xs flex items-center space-x-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span>{assignmentSuccess}</span>
              </div>
            )}

            <form onSubmit={handleAssignTask} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Select Candidate *
                </label>
                <select
                  value={assignStudentId}
                  onChange={(e) => setAssignStudentId(e.target.value)}
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="" disabled>-- Select Candidate --</option>
                  {students.map((st) => (
                    <option key={st.id} value={st.id}>
                      {st.name} — {st.roll_number} ({st.department})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Target Skill / Deficiency Area
                </label>
                <input
                  type="text"
                  value={targetSkill}
                  onChange={(e) => setTargetSkill(e.target.value)}
                  placeholder="e.g. Redis Cache Invalidation & CDC"
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Task Description & Requirements
                </label>
                <textarea
                  rows={3}
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  placeholder="Provide remediation criteria or reading list. Candidate clears task with a score >= 7.0 on graded assessment."
                  required
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1.5">
                  Completion Due Date
                </label>
                <input
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 dark:border-blue-950 bg-white dark:bg-[#0B0F19] text-slate-900 dark:text-white text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end space-x-2">
                <button
                  type="button"
                  onClick={() => setIsAssignModalOpen(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingTask}
                  className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 transition-all shadow-md shadow-blue-500/25 flex items-center space-x-1.5 disabled:opacity-50"
                >
                  {isSubmittingTask ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Assigning...</span>
                    </>
                  ) : (
                    <span>Assign Task</span>
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
