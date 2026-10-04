import React from 'react';
import StatusBadge from '../common/StatusBadge';
import Button from '../common/Button';
import { safeVal } from '../../utils/formatters';
import { ArrowUpRight, Compass } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function PriorityList({ opportunities = [], onSelectOpportunity }) {
  const navigate = useNavigate();

  if (!opportunities || opportunities.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
        No high-priority opportunities identified yet.
      </div>
    );
  }

  const handleAction = (opp) => {
    if (onSelectOpportunity) {
      onSelectOpportunity(opp);
    } else {
      // Navigate to planning pre-filled
      navigate('/planning', { state: { selectedOpportunity: opp } });
    }
  };

  return (
    <div className="space-y-3">
      {opportunities.map((opp) => (
        <div
          key={opp.id}
          className="p-4 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors shadow-subtle flex flex-col sm:flex-row sm:items-center justify-between gap-4"
        >
          <div className="space-y-1.5 flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <StatusBadge status={opp.priority} />
              <h4 className="text-sm font-semibold text-slate-900 truncate">
                {safeVal(opp.title)}
              </h4>
            </div>

            {opp.description && (
              <p className="text-xs text-slate-600 leading-relaxed max-w-3xl">
                {opp.description}
              </p>
            )}

            {opp.recommendedAction && (
              <div className="flex items-center gap-1.5 text-xs text-emerald-800 font-medium pt-1">
                <Compass className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0" />
                <span>Recommended: {opp.recommendedAction}</span>
              </div>
            )}
          </div>

          <div className="flex items-center sm:flex-shrink-0 pt-2 sm:pt-0">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleAction(opp)}
              icon={ArrowUpRight}
              className="w-full sm:w-auto"
            >
              Add to Plan
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
