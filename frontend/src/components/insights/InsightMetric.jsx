import React from 'react';
import { formatNumber } from '../../utils/formatters';

export default function InsightMetric({
  title,
  value,
  description,
  icon: Icon,
  trend,
  className = '',
}) {
  const displayVal = value !== null && value !== undefined ? formatNumber(value) : '—';

  return (
    <div className={`bg-white p-5 rounded-lg border border-slate-200 shadow-subtle ${className}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          {title}
        </span>
        {Icon && (
          <div className="w-8 h-8 rounded-md bg-slate-50 border border-slate-100 flex items-center justify-center text-slate-500">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-2xl font-bold text-slate-900 tracking-tight">
          {displayVal}
        </span>
        {trend && (
          <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded">
            {trend}
          </span>
        )}
      </div>

      {description && (
        <p className="text-xs text-slate-500 leading-normal">
          {description}
        </p>
      )}
    </div>
  );
}
