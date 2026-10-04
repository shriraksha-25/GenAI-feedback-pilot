import React from 'react';
import StatusBadge from '../common/StatusBadge';
import { safeVal } from '../../utils/formatters';

export default function FeatureRequestTable({ features = [] }) {
  if (!features || features.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-slate-500 bg-slate-50 rounded-lg border border-dashed border-slate-200">
        No feature requests identified from feedback yet.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-subtle overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/70 border-b border-slate-200/80 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              <th scope="col" className="px-5 py-3">Feature Request</th>
              <th scope="col" className="px-4 py-3">Frequency</th>
              <th scope="col" className="px-4 py-3">Priority</th>
              <th scope="col" className="px-5 py-3">Description</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
            {features.map((item) => (
              <tr key={item.id} className="hover:bg-slate-50/60 transition-colors">
                <td className="px-5 py-3.5 font-medium text-slate-900 whitespace-nowrap">
                  {safeVal(item.title)}
                </td>
                <td className="px-4 py-3.5 text-slate-600 whitespace-nowrap">
                  {item.frequency !== null ? `${item.frequency} requests` : '—'}
                </td>
                <td className="px-4 py-3.5 whitespace-nowrap">
                  <StatusBadge status={item.priority} />
                </td>
                <td className="px-5 py-3.5 text-slate-600 leading-relaxed max-w-md">
                  {safeVal(item.description)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
