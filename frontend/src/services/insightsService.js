import api from './api';

/**
 * Convert backend dashboard response into the structure
 * expected by Dashboard.jsx
 */
export function normalizeInsightsResponse(data) {
  if (!data) return null;

  const dashboard = data.dashboard || data;

  const themes = Array.isArray(dashboard.themes)
    ? dashboard.themes.map((item, index) => ({
        id: `theme-${index}`,
        name: item._id || item.name || item.theme || '—',
        count: item.count ?? item.frequency ?? null,
        description: null,
      }))
    : [];

  const issues = Array.isArray(dashboard.pain_points)
    ? dashboard.pain_points.map((item, index) => ({
        id: `issue-${index}`,
        title: item._id || item.title || item.issue || '—',
        frequency: item.count ?? item.frequency ?? null,
        priority: 'Medium',
        description: item._id || item.description || null,
        impact: null,
      }))
    : [];

  const featureRequests = Array.isArray(dashboard.feature_requests)
    ? dashboard.feature_requests.map((item, index) => ({
        id: `feature-${index}`,
        title: item._id || item.title || item.feature || '—',
        frequency: item.count ?? item.frequency ?? null,
        priority: 'Medium',
        description: item._id || item.description || null,
      }))
    : [];

  const priorityOpportunities = featureRequests.map((item) => ({
    id: item.id,
    title: item.title,
    description: item.description,
    priority: item.priority,
    recommendedAction: item.title,
    impact: null,
  }));

  return {
    metrics: {
      feedbackAnalyzed: dashboard.total_analyzed ?? 0,
      issuesIdentified: issues.length,
      featureRequests: featureRequests.length,
      themesDetected: themes.length,
    },

    summary: null,

    issues,

    featureRequests,

    themes,

    priorityOpportunities,

    lastAnalyzed:
      data.analyzed_at ||
      data.timestamp ||
      data.updated_at ||
      null,
  };
}

export const insightsService = {
  async getInsights() {
    const response = await api.get('/insights/dashboard');
    return normalizeInsightsResponse(response.data);
  },

  async generateInsights() {
    const response = await api.post('/insights/generate');
    return normalizeInsightsResponse(response.data);
  },
};