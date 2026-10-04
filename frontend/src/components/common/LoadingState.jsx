import React from 'react';

export function MetricSkeleton({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {Array.from({ length: count }).map((_, idx) => (
        <div
          key={idx}
          className="bg-white p-5 rounded-lg border border-slate-200 shadow-subtle animate-pulse space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="h-3 w-24 bg-slate-200 rounded"></div>
            <div className="h-4 w-4 bg-slate-200 rounded-full"></div>
          </div>
          <div className="h-7 w-16 bg-slate-200 rounded"></div>
          <div className="h-3 w-36 bg-slate-100 rounded"></div>
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 5, cols = 4 }) {
  return (
    <div className="w-full bg-white rounded-lg border border-slate-200 shadow-subtle overflow-hidden animate-pulse">
      <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
        <div className="h-4 w-32 bg-slate-200 rounded"></div>
        <div className="h-7 w-20 bg-slate-200 rounded"></div>
      </div>
      <div className="divide-y divide-slate-100">
        {Array.from({ length: rows }).map((_, rIdx) => (
          <div key={rIdx} className="p-4 flex items-center justify-between gap-4">
            <div className="flex-1 space-y-2">
              <div className="h-4 w-3/4 bg-slate-200 rounded"></div>
              <div className="h-3 w-1/2 bg-slate-100 rounded"></div>
            </div>
            <div className="h-6 w-16 bg-slate-100 rounded"></div>
            <div className="h-4 w-20 bg-slate-200 rounded"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function ContentSkeleton({ lines = 4 }) {
  return (
    <div className="bg-white p-6 rounded-lg border border-slate-200 shadow-subtle animate-pulse space-y-4">
      <div className="h-5 w-48 bg-slate-200 rounded"></div>
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, idx) => (
          <div
            key={idx}
            className="h-3.5 bg-slate-100 rounded"
            style={{ width: `${95 - idx * 10}%` }}
          ></div>
        ))}
      </div>
    </div>
  );
}

export default function LoadingState({ type = 'content', rows, cols, count, message }) {
  if (type === 'metric') return <MetricSkeleton count={count} />;
  if (type === 'table') return <TableSkeleton rows={rows} cols={cols} />;
  return (
    <div className="space-y-4">
      {message && (
        <p className="text-xs text-slate-500 font-medium animate-pulse">{message}</p>
      )}
      <ContentSkeleton lines={rows || 4} />
    </div>
  );
}
