import api from './api';

/**
 * Normalizes a single feedback item from FastAPI/MongoDB
 * Ensures safe fallbacks and consistent field naming across components
 */
export function normalizeFeedbackItem(item) {
  if (!item) return null;
  return {
    id: item.id || item._id || '',
    text: item.feedback_text || item.text || item.feedback || item.content || item.comment || '—',
    source: item.source || item.channel || 'Direct Input',
    date: item.created_at || item.date || item.createdAt || item.timestamp || null,
    status: item.status || 'Pending',
    analysisStatus: item.analysis_status || item.analysisStatus || (item.analyzed ? 'Analyzed' : 'Pending'),
    customer: item.customer_name || item.customer || item.customer_segment || item.user || null,
    productArea: item.product_area || null,
    email: item.customer_email || item.email || null,
    tags: Array.isArray(item.tags) ? item.tags : [],
    priority: item.priority || null,
  };
}

/**
 * Normalizes array of feedback records
 */
export function normalizeFeedbackResponse(data) {
  if (!data) return [];
  const list = Array.isArray(data) ? data : data.items || data.feedback || data.results || [];
  return list.map(normalizeFeedbackItem);
}

export const feedbackService = {
  /**
   * Fetch all feedback records from FastAPI
   * @param {Object} params - optional query filters (e.g. status, search)
   * @returns {Promise<Array>}
   */
  async getFeedback(params = {}) {
    const response = await api.get('/feedback', { params });
    return normalizeFeedbackResponse(response.data);
  },

  /**
   * Submit text feedback to FastAPI backend
   * @param {Object} data 
   * @returns {Promise<Object>}
   */
  async submitFeedback({ text, source = 'Web App', customer = null, productArea = null }) {
    const payload = {
      feedback_text: text.trim(),
      text: text.trim(),
      source,
      ...(customer ? { customer, customer_segment: customer } : {}),
      ...(productArea ? { product_area: productArea } : {}),
    };
    const response = await api.post('/feedback', payload);
    return normalizeFeedbackItem(response.data);
  },

  /**
   * Upload feedback file (CSV, TXT, PDF, DOC, DOCX) to FastAPI backend
   * @param {File} file 
   * @param {Function} onUploadProgress 
   * @returns {Promise<Object>}
   */
  async uploadFeedbackFile(file, onUploadProgress) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/feedback/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  /**
   * Trigger AI analysis on submitted feedback via FastAPI backend
   * @param {Array<string>} feedbackIds - optional array of feedback IDs
   * @returns {Promise<Object>}
   */
  async analyzeFeedback(feedbackIds = null) {
    const payload = feedbackIds ? { feedback_ids: feedbackIds } : {};
    const response = await api.post('/feedback/analyze', payload);
    return response.data;
  },
};
