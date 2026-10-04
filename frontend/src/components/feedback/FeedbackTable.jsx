import React, { useState } from 'react';
import StatusBadge from '../common/StatusBadge';
import Modal from '../common/Modal';
import Button from '../common/Button';
import { formatDate, truncateText, safeVal } from '../../utils/formatters';
import { Eye, MessageSquare } from 'lucide-react';

export default function FeedbackTable({ items = [], onTriggerAnalysis }) {
  const [selectedItem, setSelectedItem] = useState(null);

  if (!items || items.length === 0) {
    return null;
  }

  return (
    <>
      <div className="bg-white rounded-lg border border-slate-200 shadow-subtle overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Submitted Feedback Records</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              History of customer inputs ingested into FeedbackForge AI
            </p>
          </div>
          <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded">
            {items.length} {items.length === 1 ? 'record' : 'records'}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/70 border-b border-slate-200/80 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                <th scope="col" className="px-5 py-3">Feedback</th>
                <th scope="col" className="px-4 py-3">Source</th>
                <th scope="col" className="px-4 py-3">Date</th>
                <th scope="col" className="px-4 py-3">Status</th>
                <th scope="col" className="px-4 py-3">Analysis Status</th>
                <th scope="col" className="px-4 py-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
              {items.map((item) => (
                <tr
                  key={item.id}
                  className="hover:bg-slate-50/70 transition-colors"
                >
                  <td className="px-5 py-3.5 max-w-md">
                    <p className="text-slate-800 line-clamp-2 leading-relaxed">
                      {truncateText(item.text, 140)}
                    </p>
                    {item.customer && (
                      <span className="text-[11px] text-slate-400 mt-0.5 block">
                        Customer: {item.customer}
                      </span>
                    )}
                  </td>

                  <td className="px-4 py-3.5 whitespace-nowrap text-slate-600 font-medium">
                    {safeVal(item.source, 'Direct')}
                  </td>

                  <td className="px-4 py-3.5 whitespace-nowrap text-slate-500">
                    {formatDate(item.date)}
                  </td>

                  <td className="px-4 py-3.5 whitespace-nowrap">
                    <StatusBadge status={item.status} />
                  </td>

                  <td className="px-4 py-3.5 whitespace-nowrap">
                    <StatusBadge status={item.analysisStatus} />
                  </td>

                  <td className="px-4 py-3.5 whitespace-nowrap text-right">
                    <button
                      type="button"
                      onClick={() => setSelectedItem(item)}
                      className="inline-flex items-center gap-1 text-emerald-700 hover:text-emerald-800 font-medium hover:underline p-1"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      <span>Details</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedItem && (
        <Modal
          isOpen={Boolean(selectedItem)}
          onClose={() => setSelectedItem(null)}
          title="Feedback Record Details"
          subtitle={`Source: ${safeVal(selectedItem.source)} • Logged ${formatDate(selectedItem.date)}`}
          footer={
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedItem(null)}
            >
              Close
            </Button>
          }
        >
          <div className="space-y-4 text-xs">
            <div>
              <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-1">
                Raw Content
              </span>
              <div className="p-3.5 rounded bg-slate-50 border border-slate-200 text-slate-800 leading-relaxed whitespace-pre-wrap">
                {selectedItem.text}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-100">
              <div>
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-1">
                  Ingestion Status
                </span>
                <StatusBadge status={selectedItem.status} />
              </div>
              <div>
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-1">
                  AI Analysis Status
                </span>
                <StatusBadge status={selectedItem.analysisStatus} />
              </div>
            </div>

            {selectedItem.customer && (
              <div className="pt-2 border-t border-slate-100">
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-0.5">
                  Customer
                </span>
                <p className="text-slate-800">{selectedItem.customer}</p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </>
  );
}
