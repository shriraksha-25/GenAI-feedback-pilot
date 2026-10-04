import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { planningService } from '../services/planningService';
import { insightsService } from '../services/insightsService';
import PlanningCard from '../components/planning/PlanningCard';
import PriorityBadge from '../components/planning/PriorityBadge';
import Modal from '../components/common/Modal';
import Input from '../components/common/Input';
import Button from '../components/common/Button';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { TableSkeleton } from '../components/common/LoadingState';
import { KanbanSquare, Plus, RefreshCw, Compass, ArrowRight } from 'lucide-react';

export default function Planning() {
  const location = useLocation();
  const [plans, setPlans] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  // Modal create plan state
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'High',
    targetArea: 'Core Experience',
    notes: '',
    relatedOpportunity: null,
  });

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [plansData, insightsData] = await Promise.allSettled([
        planningService.getPlanningItems(),
        insightsService.getInsights(),
      ]);

      if (plansData.status === 'fulfilled') {
        setPlans(plansData.value);
      }
      if (insightsData.status === 'fulfilled' && insightsData.value?.priorityOpportunities) {
        setOpportunities(insightsData.value.priorityOpportunities);
      }
    } catch (err) {
      setError(err.message || 'Unable to load planning data.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Check if routed with pre-selected opportunity from Insights/Dashboard
  useEffect(() => {
    if (location.state?.selectedOpportunity) {
      const opp = location.state.selectedOpportunity;
      setFormData({
        title: opp.title || '',
        description: opp.description || '',
        priority: opp.priority || 'High',
        targetArea: 'Customer Friction Point',
        notes: opp.recommendedAction ? `Recommended action: ${opp.recommendedAction}` : '',
        relatedOpportunity: opp.title,
      });
      setIsModalOpen(true);
    }
  }, [location.state]);

  const handleOpenCreateModal = (opp = null) => {
    if (opp) {
      setFormData({
        title: opp.title || '',
        description: opp.description || '',
        priority: opp.priority || 'High',
        targetArea: 'Product Intelligence',
        notes: opp.recommendedAction ? `Recommended action: ${opp.recommendedAction}` : '',
        relatedOpportunity: opp.title,
      });
    } else {
      setFormData({
        title: '',
        description: '',
        priority: 'Medium',
        targetArea: 'Core Product',
        notes: '',
        relatedOpportunity: null,
      });
    }
    setIsModalOpen(true);
  };

  const handleCreatePlan = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) return;

    setIsSubmitting(true);
    try {
      await planningService.createPlanItem(formData);
      setIsModalOpen(false);
      await loadData();
    } catch (err) {
      alert(err.message || 'Failed to save planning item.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdateStatus = async (planId, newStatus) => {
    try {
      await planningService.updatePlanItem(planId, { status: newStatus });
      setPlans((prev) =>
        prev.map((p) => (p.id === planId ? { ...p, status: newStatus } : p))
      );
    } catch (err) {
      alert(err.message || 'Failed to update plan status.');
    }
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/60 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Product Planning
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Convert customer feedback insights into concrete product initiatives.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={loadData}
            icon={RefreshCw}
            disabled={isLoading}
          >
            Refresh
          </Button>

          <Button
            variant="primary"
            size="sm"
            onClick={() => handleOpenCreateModal()}
            icon={Plus}
          >
            Create Plan
          </Button>
        </div>
      </div>

      {error && (
        <ErrorState
          title="Planning Service Notice"
          message={error}
          onRetry={loadData}
        />
      )}

      {/* Recommended Opportunities for Planning */}
      {opportunities.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                AI Recommended Priority Opportunities
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Select an opportunity to generate a linked execution plan
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {opportunities.map((opp) => (
              <div
                key={opp.id}
                className="p-4 rounded-lg border border-slate-200 bg-white hover:border-slate-300 transition-colors shadow-subtle flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <PriorityBadge priority={opp.priority} />
                    <span className="text-[11px] font-medium text-slate-400">Opportunity</span>
                  </div>
                  <h4 className="text-xs font-semibold text-slate-900 line-clamp-1 mb-1">
                    {opp.title}
                  </h4>
                  {opp.description && (
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-3">
                      {opp.description}
                    </p>
                  )}
                  {opp.recommendedAction && (
                    <div className="text-[11px] text-emerald-800 font-medium bg-emerald-50/70 p-2 rounded border border-emerald-100/80 mb-3 leading-snug">
                      <span className="font-semibold text-emerald-900">Action: </span>
                      {opp.recommendedAction}
                    </div>
                  )}
                </div>

                <div className="pt-2 border-t border-slate-100 flex justify-end">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleOpenCreateModal(opp)}
                    icon={ArrowRight}
                    className="w-full text-xs"
                  >
                    Turn into Plan
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Product Plans List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              Active Planning Initiatives
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Structured initiatives tracked for product delivery
            </p>
          </div>
          <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2.5 py-1 rounded">
            {plans.length} items
          </span>
        </div>

        {isLoading ? (
          <TableSkeleton rows={4} cols={3} />
        ) : plans.length === 0 ? (
          <EmptyState
            icon={KanbanSquare}
            title="No planning items created yet"
            description="Convert customer feedback insights into your first product roadmap initiative."
            actionLabel="Create First Plan"
            actionIcon={Plus}
            onAction={() => handleOpenCreateModal()}
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {plans.map((plan) => (
              <PlanningCard
                key={plan.id}
                plan={plan}
                onUpdateStatus={handleUpdateStatus}
              />
            ))}
          </div>
        )}
      </div>

      {/* Create Plan Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Create Product Plan Item"
        subtitle="Define an actionable initiative derived from user feedback"
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsModalOpen(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleCreatePlan}
              isLoading={isSubmitting}
              loadingText="Creating..."
            >
              Save Plan
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreatePlan} className="space-y-4">
          <Input
            label="Initiative Title"
            name="title"
            placeholder="e.g. Implement real-time export progress modal"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
            disabled={isSubmitting}
          />

          <Input
            label="Problem & Scope Description"
            name="description"
            as="textarea"
            rows={3}
            placeholder="Detail the user problem this plan addresses..."
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            disabled={isSubmitting}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Input
              label="Priority Level"
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
              label="Target Functional Area"
              name="targetArea"
              placeholder="e.g. Navigation, Billing, API"
              value={formData.targetArea}
              onChange={(e) => setFormData({ ...formData, targetArea: e.target.value })}
              disabled={isSubmitting}
            />
          </div>

          <Input
            label="Implementation Notes"
            name="notes"
            as="textarea"
            rows={2}
            placeholder="Any architecture requirements, backend notes, or context..."
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            disabled={isSubmitting}
          />
        </form>
      </Modal>
    </div>
  );
}
