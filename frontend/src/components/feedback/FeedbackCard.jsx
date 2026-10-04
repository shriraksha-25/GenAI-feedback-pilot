import React from 'react';
import StatusBadge from '../common/StatusBadge';
import { formatDate, truncateText, safeVal } from '../../utils/formatters';
import { MessageSquareQuote } from 'lucide-react';

export default function FeedbackCard({ item, onClick }) {
  if (!item) return null;

  return (
    <div
      onClick={onClick}
      className={`p-4 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors shadow-subtle ${
        onClick ? 'cursor-pointer hover:bg-slate-50/50' : ''
      }`}
    >
      <div className="flex items-start justify-between gap-2 mb-2">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <MessageSquareQuote className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
          <span className="font-medium text-slate-700">{safeVal(item.source, 'Feedback')}</span>
          <span>•</span>
          <span>{formatDate(item.date)}</span>
        </div>
        <StatusBadge status={item.analysisStatus || item.status} />
      </div>

      <p className="text-xs text-slate-800 line-clamp-3 leading-relaxed mb-3">
        {truncateText(item.text, 180)}
      </p>

      {item.customer && (
        <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
          <span>{item.customer}</span>
        </div>
      )}
    </div>
  );
}
