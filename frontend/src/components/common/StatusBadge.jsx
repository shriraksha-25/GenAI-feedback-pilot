import React from 'react';

export default function StatusBadge({ status, type = 'status', className = '' }) {
  if (!status) return <span className="text-slate-400 text-xs">—</span>;

  const normalized = String(status).toLowerCase().trim();

  // Palette styles according to design guidelines
  const styles = {
    // Priorities
    high: 'bg-rose-50 text-rose-700 border-rose-200/80',
    critical: 'bg-rose-100 text-rose-800 border-rose-300',
    medium: 'bg-amber-50 text-amber-700 border-amber-200/80',
    low: 'bg-slate-100 text-slate-700 border-slate-200',

    // Statuses
    analyzed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    completed: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    done: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    planned: 'bg-emerald-50 text-emerald-800 border-emerald-200',
    pending: 'bg-amber-50 text-amber-700 border-amber-200',
    processing: 'bg-violet-50 text-violet-700 border-violet-200 animate-pulse',
    'in progress': 'bg-amber-50 text-amber-800 border-amber-200',
    'ai generated': 'bg-violet-50 text-violet-700 border-violet-200',
    draft: 'bg-slate-100 text-slate-600 border-slate-200',
  };

  const dotColors = {
    high: 'bg-rose-500',
    critical: 'bg-rose-600',
    medium: 'bg-amber-500',
    low: 'bg-slate-400',
    analyzed: 'bg-emerald-500',
    completed: 'bg-emerald-500',
    done: 'bg-emerald-500',
    planned: 'bg-emerald-600',
    pending: 'bg-amber-400',
    processing: 'bg-violet-500',
    'in progress': 'bg-amber-500',
    'ai generated': 'bg-violet-500',
    draft: 'bg-slate-400',
  };

  const badgeClass = styles[normalized] || 'bg-slate-100 text-slate-700 border-slate-200';
  const dotClass = dotColors[normalized] || 'bg-slate-400';

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-xs font-medium border ${badgeClass} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`} aria-hidden="true" />
      <span className="capitalize">{status}</span>
    </span>
  );
}
