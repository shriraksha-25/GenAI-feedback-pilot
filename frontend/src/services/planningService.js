import api from './api';

export const planningService = {
  async getPlanningItems() {
    const response = await api.get('/planning');
    const data = response.data;

    const items = Array.isArray(data)
      ? data
      : data.items || data.plans || [];

    return items.map((item) => ({
      id: item.id || item._id,
      title: item.title || '—',
      description: item.description || '',
      priority: item.priority || 'Medium',
      targetArea:
        item.target_area || item.targetArea || 'Core Product',
      notes: item.notes || '',
      status: item.status || 'Planned',
      createdAt:
        item.created_at || item.createdAt || null,
      relatedOpportunity:
        item.related_opportunity ||
        item.opportunity ||
        null,
    }));
  },

  async createPlanItem(planData) {
    const payload = {
      title: planData.title.trim(),
      description:
        planData.description?.trim() || '',
      priority: planData.priority || 'Medium',
      target_area:
        planData.targetArea || 'Core Product',
      notes: planData.notes?.trim() || '',
      status: planData.status || 'Planned',
      related_opportunity:
        planData.relatedOpportunity || null,
    };

    const response = await api.post(
      '/planning',
      payload
    );

    return response.data;
  },

  async updatePlanItem(id, updates) {
    const response = await api.put(
      `/planning/${id}`,
      updates
    );

    return response.data;
  },

  // -----------------------------
  // M3 Feature APIs
  // -----------------------------

  async getFeatures() {
    const response = await api.get('/features');

    return Array.isArray(response.data)
      ? response.data
      : [];
  },

  async createFeature(featureData) {
    const response = await api.post('/features', {
      title: featureData.title,
      description:
        featureData.description || '',
      theme: featureData.theme || null,
      pain_point:
        featureData.pain_point || null,
      feature_category:
        featureData.feature_category || null,
      source_feedback_ids:
        featureData.source_feedback_ids || [],
      created_by:
        featureData.created_by || null,
    });

    return response.data;
  },

  async getFeature(featureId) {
    const response = await api.get(
      `/features/${featureId}`
    );

    return response.data;
  },

  // -----------------------------
  // M3 PRD APIs
  // -----------------------------

  async generatePRD(featureId) {
    const response = await api.post(
      '/requirements/prd/generate',
      {
        feature_id: featureId,
        workspace_id: 'default-workspace',
        requested_by: 'frontend',
      }
    );

    return response.data;
  },

  async getPRDForFeature(featureId) {
    const response = await api.get(
      `/requirements/prd/feature/${featureId}`
    );

    return response.data;
  },

  // -----------------------------
  // M3 User Story APIs
  // -----------------------------

  async generateUserStories(featureId, prdId) {
    const response = await api.post(
      '/requirements/stories/generate',
      {
        feature_id: featureId,
        workspace_id: 'default-workspace',
        prd_id: prdId,
        requested_by: 'frontend',
      }
    );

    // IMPORTANT:
    // Return the generated stories response.
    return response.data;
  },

  async getUserStory(userStoryId) {
    const response = await api.get(
      `/requirements/stories/${userStoryId}`
    );

    return response.data;
  },
};