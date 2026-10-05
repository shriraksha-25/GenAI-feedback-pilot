import api from './api';

export function normalizeFeedbackItem(item) {
  if (!item) return null;

  const aiStatus = item.ai_analysis?.ai_status;

  return {
    id: item.id || item._id || item.feedback_id || '',

    text:
      item.feedback_text ||
      item.description ||
      item.text ||
      item.feedback ||
      item.content ||
      item.comment ||
      '—',

    source:
      item.source ||
      item.channel ||
      'Direct Input',

    date:
      item.created_at ||
      item.date ||
      item.createdAt ||
      item.timestamp ||
      null,

    status:
      item.status ||
      'Pending',

    analysisStatus:
      item.analysis_status ||
      item.analysisStatus ||
      (aiStatus === 'completed'
        ? 'Analyzed'
        : aiStatus === 'failed'
          ? 'Failed'
          : 'Pending'),

    customer:
      item.customer_name ||
      item.customer ||
      item.customer_segment ||
      item.user ||
      null,

    productArea:
      item.product_area ||
      item.product ||
      null,

    email:
      item.customer_email ||
      item.email ||
      null,

    tags:
      Array.isArray(item.tags)
        ? item.tags
        : [],

    priority:
      item.priority ||
      null,
  };
}

export function normalizeFeedbackResponse(data) {
  if (!data) return [];

  const list = Array.isArray(data)
    ? data
    : data.items ||
      data.feedback ||
      data.results ||
      [];

  return list.map(normalizeFeedbackItem);
}

export const feedbackService = {
  async getFeedback(params = {}) {
    const response = await api.get('/feedback', {
      params,
    });

    return normalizeFeedbackResponse(response.data);
  },

  async submitFeedback({
    text,
    source = 'Web App',
    customer = null,
    productArea = null,
  }) {
    const payload = {
      feedback_text: text.trim(),
      text: text.trim(),
      source,

      ...(customer
        ? {
            customer,
            customer_segment: customer,
          }
        : {}),

      ...(productArea
        ? {
            product_area: productArea,
          }
        : {}),
    };

    const response = await api.post('/feedback', payload);

    return normalizeFeedbackItem(response.data);
  },

  async uploadFeedbackFile(file, onUploadProgress) {
    const formData = new FormData();

    formData.append('file', file);

    const response = await api.post(
      '/feedback/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress,
      }
    );

    return response.data;
  },

  async analyzeFeedback(feedbackIds = null) {
    const payload = feedbackIds
      ? { feedback_ids: feedbackIds }
      : {};

    const response = await api.post(
      '/feedback/analyze',
      payload
    );

    return response.data;
  },
};