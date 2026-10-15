
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { insightsService } from '../services/insightsService';
import { executiveSummaryService } from '../services/executiveSummaryService';
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
  FileText,
} from 'lucide-react';

function displayValue(value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  if (typeof value === 'string' || typeof value === 'number') {
    return String(value);
  }

  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === 'string' || typeof item === 'number') {
          return String(item);
        }

        if (item && typeof item === 'object') {
          return (
            item.title ||
            item.name ||
            item.description ||
            JSON.stringify(item)
          );
        }

        return '';
      })
      .filter(Boolean)
      .join('\n');
  }

  if (typeof value === 'object') {
    return Object.entries(value)
      .map(([key, item]) => {
        const formatted = displayValue(item);
        return formatted ? `${key.replaceAll('_', ' ')}: ${formatted}` : null;
      })
      .filter(Boolean)
      .join('\n');
  }

  return String(value);
}

function SummaryContent({ summary }) {
  const content = summary?.content || {};

  const sections = [
    ['overview', 'Overview'],
    ['customer_pain_points', 'Customer Pain Points'],
    ['priority_features', 'Priority Features'],
    ['product_opportunities', 'Product Opportunities'],
    ['roadmap_highlights', 'Roadmap Highlights'],
    ['risks', 'Risks'],
    ['dependencies', 'Dependencies'],
    ['recommendations', 'Recommendations'],
    ['expected_outcomes', 'Expected Outcomes'],
  ];

  const visibleSections = sections
    .map(([key, label]) => ({
      key,
      label,
      value: displayValue(content[key]),
    }))
    .filter((section) => section.value);

  if (visibleSections.length === 0) {
    return (
      <p className="text-sm text-slate-600">
        A summary record was returned, but it contains no displayable content.
        Try generating the summary again.
      </p>
    );
  }

  return (
    <div className="space-y-5">
      {visibleSections.map((section) => (
        <section key={section.key}>
          <h3 className="text-sm font-semibold text-slate-800 mb-1.5">
            {section.label}
          </h3>
          <p className="text-sm text-slate-600 leading-relaxed whitespace-pre-line">
            {section.value}
          </p>
        </section>
      ))}
    </div>
  );
}

