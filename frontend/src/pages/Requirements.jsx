import React, { useState, useEffect } from 'react';
import { planningService } from '../services/planningService';
import StatusBadge from '../components/common/StatusBadge';
import PriorityBadge from '../components/planning/PriorityBadge';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { TableSkeleton } from '../components/common/LoadingState';
import { safeVal, formatDate } from '../utils/formatters';
import {
  FileText,
  Sparkles,
  Plus,
  RefreshCw,
  CheckSquare,
  AlertCircle,
} from 'lucide-react';

export default function Requirements() {
  const [requirements, setRequirements] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Detail Modal & Create Modal
  const [selectedReq, setSelectedReq] = useState(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'Medium',
    relatedCustomerIssue: '',
    acceptanceCriteria: '',
    status: 'Draft',
  });

  const loadRequirements = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await planningService.getRequirements();
      setRequirements(data);
    } catch (err) {
      setError(err.message || 'Unable to load requirements.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRequirements();
  }, []);

  const handleGenerateAI = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const generated = await planningService.generateRequirements();
      if (Array.isArray(generated) && generated.length > 0) {
        setRequirements((prev) => [...generated, ...prev]);
      } else {
        await loadRequirements();
      }
    } catch (err) {
      setError(err.message || 'Failed to generate requirements with backend AI.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCreateRequirement = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    setIsSubmitting(true);
    try {
      const criteriaList = formData.acceptanceCriteria
        .split('\n')
        .map((c) => c.trim())
        .filter(Boolean);

      await planningService.createRequirement({
        title: formData.title,
        description: formData.description,
        priority: formData.priority,
        relatedCustomerIssue: formData.relatedCustomerIssue,
        acceptanceCriteria: criteriaList,
        status: formData.status,
      });

      setIsCreateModalOpen(false);
      setFormData({
        title: '',
        description: '',
        priority: 'Medium',
        relatedCustomerIssue: '',
        acceptanceCriteria: '',
        status: 'Draft',
      });
      await loadRequirements();
    } catch (err) {
      alert(err.message || 'Failed to create requirement.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/60 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Requirements Management
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Generate and manage product requirements based on insights.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={loadRequirements}
            icon={RefreshCw}
            disabled={isLoading || isGenerating}
          >
            Refresh
          </Button>

          <Button
            variant="ai"
            size="sm"
            onClick={handleGenerateAI}
            isLoading={isGenerating}
            loadingText="Generating Requirements..."
            icon={Sparkles}
          >
            Generate Requirements
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsCreateModalOpen(true)}
            icon={Plus}
          >
            New Requirement
          </Button>
        </div>
      </div>

      {error && (
        <ErrorState
          title="Requirements Service Notice"
          message={error}
          onRetry={loadRequirements}
        />
      )}

      {/* Requirements Table */}
      <div className="space-y-4">
        {isLoading ? (
          <TableSkeleton rows={5} cols={5} />
        ) : requirements.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No requirements created yet"
            description="Use AI to generate structured product requirements from your feedback insights, or draft one manually."
            actionLabel="Generate Requirements"
            actionIcon={Sparkles}
            actionVariant="ai"
            onAction={handleGenerateAI}
            secondaryActionLabel="Create Manually"
            onSecondaryAction={() => setIsCreateModalOpen(true)}
          />
        ) : (
          <div className="bg-white rounded-lg border border-slate-200 shadow-subtle overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/70 border-b border-slate-200/80 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
                    <th scope="col" className="px-5 py-3">Requirement Title</th>
                    <th scope="col" className="px-4 py-3">Priority</th>
                    <th scope="col" className="px-4 py-3">Related Customer Issue</th>
                    <th scope="col" className="px-4 py-3">Criteria Count</th>
                    <th scope="col" className="px-4 py-3">Status</th>
                    <th scope="col" className="px-4 py-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                  {requirements.map((req) => (
                    <tr
                      key={req.id}
                      className="hover:bg-slate-50/60 transition-colors"
                    >
                      <td className="px-5 py-3.5 max-w-sm">
                        <span className="font-semibold text-slate-900 block truncate">
                          {safeVal(req.title)}
                        </span>
                        {req.description && (
                          <span className="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                            {req.description}
                          </span>
                        )}
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <PriorityBadge priority={req.priority} />
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap text-slate-600">
                        {req.relatedCustomerIssue ? (
                          <span className="inline-flex items-center gap-1.5 text-xs text-slate-700 font-medium bg-slate-50 px-2 py-0.5 rounded border border-slate-200/60">
                            <AlertCircle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0" />
                            <span className="truncate max-w-[180px]">{req.relatedCustomerIssue}</span>
                          </span>
                        ) : (
                          '—'
                        )}
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap text-slate-600 font-medium">
                        {req.acceptanceCriteria?.length || 0} items
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap">
                        <StatusBadge status={req.status} />
                      </td>

                      <td className="px-4 py-3.5 whitespace-nowrap text-right">
                        <button
                          type="button"
                          onClick={() => setSelectedReq(req)}
                          className="text-emerald-700 hover:text-emerald-800 font-medium hover:underline p-1"
                        >
                          View Specification
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Requirement Detail Modal */}
      {selectedReq && (
        <Modal
          isOpen={Boolean(selectedReq)}
          onClose={() => setSelectedReq(null)}
          title={selectedReq.title}
          subtitle={`Priority: ${selectedReq.priority} • Status: ${selectedReq.status}`}
          footer={
            <Button
              variant="outline"
              size="sm"
              onClick={() => setSelectedReq(null)}
            >
              Close
            </Button>
          }
        >
          <div className="space-y-4 text-xs">
            <div>
              <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-1">
                Description & Context
              </span>
              <p className="text-slate-800 leading-relaxed bg-slate-50 p-3 rounded border border-slate-100">
                {safeVal(selectedReq.description)}
              </p>
            </div>

            {selectedReq.relatedCustomerIssue && (
              <div>
                <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-1">
                  Originating Customer Issue
                </span>
                <div className="p-2.5 rounded bg-amber-50/60 border border-amber-200/60 text-amber-900 font-medium">
                  {selectedReq.relatedCustomerIssue}
                </div>
              </div>
            )}

            <div>
              <span className="font-semibold text-slate-500 uppercase tracking-wider text-[11px] block mb-1.5">
                Acceptance Criteria
              </span>
              {selectedReq.acceptanceCriteria && selectedReq.acceptanceCriteria.length > 0 ? (
                <ul className="space-y-2">
                  {selectedReq.acceptanceCriteria.map((criterion, idx) => (
                    <li
                      key={idx}
                      className="flex items-start gap-2 p-2 rounded bg-slate-50 border border-slate-100 text-slate-700"
                    >
                      <CheckSquare className="w-4 h-4 text-emerald-600 mt-0.5 flex-shrink-0" />
                      <span className="leading-relaxed">{criterion}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-400 italic">No acceptance criteria defined yet.</p>
              )}
            </div>
          </div>
        </Modal>
      )}

      {/* Create Requirement Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Draft Product Requirement"
        subtitle="Specify user story, context, and verifiable acceptance criteria"
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsCreateModalOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleCreateRequirement}
              isLoading={isSubmitting}
              loadingText="Saving..."
            >
              Save Requirement
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreateRequirement} className="space-y-4">
          <Input
            label="Requirement Title"
            name="title"
            placeholder="e.g. Export logs with CSV download support"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            disabled={isSubmitting}
          />

          <Input
            label="Description & User Story"
            name="description"
            as="textarea"
            rows={3}
            placeholder="As a user, I want to export filtered customer feedback as a CSV..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            disabled={isSubmitting}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Priority"
              name="priority"
              as="select"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              disabled={isSubmitting}
            >
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </Input>

            <Input
              label="Initial Status"
              name="status"
              as="select"
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value })}
              disabled={isSubmitting}
            >
              <option value="Draft">Draft</option>
              <option value="Planned">Planned</option>
              <option value="In Progress">In Progress</option>
              <option value="Done">Done</option>
            </Input>
          </div>

          <Input
            label="Related Customer Issue"
            name="relatedCustomerIssue"
            placeholder="e.g. Slow manual copy-paste of table data"
            value={formData.relatedCustomerIssue}
            onChange={(e) => setFormData({ ...formData, relatedCustomerIssue: e.target.value })}
            disabled={isSubmitting}
          />

          <Input
            label="Acceptance Criteria (One per line)"
            name="acceptanceCriteria"
            as="textarea"
            rows={3}
            placeholder="Given the user clicks export, CSV file downloads within 2 seconds.&#10;CSV includes all applied filter parameters."
            value={formData.acceptanceCriteria}
            onChange={(e) => setFormData({ ...formData, acceptanceCriteria: e.target.value })}
            disabled={isSubmitting}
          />
        </form>
      </Modal>
    </div>
  );
}
