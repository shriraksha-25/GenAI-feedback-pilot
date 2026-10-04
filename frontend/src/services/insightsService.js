import api from './api';

/**
 * Normalizes insights data structure from FastAPI backend
 * Handles field name variations safely without fabricating data
 */
export function normalizeInsightsResponse(data) {
  if (!data) return null;

  // Extract metrics safely
  const rawMetrics = data.metrics || data.overview || {};
  const metrics = {
    feedbackAnalyzed: rawMetrics.feedback_analyzed ?? rawMetrics.feedbackAnalyzed ?? data.total_feedback ?? null,
    issuesIdentified: rawMetrics.issues_identified ?? rawMetrics.issuesIdentified ?? (Array.isArray(data.issues) ? data.issues.length : null),
    featureRequests: rawMetrics.feature_requests ?? rawMetrics.featureRequests ?? (Array.isArray(data.feature_requests) ? data.feature_requests.length : null),
    themesDetected: rawMetrics.themes_detected ?? rawMetrics.themesDetected ?? (Array.isArray(data.themes) ? data.themes.length : null),
  };

  // AI Summary
  const summary = data.summary || data.ai_summary || data.executive_summary || null;

  // Issues & Pain points
  const rawIssues = data.issues || data.pain_points || [];
  const issues = Array.isArray(rawIssues)
    ? rawIssues.map((item, idx) => ({
        id: item.id || `issue-${idx}`,
        title: item.issue || item.title || item.name || '—',
        frequency: item.frequency ?? item.count ?? item.occurrences ?? null,
        priority: item.priority || 'Medium',
        description: item.description || item.details || null,
        impact: item.impact || null,
      }))
    : [];

  // Feature requests
  const rawFeatures = data.feature_requests || data.features || [];
  const featureRequests = Array.isArray(rawFeatures)
    ? rawFeatures.map((item, idx) => ({
        id: item.id || `feature-${idx}`,
        title: item.feature || item.title || item.name || '—',
        frequency: item.frequency ?? item.count ?? item.requests ?? null,
        priority: item.priority || 'Medium',
        description: item.description || item.details || null,
      }))
    : [];

  // Common Themes
  const rawThemes = data.themes || data.common_themes || [];
  const themes = Array.isArray(rawThemes)
    ? rawThemes.map((item, idx) => {
        if (typeof item === 'string') return { id: `theme-${idx}`, name: item, count: null };
        return {
          id: item.id || `theme-${idx}`,
          name: item.name || item.theme || item.title || '—',
          count: item.count ?? item.frequency ?? null,
          description: item.description || null,
        };
      })
    : [];

  // Priority opportunities
  const rawOpportunities = data.priority_opportunities || data.opportunities || [];
  const priorityOpportunities = Array.isArray(rawOpportunities)
    ? rawOpportunities.map((item, idx) => ({
        id: item.id || `opp-${idx}`,
        title: item.title || item.opportunity || '—',
        description: item.description || null,
        priority: item.priority || 'High',
        recommendedAction: item.recommended_action || item.action || null,
        impact: item.impact || null,
      }))
    : [];

  return {
    metrics,
    summary,
    issues,
    featureRequests,
    themes,
    priorityOpportunities,
    lastAnalyzed: data.analyzed_at || data.timestamp || data.updated_at || null,
  };
}

export const insightsService = {
  /**
   * Fetch current AI insights from FastAPI backend
   * @returns {Promise<Object|null>}
   */
  async getInsights() {
    const response = await api.get('/insights');
    return normalizeInsightsResponse(response.data);
  },

  /**
   * Request backend to generate/recompute insights from customer feedback
   * @returns {Promise<Object>}
   */
  async generateInsights() {
    const response = await api.post('/insights/generate');
    return normalizeInsightsResponse(response.data);
  },
};