export default function Insights() {
  const navigate = useNavigate();

  const [insights, setInsights] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState(null);

  const [roadmap, setRoadmap] = useState(null);
  const [executiveSummary, setExecutiveSummary] = useState(null);
  const [isSummaryLoading, setIsSummaryLoading] = useState(true);
  const [summaryError, setSummaryError] = useState(null);
  const [summarySuccess, setSummarySuccess] = useState(null);

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

  const fetchExecutiveSummary = async () => {
    setIsSummaryLoading(true);
    setSummaryError(null);

    try {
      const result = await executiveSummaryService.getCurrentSummary();
      setRoadmap(result.roadmap);
      setExecutiveSummary(result.summary);
    } catch (err) {
      setSummaryError(
        err.message || 'Unable to retrieve the executive summary.'
      );
    } finally {
      setIsSummaryLoading(false);
    }
  };

  const handleRefresh = async () => {
    await Promise.all([
      fetchInsights(),
      fetchExecutiveSummary(),
    ]);
  };

  useEffect(() => {
    fetchInsights();
    fetchExecutiveSummary();
  }, []);

  const handleGenerateInsights = async () => {
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

  const handleGenerateSummary = async () => {
    setIsGenerating(true);
    setSummaryError(null);
    setSummarySuccess(null);

    try {
      let currentRoadmap = roadmap;

      if (!currentRoadmap) {
        const result = await executiveSummaryService.getCurrentSummary();
        currentRoadmap = result.roadmap;
        setRoadmap(currentRoadmap);
      }

      const roadmapId =
        currentRoadmap?.roadmap_id ||
        currentRoadmap?.id ||
        currentRoadmap?._id;

      const generated =
        await executiveSummaryService.generateSummary(roadmapId);

      const returnedSummary = generated?.summary || generated;

      if (
        returnedSummary &&
        typeof returnedSummary === 'object' &&
        returnedSummary.content
      ) {
        setExecutiveSummary(returnedSummary);
        setSummarySuccess('Executive summary generated and saved successfully.');
      } else {
        // Reload the saved record if the endpoint response uses another shape.
        await fetchExecutiveSummary();
        setSummarySuccess('Executive summary generation request completed.');
      }
    } catch (err) {
      setSummaryError(
        err.message || 'Failed to generate the executive summary.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const hasInsightsData =
    Boolean(insights?.metrics?.feedbackAnalyzed) ||
    Boolean(insights?.summary) ||
    Boolean(insights?.issues && insights.issues.length > 0) ||
    Boolean(insights?.featureRequests && insights.featureRequests.length > 0) ||
    Boolean(
      insights?.priorityOpportunities &&
      insights.priorityOpportunities.length > 0
    );

  const hasSummaryContent = Boolean(
    executiveSummary?.content &&
    Object.values(executiveSummary.content).some((value) => {
      if (Array.isArray(value)) return value.length > 0;
      if (value && typeof value === 'object') {
        return Object.keys(value).length > 0;
      }
      return value !== null && value !== undefined && value !== '';
    })
  );

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/60 gap-4">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
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

        <div className="flex items-center gap-2.5 flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            icon={RefreshCw}
            disabled={isLoading || isSummaryLoading || isGenerating}
          >
            Refresh
          </Button>

          <Button
            variant="ai"
            size="sm"
            onClick={handleGenerateInsights}
            isLoading={isGenerating}
            loadingText="Analyzing Feedback..."
            icon={Sparkles}
            disabled={isGenerating}
          >
            Analyze Feedback
          </Button>
        </div>
      </div>

      {error && (
        <ErrorState
          title="Insights Service Alert"
          message={error}
          onRetry={fetchInsights}
        />
      )}

      {isLoading ? (
        <div className="space-y-6">
          <MetricSkeleton count={4} />
          <ContentSkeleton lines={5} />
          <ContentSkeleton lines={4} />
        </div>
      ) : !hasInsightsData ? (
        <EmptyState
          icon={Sparkles}
          title="No insights available yet"
          description="Submit customer feedback to generate insights and discover high-priority opportunities."
          actionLabel="Analyze Feedback"
          actionIcon={Sparkles}
          actionVariant="ai"
          onAction={handleGenerateInsights}
          secondaryActionLabel="Submit Customer Feedback"
          onSecondaryAction={() => navigate('/feedback')}
        />
      ) : (
        <div className="space-y-8">
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

          {insights?.summary && (
            <div className="p-5 sm:p-6 rounded-lg border border-slate-200 bg-white shadow-subtle">
              <div className="flex items-center gap-2 mb-2.5">
                <Sparkles className="w-4 h-4 text-violet-600" />
                <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                  AI Synthesis
                </h2>
              </div>
              <p className="text-sm text-slate-800 leading-relaxed">
                {insights.summary}
              </p>
            </div>
          )}

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

      <section className="rounded-xl border border-slate-200 bg-white shadow-subtle overflow-hidden">
        <div className="p-5 sm:p-6 border-b border-slate-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-violet-600" />
              <h2 className="text-base font-semibold text-slate-900">
                Executive Summary
              </h2>
            </div>
            <p className="text-sm text-slate-500 mt-1">
              AI-generated leadership summary grounded in the current product roadmap.
            </p>
            {roadmap && (
              <p className="text-xs text-slate-400 mt-1">
                Roadmap: {roadmap.title || 'Current roadmap'}
                {roadmap.version ? ` · Version ${roadmap.version}` : ''}
              </p>
            )}
          </div>

          <Button
            variant="ai"
            size="sm"
            onClick={handleGenerateSummary}
            isLoading={isGenerating}
            loadingText="Generating Summary..."
            icon={Sparkles}
            disabled={isGenerating || isSummaryLoading}
          >
            {hasSummaryContent ? 'Regenerate Summary' : 'Generate Executive Summary'}
          </Button>
        </div>

        <div className="p-5 sm:p-6">
          {summaryError && (
            <div
              role="alert"
              className="mb-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700"
            >
              <p>{summaryError}</p>
              {!roadmap && (
                <p className="mt-1">
                  A saved current roadmap is required before generating a summary.
                </p>
              )}
            </div>
          )}

          {summarySuccess && (
            <p
              role="status"
              className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700"
            >
              {summarySuccess}
            </p>
          )}

          {isSummaryLoading ? (
            <div className="space-y-3">
              <ContentSkeleton lines={4} />
            </div>
          ) : hasSummaryContent ? (
            <div className="space-y-5">
              <div>
                <h3 className="text-base font-semibold text-slate-900">
                  {executiveSummary.title || 'Product Executive Summary'}
                </h3>
                <div className="flex flex-wrap gap-x-4 gap-y-1 mt-1 text-xs text-slate-500">
                  {executiveSummary.version && (
                    <span>Summary version {executiveSummary.version}</span>
                  )}
                  {executiveSummary.roadmap_version && (
                    <span>Roadmap version {executiveSummary.roadmap_version}</span>
                  )}
                  {executiveSummary.review_status && (
                    <span>
                      Status: {executiveSummary.review_status.replaceAll('_', ' ')}
                    </span>
                  )}
                </div>
              </div>

              <SummaryContent summary={executiveSummary} />
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-8 h-8 text-slate-300 mx-auto mb-3" />
              <p className="text-sm font-medium text-slate-700">
                No executive summary saved yet
              </p>
              <p className="text-sm text-slate-500 mt-1">
                Generate one to summarize roadmap highlights, customer needs, risks, and recommendations.
              </p>
              {!roadmap && !summaryError && (
                <p className="text-xs text-amber-600 mt-2">
                  No current roadmap was found in this workspace.
                </p>
              )}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
