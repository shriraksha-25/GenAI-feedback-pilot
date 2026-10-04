import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { insightsService } from '../services/insightsService';
import { feedbackService } from '../services/feedbackService';
import InsightMetric from '../components/insights/InsightMetric';
import IssueTable from '../components/insights/IssueTable';
import PriorityList from '../components/insights/PriorityList';
import FeedbackCard from '../components/feedback/FeedbackCard';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { MetricSkeleton, ContentSkeleton } from '../components/common/LoadingState';
import Button from '../components/common/Button';
import {
  MessageSquareQuote,
  AlertTriangle,
  Lightbulb,
  Layers,
  Sparkles,
  ArrowRight,
  PlusCircle,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from 'recharts';

export default function Dashboard() {
  const { user } = useAuth();
  const [insights, setInsights] = useState(null);
  const [recentFeedback, setRecentFeedback] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [insightsData, feedbackData] = await Promise.allSettled([
        insightsService.getInsights(),
        feedbackService.getFeedback({ limit: 4 }),
      ]);

      if (insightsData.status === 'fulfilled') {
        setInsights(insightsData.value);
      }
      if (feedbackData.status === 'fulfilled') {
        setRecentFeedback(feedbackData.value.slice(0, 4));
      }
      if (insightsData.status === 'rejected' && feedbackData.status === 'rejected') {
        setError(insightsData.reason?.message || 'Unable to load dashboard data.');
      }
    } catch (err) {
      setError(err.message || 'Error communicating with backend.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Time-appropriate greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const userName = user?.name ? user.name.split(' ')[0] : 'Product Lead';

  // Prepare chart data ONLY if actual issues with frequency are returned by backend
  const issueChartData =
    insights?.issues && insights.issues.some((i) => i.frequency !== null)
      ? insights.issues
          .filter((i) => i.frequency !== null)
          .slice(0, 5)
          .map((i) => ({
            name: i.title.length > 18 ? `${i.title.slice(0, 18)}...` : i.title,
            count: i.frequency,
          }))
      : [];

  const hasAnyData =
    Boolean(insights?.metrics?.feedbackAnalyzed) ||
    Boolean(recentFeedback && recentFeedback.length > 0) ||
    Boolean(insights?.issues && insights.issues.length > 0);

  return (
    <div className="space-y-8">
      {/* Dashboard Greeting Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-slate-200/60 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            {getGreeting()}, {userName}
          </h1>
          <p className="text-sm text-slate-500 mt-1">
            Here's what's happening with your customer feedback.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Link to="/feedback">
            <Button variant="primary" size="sm" icon={PlusCircle}>
              Submit Feedback
            </Button>
          </Link>
          <Link to="/insights">
            <Button variant="outline" size="sm" icon={Sparkles}>
              View Insights
            </Button>
          </Link>
        </div>
      </div>

      {/* Error Banner */}
      {error && (
        <ErrorState
          title="Unable to load dashboard data"
          message={error}
          onRetry={fetchDashboardData}
        />
      )}

      {/* Loading Skeleton */}
      {isLoading ? (
        <div className="space-y-6">
          <MetricSkeleton count={4} />
          <ContentSkeleton lines={6} />
        </div>
      ) : !hasAnyData && !error ? (
        /* Intentional Empty State */
        <EmptyState
          icon={MessageSquareQuote}
          title="No customer feedback yet"
          description="Submit your first piece of customer feedback or import raw feedback transcripts to start generating actionable product insights."
          actionLabel="Add Customer Feedback"
          actionIcon={PlusCircle}
          onAction={() => (window.location.href = '/feedback')}
        />
      ) : (
        /* Data-driven Dashboard Content */
        <div className="space-y-8">
          {/* Top 4 Metrics */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <InsightMetric
              title="Feedback Analyzed"
              value={insights?.metrics?.feedbackAnalyzed}
              description="Customer records processed through AI"
              icon={MessageSquareQuote}
            />
            <InsightMetric
              title="Issues Identified"
              value={insights?.metrics?.issuesIdentified}
              description="Friction points and software bugs"
              icon={AlertTriangle}
            />
            <InsightMetric
              title="Feature Requests"
              value={insights?.metrics?.featureRequests}
              description="User enhancements requested"
              icon={Lightbulb}
            />
            <InsightMetric
              title="Common Themes"
              value={insights?.metrics?.themesDetected}
              description="Recurring feedback patterns"
              icon={Layers}
            />
          </div>

          {/* AI Executive Summary if available */}
          {insights?.summary && (
            <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-subtle">
              <div className="flex items-center gap-2 mb-2">
                <Sparkles className="w-4 h-4 text-violet-600" />
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-700">
                  Recent AI Executive Summary
                </h3>
              </div>
              <p className="text-sm text-slate-700 leading-relaxed">
                {insights.summary}
              </p>
            </div>
          )}

          {/* Issue Frequency Chart - ONLY shown if real frequency data exists from backend */}
          {issueChartData.length > 0 && (
            <div className="p-5 rounded-lg border border-slate-200 bg-white shadow-subtle">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-semibold text-slate-900">
                    Top Issue Frequency
                  </h3>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Distribution of reported customer friction areas
                  </p>
                </div>
              </div>
              <div className="h-60 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={issueChartData} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                    <XAxis
                      dataKey="name"
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      angle={-15}
                      textAnchor="end"
                    />
                    <YAxis
                      stroke="#94A3B8"
                      fontSize={11}
                      tickLine={false}
                      allowDecimals={false}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#FFFFFF',
                        borderColor: '#E2E8F0',
                        borderRadius: '0.375rem',
                        fontSize: '12px',
                      }}
                    />
                    <Bar dataKey="count" fill="#059669" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Priority Opportunities & Top Customer Issues */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Customer Issues */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">
                  Top Customer Issues
                </h3>
                <Link
                  to="/insights"
                  className="text-xs text-emerald-700 hover:text-emerald-800 font-medium inline-flex items-center gap-1"
                >
                  View all <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
              <IssueTable issues={insights?.issues?.slice(0, 3)} />
            </div>

            {/* Priority Opportunities */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">
                  Priority Opportunities
                </h3>
                <Link
                  to="/planning"
                  className="text-xs text-emerald-700 hover:text-emerald-800 font-medium inline-flex items-center gap-1"
                >
                  Go to Planning <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
              <PriorityList opportunities={insights?.priorityOpportunities?.slice(0, 3)} />
            </div>
          </div>

          {/* Recent Feedback Feed */}
          {recentFeedback.length > 0 && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-slate-900">
                  Recent Ingested Feedback
                </h3>
                <Link
                  to="/feedback"
                  className="text-xs text-emerald-700 hover:text-emerald-800 font-medium inline-flex items-center gap-1"
                >
                  View feedback log <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {recentFeedback.map((item) => (
                  <FeedbackCard key={item.id} item={item} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
