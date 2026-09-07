import React, { useEffect, useState } from 'react';
import {
  Cpu,
  RefreshCw,
  Activity,
  CheckCircle2,
  AlertTriangle,
  Zap,
  Layers
} from 'lucide-react';
import { api } from '../services/api';
import type { PoolStatus } from '../types';

export const KeyPoolMonitor: React.FC = () => {
  const [status, setStatus] = useState<PoolStatus | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getPoolStatus();
      setStatus(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch pool status.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="max-w-6xl mx-auto py-8 px-4 sm:px-6 space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-blue-600 dark:text-cyan-400 uppercase tracking-wider mb-1">
            <Cpu className="w-3.5 h-3.5" />
            <span>Multi-Tenant Infrastructure</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            50-Key Gemini Pool Diagnostic Center
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Round-robin rotation, 429 quota isolation, and transient error failover for Google Gemini 3.6 Flash
          </p>
        </div>

        <button
          onClick={fetchStatus}
          disabled={isLoading}
          className="p-2.5 px-4 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-900 transition-all text-xs font-bold flex items-center space-x-2 shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-blue-500' : ''}`} />
          <span>Refresh Pool</span>
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-rose-700 dark:text-rose-300 text-xs flex items-center space-x-2 font-medium">
          <AlertTriangle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Cluster Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="p-5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Total Keys Loaded</span>
            <Layers className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-3xl font-black text-slate-900 dark:text-white">
            {status ? status.total_keys : '50'}
          </div>
          <div className="text-[11px] text-slate-400">Dedicated API secrets</div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Active & Healthy</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-3xl font-black text-emerald-600 dark:text-emerald-400">
            {status ? status.active_healthy_keys : '50'}
          </div>
          <div className="text-[11px] text-slate-400">Ready for instant routing</div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Peak Rate Limit (RPM)</span>
            <Zap className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-3xl font-black text-blue-600 dark:text-cyan-400">
            750 <span className="text-xs font-normal text-slate-400">req/min</span>
          </div>
          <div className="text-[11px] text-slate-400">50 keys × 15 RPM free quota</div>
        </div>

        <div className="p-5 rounded-2xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
            <span>Requests Served</span>
            <Activity className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="text-3xl font-black text-indigo-600 dark:text-indigo-400">
            {status ? status.total_requests_served : '0'}
          </div>
          <div className="text-[11px] text-slate-400">Across current session</div>
        </div>

      </div>

      {/* Visual 50-Key Grid */}
      <div className="p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center space-x-2">
            <span>Live Key Cluster Visualizer (50 Slots)</span>
          </h3>
          <span className="text-[11px] text-slate-400">
            Auto-refreshing every 5 seconds
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-5 md:grid-cols-10 gap-2">
          {Array.from({ length: 50 }).map((_, i) => {
            const isCooling = status && status.cooling_down_keys > 0 && i < status.cooling_down_keys;
            return (
              <div
                key={i}
                className={`p-2 rounded-xl border text-center transition-all ${
                  isCooling
                    ? 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-900 text-rose-800 dark:text-rose-300'
                    : 'bg-slate-50 dark:bg-slate-900/50 border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300'
                }`}
              >
                <div className="flex items-center justify-center space-x-1 mb-1">
                  <span
                    className={`w-2 h-2 rounded-full ${
                      isCooling ? 'bg-rose-500 animate-pulse' : 'bg-emerald-500'
                    }`}
                  />
                  <span className="text-[10px] font-mono font-bold">#{i + 1}</span>
                </div>
                <div className="text-[9px] font-mono text-slate-400 truncate">
                  {isCooling ? 'COOLDOWN' : 'ACTIVE'}
                </div>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
};
