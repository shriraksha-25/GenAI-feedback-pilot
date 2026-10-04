import React from 'react';
import { Layers } from 'lucide-react';
import { safeVal } from '../../utils/formatters';

export default function ThemeList({ themes = [] }) {
  if (!themes || themes.length === 0) {
    return (
      <div className="p-5 text-center text-xs text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
        No recurring feedback themes detected yet.
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {themes.map((theme) => (
        <div
          key={theme.id}
          className="p-3.5 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors shadow-subtle flex flex-col justify-between"
        >
          <div>
            <div className="flex items-center justify-between gap-2 mb-1">
              <div className="flex items-center gap-1.5 min-w-0">
                <Layers className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                <span className="text-xs font-semibold text-slate-800 truncate">
                  {safeVal(theme.name)}
                </span>
              </div>
              {theme.count !== null && theme.count !== undefined && (
                <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
                  {theme.count} mentions
                </span>
              )}
            </div>
            {theme.description && (
              <p className="text-xs text-slate-500 leading-relaxed mt-1 line-clamp-2">
                {theme.description}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
