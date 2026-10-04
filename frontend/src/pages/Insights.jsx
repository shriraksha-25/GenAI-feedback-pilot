import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { insightsService } from '../services/insightsService';
import InsightMetric from '../components/insights/InsightMetric';
import IssueTable from '../components/insights/IssueTable';
import FeatureRequestTable from '../components/insights/FeatureRequestTable';
import ThemeList from '../components/insights/ThemeList';
import PriorityList from '../components/insights/PriorityList';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { MetricSkeleton, ContentSkeleton } from '../components/common/LoadingState';
import Button from '../components/common/Button';
import { formatDate } from '../utils/formatters';
import {
  MessageSquareQuote,
  AlertTriangle,
  Lightbulb,
  Layers,
  Sparkles,
  RefreshCw,
  Clock,
} from 'lucide-react';

export default function Insights() {
  const navigate = useNavigate();
  const [insights, setInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const fetchInsights = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await insightsService.getInsights();
      setInsights(data);
    } catch (err) {
      setError(err.message || 'Unable to retrieve product insights.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      const data = await insightsService.generateInsights();
      setInsights(data);
    } catch (err) {
      setError(err.message || 'Failed to recompute customer insights.');
    } finally {
      setIsGenerating(false);
    }
  };

  const hasInsightsData =
    Boolean(insights?.metrics?.feedbackAnalyzed) ||
    Boolean(insights?.summary) ||
    Boolean(insights?.issues && insights.issues.length > 0) ||
    Boolean(insights?.featureRequests && insights.featureRequests.length > 0) ||
    Boolean(insights?.priorityOpportunities && insights.priorityOpportunities.length > 0);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/60 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Customer Insights
            </h1>
            {insights?.lastAnalyzed && (
              <span className="inline-flex items-center gap-1 text-[11px] text-slate-500 bg-slate-100 px-2 py-0.5 rounded font-medium">
                <Clock className="w-3 h-3 text-slate-400" />
                Updated {formatDate(insights.lastAnalyzed, true)}
              </span>
            )}
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Understand what customers are saying and identify product opportunities.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchInsights}
            icon={RefreshCw}
            disabled={isLoading || isGenerating}
          >
            Refresh
          </Button>

          <Button
            variant="ai"
            size="sm"
            onClick={handleGenerate}
            isLoading={isGenerating}
            loadingText="Generating Insights..."
            icon={Sparkles}
          >
            Analyze Feedback
          </Button>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <ErrorState
          title="Insights Service Alert"
          message={error}
          onRetry={fetchInsights}
        />
      )}

      {/* Loading state */}
      {isLoading ? (
        <div className="space-y-6">
          <MetricSkeleton count={4} />
          <ContentSkeleton lines={5} />
          <ContentSkeleton lines={4} />
        </div>
      ) : !hasInsightsData ? (
        /* Empty State */
        <EmptyState
          icon={Sparkles}
          title="No insights available yet"
          description="Submit customer feedback to generate insights and discover high-priority opportunities."
          actionLabel="Analyze Feedback"
          actionIcon={Sparkles}
          actionVariant="ai"
          onAction={handleGenerate}
          secondaryActionLabel="Submit Customer Feedback"
          onSecondaryAction={() => navigate('/feedback')}
        />
      ) : (
        /* Detailed Insights Workspace */
        <div className="space-y-8">
          {/* Section A: Overview Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <InsightMetric
              title="Feedback Analyzed"
              value={insights?.metrics?.feedbackAnalyzed}
              description="Customer inputs examined"
              icon={MessageSquareQuote}
            />
            <InsightMetric
              title="Issues Identified"
              value={insights?.metrics?.issuesIdentified}
              description="Identified pain points & defects"
              icon={AlertTriangle}
            />
            <InsightMetric
              title="Feature Requests"
              value={insights?.metrics?.featureRequests}
              description="Customer requests and ideas"
              icon={Lightbulb}
            />
            <InsightMetric
              title="Themes Detected"
              value={insights?.metrics?.themesDetected}
              description="Recurring qualitative clusters"
              icon={Layers}
            />
          </div>

          {/* Section B: AI Summary */}
          {insights?.summary && (
            <div className="p-5 sm:p-6 rounded-lg border border-slate-200 bg-white shadow-subtle">
              <div className="flex items-center gap-2 mb-2.5">
                <Sparkles className="w-4 h-4 text-violet-600" />
                <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                  AI Synthesis & Executive Summary
                </h2>
              </div>
              <p className="text-sm text-slate-800 leading-relaxed">
                {insights.summary}
              </p>
            </div>
          )}

          {/* Section F: Priority Opportunities */}
          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Priority Opportunities
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Highest-leverage areas for immediate product enhancement
              </p>
            </div>
            <PriorityList opportunities={insights?.priorityOpportunities} />
          </div>

          {/* Section C: Issues & Pain Points */}
          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Customer Issues & Pain Points
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Reported user frictions and workflow obstacles
              </p>
            </div>
            <IssueTable issues={insights?.issues} />
          </div>

          {/* Section D: Feature Requests */}
          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Customer Feature Requests
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Enhancements demanded by active customers
              </p>
            </div>
            <FeatureRequestTable features={insights?.featureRequests} />
          </div>

          {/* Section E: Common Themes */}
          <div className="space-y-3">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Common Recurring Themes
              </h2>
              <p className="text-xs text-slate-500 mt-0.5">
                Categorical patterns detected across feedback submissions
              </p>
            </div>
            <ThemeList themes={insights?.themes} />
          </div>
        </div>
      )}
    </div>
  );
}
