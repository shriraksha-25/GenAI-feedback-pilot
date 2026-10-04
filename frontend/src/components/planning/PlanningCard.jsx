import React from 'react';
import PriorityBadge from './PriorityBadge';
import StatusBadge from '../common/StatusBadge';
import { safeVal, formatDate } from '../../utils/formatters';
import { Target, FileText, CheckCircle2 } from 'lucide-react';

export default function PlanningCard({ plan, onUpdateStatus }) {
  if (!plan) return null;

  const isCompleted = plan.status?.toLowerCase() === 'completed' || plan.status?.toLowerCase() === 'done';

  return (
    <div className="p-4 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors shadow-subtle flex flex-col justify-between">
      <div>
        <div className="flex items-start justify-between gap-2 mb-2">
          <div className="flex items-center gap-2 flex-wrap">
            <PriorityBadge priority={plan.priority} />
            <StatusBadge status={plan.status} />
          </div>
          {plan.targetArea && (
            <span className="inline-flex items-center gap-1 text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded">
              <Target className="w-3 h-3 text-slate-400" />
              <span>{plan.targetArea}</span>
            </span>
          )}
        </div>

        <h4 className="text-sm font-semibold text-slate-900 mb-1.5 leading-snug">
          {safeVal(plan.title)}
        </h4>

        {plan.description && (
          <p className="text-xs text-slate-600 leading-relaxed mb-3">
            {plan.description}
          </p>
        )}

        {plan.notes && (
          <div className="p-2.5 rounded bg-slate-50 border border-slate-100 mb-3 text-xs text-slate-600 flex items-start gap-2">
            <FileText className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
            <div className="leading-relaxed">
              <span className="font-semibold text-slate-700">Notes: </span>
              {plan.notes}
            </div>
          </div>
        )}
      </div>

      <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
        <span>{plan.createdAt ? formatDate(plan.createdAt) : 'Initiative Item'}</span>
        
        {onUpdateStatus && (
          <button
            type="button"
            onClick={() => onUpdateStatus(plan.id, isCompleted ? 'Planned' : 'Completed')}
            className={`inline-flex items-center gap-1 font-medium transition-colors ${
              isCompleted
                ? 'text-slate-500 hover:text-slate-700'
                : 'text-emerald-700 hover:text-emerald-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>{isCompleted ? 'Mark Pending' : 'Mark Completed'}</span>
          </button>
        )}
      </div>
    </div>
  );
}
