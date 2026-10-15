
import api from './api';

const WORKSPACE_ID = 'default-workspace';

function getList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.features)) return data.features;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function normalizeMessage(message) {
  return {
    id: message.message_id || message.id || crypto.randomUUID(),
    role: message.role || 'assistant',
    content: message.content || '',
    timestamp:
      message.created_at ||
      message.timestamp ||
      new Date().toISOString(),
  };
}

function normalizeConversation(conversation, messages = []) {
  return {
    id: conversation.conversation_id || conversation.id,
    title: conversation.title || 'New Assistant Chat',
    featureId: conversation.feature_id || null,
    messages: messages.map(normalizeMessage),
    updatedAt:
      conversation.updated_at ||
      conversation.updatedAt ||
      conversation.created_at ||
      new Date().toISOString(),
    status: conversation.status || 'active',
  };
}

const assistantService = {
  workspaceId: WORKSPACE_ID,

  async getFeatures() {
    const response = await api.get('/features');
    return getList(response.data);
  },

  async getConversations(userId) {
    if (!userId) {
      throw new Error(
        'Your user ID is missing. Please sign in again.'
      );
    }

    const response = await api.get('/chat/conversations', {
      params: {
        workspace_id: WORKSPACE_ID,
        user_id: userId,
      },
    });

    const conversations = getList(response.data);

    const hydrated = await Promise.all(
      conversations.map(async (conversation) => {
        const id =
          conversation.conversation_id || conversation.id;

        try {
          const detail = await api.get(
            `/chat/conversations/${encodeURIComponent(id)}`
          );

          return normalizeConversation(
            detail.data,
            detail.data.messages || []
          );
        } catch {
          return normalizeConversation(conversation, []);
        }
      })
    );

    return hydrated.sort(
      (a, b) =>
        new Date(b.updatedAt).getTime() -
        new Date(a.updatedAt).getTime()
    );
  },

  async createConversation({
    userId,
    title = 'New Assistant Chat',
    featureId = null,
  }) {
    if (!userId) {
      throw new Error(
        'Your user ID is missing. Please sign in again.'
      );
    }

    const response = await api.post('/chat/conversations', {
      workspace_id: WORKSPACE_ID,
      user_id: userId,
      title,
      ...(featureId ? { feature_id: featureId } : {}),
    });

    return normalizeConversation(response.data, []);
  },

  async getConversation(conversationId) {
    const response = await api.get(
      `/chat/conversations/${encodeURIComponent(conversationId)}`
    );

    return normalizeConversation(
      response.data,
      response.data.messages || []
    );
  },

  async sendMessage({
    conversationId,
    message,
    featureId = null,
  }) {
    const response = await api.post(
      `/chat/conversations/${encodeURIComponent(
        conversationId
      )}/messages`,
      {
        workspace_id: WORKSPACE_ID,
        content: message.trim(),
        ...(featureId ? { feature_id: featureId } : {}),
      }
    );

    const assistantMessage = response.data?.assistant_message;

    if (!assistantMessage?.content) {
      throw new Error(
        'The server did not return an assistant response.'
      );
    }

    return {
      userMessage: response.data.user_message
        ? normalizeMessage(response.data.user_message)
        : null,
      assistantMessage: normalizeMessage(assistantMessage),
    };
  },

  async deleteConversation(conversationId) {
    // The backend supports closing conversations, not permanent deletion.
    await api.patch(
      `/chat/conversations/${encodeURIComponent(
        conversationId
      )}/close`
    );
  },
};

export default assistantService;
