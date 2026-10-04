import React from 'react';

export default function PriorityBadge({ priority, className = '' }) {
  const normalized = (priority || 'medium').toLowerCase();

  const styles = {
    high: 'bg-rose-50 text-rose-700 border-rose-200',
    critical: 'bg-rose-100 text-rose-800 border-rose-300',
    medium: 'bg-amber-50 text-amber-700 border-amber-200',
    low: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const dots = {
    high: 'bg-rose-500',
    critical: 'bg-rose-600',
    medium: 'bg-amber-500',
    low: 'bg-slate-400',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium border ${
        styles[normalized] || styles.medium
      } ${className}`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${dots[normalized] || dots.medium}`}
        aria-hidden="true"
      />
      <span className="capitalize">{priority || 'Medium'}</span>
    </span>
  );
}
