import api from './api';

export const planningService = {
  /**
   * Fetch all planning items from FastAPI backend
   * @returns {Promise<Array>}
   */
  async getPlanningItems() {
    const response = await api.get('/planning');
    const data = response.data;
    const items = Array.isArray(data) ? data : data.items || data.plans || [];
    return items.map((item) => ({
      id: item.id || item._id,
      title: item.title || '—',
      description: item.description || '',
      priority: item.priority || 'Medium',
      targetArea: item.target_area || item.targetArea || 'Core Product',
      notes: item.notes || '',
      status: item.status || 'Planned',
      createdAt: item.created_at || item.createdAt || null,
      relatedOpportunity: item.related_opportunity || item.opportunity || null,
    }));
  },

  /**
   * Create a new planning item via FastAPI backend
   * @param {Object} planData 
   * @returns {Promise<Object>}
   */
  async createPlanItem(planData) {
    const payload = {
      title: planData.title.trim(),
      description: planData.description?.trim() || '',
      priority: planData.priority || 'Medium',
      target_area: planData.targetArea || 'Core Product',
      notes: planData.notes?.trim() || '',
      status: planData.status || 'Planned',
      related_opportunity: planData.relatedOpportunity || null,
    };
    const response = await api.post('/planning', payload);
    return response.data;
  },

  /**
   * Update planning item via FastAPI backend
   * @param {string} id 
   * @param {Object} updates 
   * @returns {Promise<Object>}
   */
  async updatePlanItem(id, updates) {
    const response = await api.put(`/planning/${id}`, updates);
    return response.data;
  },

  /**
   * Fetch generated or stored requirements from FastAPI backend
   * @returns {Promise<Array>}
   */
  async getRequirements() {
    const response = await api.get('/requirements');
    const data = response.data;
    const items = Array.isArray(data) ? data : data.items || data.requirements || [];
    return items.map((req) => ({
      id: req.id || req._id,
      title: req.title || '—',
      description: req.description || '',
      priority: req.priority || 'Medium',
      relatedCustomerIssue: req.related_customer_issue || req.relatedIssue || req.customer_issue || null,
      acceptanceCriteria: Array.isArray(req.acceptance_criteria)
        ? req.acceptance_criteria
        : req.acceptanceCriteria
        ? [req.acceptanceCriteria]
        : [],
      status: req.status || 'Draft',
      createdAt: req.created_at || req.createdAt || null,
    }));
  },

  /**
   * Request backend AI to generate requirements from insights/feedback
   * @returns {Promise<Array>}
   */
  async generateRequirements() {
    const response = await api.post('/requirements/generate');
    const data = response.data;
    const items = Array.isArray(data) ? data : data.items || data.requirements || [];
    return items.map((req) => ({
      id: req.id || req._id || String(Date.now()),
      title: req.title || '—',
      description: req.description || '',
      priority: req.priority || 'Medium',
      relatedCustomerIssue: req.related_customer_issue || req.relatedIssue || null,
      acceptanceCriteria: Array.isArray(req.acceptance_criteria)
        ? req.acceptance_criteria
        : req.acceptanceCriteria
        ? [req.acceptanceCriteria]
        : [],
      status: req.status || 'Draft',
    }));
  },

  /**
   * Create single requirement manually via FastAPI backend
   * @param {Object} reqData 
   * @returns {Promise<Object>}
   */
  async createRequirement(reqData) {
    const payload = {
      title: reqData.title.trim(),
      description: reqData.description?.trim() || '',
      priority: reqData.priority || 'Medium',
      related_customer_issue: reqData.relatedCustomerIssue || null,
      acceptance_criteria: reqData.acceptanceCriteria || [],
      status: reqData.status || 'Draft',
    };
    const response = await api.post('/requirements', payload);
    return response.data;
  },

  /**
   * Update requirement status or details via FastAPI backend
   * @param {string} id 
   * @param {Object} updates 
   * @returns {Promise<Object>}
   */
  async updateRequirement(id, updates) {
    const response = await api.put(`/requirements/${id}`, updates);
    return response.data;
  },
};
