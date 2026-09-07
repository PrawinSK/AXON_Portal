import React from 'react';
import {
  Award,
  CheckCircle2,
  AlertCircle,
  Calendar,
  RotateCcw,
  Printer,
  Sparkles,
  TrendingUp,
  BrainCircuit,
  MessageSquare,
  ShieldCheck
} from 'lucide-react';
import type { SynthesisResponse } from '../types';

interface ScorecardViewProps {
  synthesis: SynthesisResponse;
  candidateName: string;
  onRestart: () => void;
}

export const ScorecardView: React.FC<ScorecardViewProps> = ({
  synthesis,
  candidateName,
  onRestart,
}) => {
  // Compute SVG Radar Polygon Coordinates
  const metrics = [
    { label: 'Technical Depth', value: synthesis.technical_depth },
    { label: 'Logical Reasoning', value: synthesis.logical_reasoning },
    { label: 'Communication', value: synthesis.communication_clarity },
    ...Object.entries(synthesis.domain_scores).slice(0, 3).map(([k, v]) => ({
      label: k.length > 14 ? `${k.slice(0, 12)}...` : k,
      value: v,
    })),
  ];

  const size = 260;
  const center = size / 2;
  const radius = center - 40;
  const angleStep = (Math.PI * 2) / metrics.length;

  // Compute polygon points for candidate scores (scaled 0..10)
  const polygonPoints = metrics
    .map((m, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const normalized = Math.max(0.5, Math.min(10, m.value)) / 10;
      const x = center + radius * normalized * Math.cos(angle);
      const y = center + radius * normalized * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(' ');

  // Outer ring polygon points
  const outerRingPoints = metrics
    .map((_, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * Math.cos(angle);
      const y = center + radius * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(' ');

  // Mid ring polygon points
  const midRingPoints = metrics
    .map((_, i) => {
      const angle = i * angleStep - Math.PI / 2;
      const x = center + radius * 0.5 * Math.cos(angle);
      const y = center + radius * 0.5 * Math.sin(angle);
      return `${x},${y}`;
    })
    .join(' ');

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 space-y-8 print:p-0">
      
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm print:border-none">
        <div>
          <div className="flex items-center space-x-2 text-xs font-bold text-blue-600 dark:text-cyan-400 uppercase tracking-wider mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Assessment Synthesis Completed</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black text-slate-900 dark:text-white tracking-tight">
            Performance Scorecard: {candidateName}
          </h1>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
            Mode: <span className="font-semibold uppercase text-slate-700 dark:text-slate-300">{synthesis.mode}</span> | Session ID: <code className="text-[10px]">{synthesis.session_id.slice(0, 8)}</code>
          </p>
        </div>

        <div className="flex items-center space-x-3 print:hidden">
          <button
            onClick={handlePrint}
            className="p-2.5 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-900 transition-all text-xs font-semibold flex items-center space-x-1.5"
          >
            <Printer className="w-4 h-4" />
            <span>Print Report</span>
          </button>

          <button
            onClick={onRestart}
            className="py-2.5 px-4 rounded-xl bg-blue-600 hover:bg-blue-700 text-white transition-all text-xs font-bold flex items-center space-x-1.5 shadow-md shadow-blue-500/20"
          >
            <RotateCcw className="w-4 h-4" />
            <span>New Interview</span>
          </button>
        </div>
      </div>

      {/* Task Auto-Close Notice (if applicable) */}
      {synthesis.tasks_auto_closed && synthesis.tasks_auto_closed.length > 0 && (
        <div className="p-4 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-emerald-900 dark:text-emerald-200 flex items-center space-x-3">
          <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400 shrink-0" />
          <div className="text-xs">
            <span className="font-bold">Remediation Task Auto-Closed: </span>
            {synthesis.tasks_auto_closed.join(', ')}
          </div>
        </div>
      )}

      {/* Score Overview & Radar Visualization */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
        
        {/* Overall Score Badge + Dimension Bars */}
        <div className="md:col-span-6 space-y-6">
          <div className="p-6 rounded-3xl bg-gradient-to-tr from-blue-600 via-blue-700 to-indigo-800 text-white shadow-lg shadow-blue-500/20">
            <div className="flex items-center justify-between">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-cyan-200 block mb-1">
                  Overall Competency
                </span>
                <div className="flex items-baseline space-x-1">
                  <span className="text-5xl font-black">{synthesis.overall_score.toFixed(1)}</span>
                  <span className="text-lg text-blue-200 font-semibold">/ 10</span>
                </div>
              </div>
              <div className="w-14 h-14 rounded-2xl bg-white/10 backdrop-blur-md flex items-center justify-center">
                <Award className="w-8 h-8 text-amber-300" />
              </div>
            </div>
            <p className="text-xs text-blue-100 mt-4 leading-relaxed">
              Synthesized by Axon AI across all turn evaluations, technical grounding, and problem-solving mechanics.
            </p>
          </div>

          {/* Sub-Metric Bars */}
          <div className="p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
              Core Technical Dimensions
            </h3>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="flex items-center space-x-1 text-slate-800 dark:text-slate-200">
                  <TrendingUp className="w-3.5 h-3.5 text-blue-500" />
                  <span>Technical Depth</span>
                </span>
                <span className="font-mono text-blue-600 dark:text-cyan-400">{synthesis.technical_depth.toFixed(1)}/10</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div className="h-full bg-blue-600 rounded-full" style={{ width: `${synthesis.technical_depth * 10}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="flex items-center space-x-1 text-slate-800 dark:text-slate-200">
                  <BrainCircuit className="w-3.5 h-3.5 text-indigo-500" />
                  <span>Logical Reasoning</span>
                </span>
                <span className="font-mono text-indigo-600 dark:text-indigo-400">{synthesis.logical_reasoning.toFixed(1)}/10</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${synthesis.logical_reasoning * 10}%` }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold mb-1">
                <span className="flex items-center space-x-1 text-slate-800 dark:text-slate-200">
                  <MessageSquare className="w-3.5 h-3.5 text-emerald-500" />
                  <span>Communication Clarity</span>
                </span>
                <span className="font-mono text-emerald-600 dark:text-emerald-400">{synthesis.communication_clarity.toFixed(1)}/10</span>
              </div>
              <div className="w-full h-2 rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${synthesis.communication_clarity * 10}%` }} />
              </div>
            </div>
          </div>

        </div>

        {/* Skill Radar Chart (SVG Visualization) */}
        <div className="md:col-span-6 p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm flex flex-col items-center justify-center">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 mb-2 self-start">
            Skill Competency Radar
          </h3>

          <div className="relative">
            <svg width={size} height={size} className="overflow-visible">
              {/* Outer boundary ring */}
              <polygon
                points={outerRingPoints}
                className="fill-none stroke-slate-200 dark:stroke-slate-800"
                strokeWidth="1.5"
              />
              {/* Mid ring */}
              <polygon
                points={midRingPoints}
                className="fill-none stroke-slate-200/60 dark:stroke-slate-800/60"
                strokeWidth="1"
                strokeDasharray="3 3"
              />

              {/* Axis rays */}
              {metrics.map((_, i) => {
                const angle = i * angleStep - Math.PI / 2;
                const x = center + radius * Math.cos(angle);
                const y = center + radius * Math.sin(angle);
                return (
                  <line
                    key={i}
                    x1={center}
                    y1={center}
                    x2={x}
                    y2={y}
                    className="stroke-slate-200 dark:stroke-slate-800"
                    strokeWidth="1"
                  />
                );
              })}

              {/* Candidate filled polygon */}
              <polygon
                points={polygonPoints}
                className="fill-blue-500/25 stroke-blue-600 dark:stroke-cyan-400"
                strokeWidth="2.5"
              />

              {/* Data points */}
              {metrics.map((m, i) => {
                const angle = i * angleStep - Math.PI / 2;
                const normalized = Math.max(0.5, Math.min(10, m.value)) / 10;
                const x = center + radius * normalized * Math.cos(angle);
                const y = center + radius * normalized * Math.sin(angle);

                // Label position slightly outward
                const lx = center + (radius + 18) * Math.cos(angle);
                const ly = center + (radius + 18) * Math.sin(angle);

                return (
                  <g key={i}>
                    <circle cx={x} cy={y} r="3.5" className="fill-blue-600 dark:fill-cyan-400 stroke-white dark:stroke-[#0B0F19]" strokeWidth="1.5" />
                    <text
                      x={lx}
                      y={ly}
                      textAnchor="middle"
                      dominantBaseline="middle"
                      className="text-[10px] font-semibold fill-slate-700 dark:fill-slate-300"
                    >
                      {m.label}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          {/* Domain Badges */}
          <div className="mt-4 flex flex-wrap gap-2 justify-center">
            {Object.entries(synthesis.domain_scores).map(([k, v]) => (
              <span
                key={k}
                className="px-2.5 py-1 rounded-full text-[11px] font-semibold bg-slate-100 text-slate-800 dark:bg-slate-900 dark:text-cyan-300 border border-slate-200 dark:border-slate-800"
              >
                {k}: <span className="font-mono">{Number(v).toFixed(1)}</span>
              </span>
            ))}
          </div>
        </div>

      </div>

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        
        {/* Strengths */}
        <div className="p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 text-xs font-bold uppercase tracking-wider">
            <CheckCircle2 className="w-4 h-4" />
            <span>Demonstrated Strengths</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {synthesis.strengths.map((s, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                <span>{s}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Areas for Improvement */}
        <div className="p-6 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-3">
          <div className="flex items-center space-x-2 text-amber-600 dark:text-amber-400 text-xs font-bold uppercase tracking-wider">
            <AlertCircle className="w-4 h-4" />
            <span>Critical Knowledge Gaps</span>
          </div>
          <ul className="space-y-2 text-xs text-slate-700 dark:text-slate-300">
            {synthesis.weaknesses.map((w, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                <span>{w}</span>
              </li>
            ))}
          </ul>
        </div>

      </div>

      {/* Week-by-Week Actionable Remediation Roadmap */}
      <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#0B0F19] border border-slate-200 dark:border-blue-950/80 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 text-blue-600 dark:text-cyan-400 text-xs font-bold uppercase tracking-wider">
          <Calendar className="w-4 h-4" />
          <span>Curated Learning & Remediation Roadmap</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          {synthesis.roadmap.map((step) => (
            <div
              key={step.week}
              className="p-5 rounded-2xl bg-slate-50 dark:bg-slate-900/40 border border-slate-200/80 dark:border-slate-800 space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-cyan-300">
                  Week {step.week}
                </span>
                <span className="text-xs font-bold text-slate-900 dark:text-white">
                  {step.focus}
                </span>
              </div>

              <ul className="space-y-1.5 text-xs text-slate-600 dark:text-slate-400">
                {step.action_items.map((item, i) => (
                  <li key={i} className="flex items-start space-x-2">
                    <span className="text-blue-500 dark:text-cyan-400 font-bold">›</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
