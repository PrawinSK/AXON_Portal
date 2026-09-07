import { useState, useEffect } from 'react';
import { ThemeProvider, useTheme } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { LoginPortal } from './components/auth/LoginPortal';
import { SetupScreen } from './components/SetupScreen';
import { InterviewRoom } from './components/InterviewRoom';
import { ScorecardView } from './components/ScorecardView';
import { StudentTasks } from './components/StudentTasks';
import { StudentProfilesView } from './components/StudentProfilesView';
import { DepartmentTasksView } from './components/DepartmentTasksView';
import { HODHeatmap } from './components/HODHeatmap';
import { KeyPoolMonitor } from './components/KeyPoolMonitor';
import { Loader2, Sun, Moon } from 'lucide-react';
import type {
  AppTab,
  StartInterviewResponse,
  SynthesisResponse,
} from './types';

export function AppContent() {
  const { theme, toggleTheme } = useTheme();
  const { user, role, isAuthenticated, isLoading } = useAuth();

  // Active Navigation Tab
  const [activeTab, setActiveTab] = useState<AppTab>('interview');

  // Targeted remediation skill passed to interview setup
  const [targetedSkill, setTargetedSkill] = useState<string | undefined>(undefined);

  // Interview Lifecycle States: 'setup' | 'interviewing' | 'concluded'
  const [interviewPhase, setInterviewPhase] = useState<'setup' | 'interviewing' | 'concluded'>('setup');
  const [activeSession, setActiveSession] = useState<StartInterviewResponse | null>(null);
  const [candidateName, setCandidateName] = useState<string>('Candidate');
  const [synthesisResult, setSynthesisResult] = useState<SynthesisResponse | null>(null);

  // Synchronize default tabs with authenticated role
  useEffect(() => {
    if (role === 'student') {
      setActiveTab('interview');
    } else if (role === 'staff') {
      setActiveTab('students');
    } else if (role === 'hod') {
      setActiveTab('students');
    }
  }, [role]);

  const handleInterviewStarted = (session: StartInterviewResponse, name: string) => {
    setActiveSession(session);
    setCandidateName(name);
    setInterviewPhase('interviewing');
  };

  const handleInterviewConcluded = (synthesis: SynthesisResponse) => {
    setSynthesisResult(synthesis);
    setInterviewPhase('concluded');
  };

  const handleRestart = () => {
    setActiveSession(null);
    setSynthesisResult(null);
    setInterviewPhase('setup');
    setTargetedSkill(undefined);
  };

  const handleStartTargetedInterview = (skill: string) => {
    setTargetedSkill(skill);
    setActiveTab('interview');
    setInterviewPhase('setup');
  };

  // 1. Loading State during session hydration
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-[#030712]">
        <div className="text-center">
          <Loader2 className="w-10 h-10 animate-spin text-blue-600 dark:text-cyan-400 mx-auto mb-3" />
          <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Initializing Axon Security Context...
          </p>
        </div>
      </div>
    );
  }

  // 2. Unauthenticated State -> Three-Surface Institutional Login Portal
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-[#030712] text-slate-900 dark:text-slate-100 transition-colors duration-200">
        <header className="py-4 px-6 border-b border-slate-200 dark:border-blue-950/60 bg-white/90 dark:bg-[#030712]/90 backdrop-blur-md flex items-center justify-between">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 via-blue-500 to-cyan-400 flex items-center justify-center text-white shadow-md shadow-blue-500/20 font-bold">
              Ax
            </div>
            <span className="font-extrabold text-lg text-slate-900 dark:text-white">
              Axon<span className="text-blue-600 dark:text-cyan-400">.ai</span>
            </span>
          </div>

          <div className="flex items-center space-x-3">
            <span className="hidden sm:inline-block text-xs font-semibold px-3 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-cyan-300 border border-blue-200 dark:border-blue-900">
              Department of Information Technology
            </span>

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
        </header>

        <main className="flex-1">
          <LoginPortal />
        </main>

        <footer className="border-t border-slate-200 dark:border-blue-950/60 py-4 text-center text-xs text-slate-500">
          Axon Institutional Assessment Portal • Department of Information Technology
        </footer>
      </div>
    );
  }

  // 3. Authenticated Role-Restricted Workspaces
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-[#030712] text-slate-900 dark:text-slate-100 transition-colors duration-200">
      <Navbar
        activeTab={activeTab}
        onSelectTab={(tab) => {
          // Prevent unauthorized tab navigation
          if (role === 'student' && tab !== 'interview' && tab !== 'my-tasks') return;
          if (role === 'staff' && tab !== 'students' && tab !== 'tasks') return;
          setActiveTab(tab);
        }}
      />

      <main className="flex-1 p-4 sm:p-6 lg:p-8">
        {/* STUDENT WORKSPACE */}
        {role === 'student' && (
          <>
            {activeTab === 'interview' && (
              <>
                {interviewPhase === 'setup' && (
                  <SetupScreen
                    onInterviewStarted={handleInterviewStarted}
                    initialTargetSkill={targetedSkill}
                  />
                )}

                {interviewPhase === 'interviewing' && activeSession && (
                  <InterviewRoom
                    session={activeSession}
                    candidateName={candidateName}
                    onConcluded={handleInterviewConcluded}
                    onAbort={handleRestart}
                  />
                )}

                {interviewPhase === 'concluded' && synthesisResult && (
                  <ScorecardView
                    synthesis={synthesisResult}
                    candidateName={candidateName}
                    onRestart={handleRestart}
                  />
                )}
              </>
            )}

            {activeTab === 'my-tasks' && (
              <StudentTasks onStartTargetedInterview={handleStartTargetedInterview} />
            )}
          </>
        )}

        {/* STAFF WORKSPACE */}
        {role === 'staff' && (
          <>
            {activeTab === 'students' && <StudentProfilesView userRole="staff" />}
            {activeTab === 'tasks' && <DepartmentTasksView />}
          </>
        )}

        {/* HOD WORKSPACE */}
        {role === 'hod' && (
          <>
            {activeTab === 'students' && <StudentProfilesView userRole="hod" />}
            {activeTab === 'hod' && <HODHeatmap />}
            {activeTab === 'pool' && <KeyPoolMonitor />}
            {activeTab === 'tasks' && <DepartmentTasksView />}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-blue-950/60 py-6 text-center text-xs text-slate-500 dark:text-slate-500">
        <p>Axon Assessment Platform • Institutional Node Verified • {user.department}</p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </ThemeProvider>
  );
}
