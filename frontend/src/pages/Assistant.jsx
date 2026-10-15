
import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import assistantService from '../services/assistantService';
import ChatSidebar from '../components/chat/ChatSidebar';
import ChatMessage from '../components/chat/ChatMessage';
import ChatInput from '../components/chat/ChatInput';
import EmptyChatState from '../components/chat/EmptyChatState';
import {
  Bot,
  Sparkles,
  AlertCircle,
  PanelLeftOpen,
  PanelLeftClose,
} from 'lucide-react';

const getFeatureId = (feature) =>
  feature?.feature_id ||
  feature?.id ||
  feature?._id ||
  null;

const getEvidenceCount = (feature) =>
  Array.isArray(feature?.source_feedback_ids)
    ? feature.source_feedback_ids.length
    : 0;

const getFeatureLabel = (feature) =>
  feature?.title ||
  feature?.description ||
  feature?.feature_category ||
  'Untitled feature';

function normalizeFeatures(response) {
  const list = Array.isArray(response)
    ? response
    : Array.isArray(response?.value)
      ? response.value
      : Array.isArray(response?.items)
        ? response.items
        : [];

  return list.filter((feature) => getFeatureId(feature));
}

function chooseDefaultFeature(features) {
  if (!features.length) return null;

  return [...features].sort(
    (a, b) => getEvidenceCount(b) - getEvidenceCount(a)
  )[0];
}

export default function Assistant() {
  const { user } = useAuth();

  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [features, setFeatures] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const messagesEndRef = useRef(null);

  const activeConversation =
    conversations.find((item) => item.id === activeId) || null;

  const messages = activeConversation?.messages || [];

  useEffect(() => {
    let cancelled = false;

    async function initialize() {
      setIsInitializing(true);
      setError(null);

      try {
        if (!user?.user_id) {
          throw new Error(
            'Your account session does not contain a user ID. Please sign out and sign in again.'
          );
        }

        const [featureResponse, existing] = await Promise.all([
          assistantService.getFeatures(),
          assistantService.getConversations(user.user_id),
        ]);

        if (cancelled) return;

        const loadedFeatures = normalizeFeatures(featureResponse);
        setFeatures(loadedFeatures);

        const defaultFeature = chooseDefaultFeature(loadedFeatures);
        const defaultFeatureId = getFeatureId(defaultFeature);

        if (existing.length > 0) {
          const hydratedConversations = existing.map((conversation) => {
            const savedFeatureExists = loadedFeatures.some(
              (feature) =>
                getFeatureId(feature) === conversation.featureId
            );

            return {
              ...conversation,
              featureId: savedFeatureExists
                ? conversation.featureId
                : defaultFeatureId,
            };
          });

          setConversations(hydratedConversations);
          setActiveId(hydratedConversations[0].id);
        } else {
          const conversation =
            await assistantService.createConversation({
              userId: user.user_id,
              title: 'Product Insights Kickoff',
              featureId: defaultFeatureId,
            });

          if (cancelled) return;

          setConversations([conversation]);
          setActiveId(conversation.id);

          if (!defaultFeatureId) {
            setError(
              'No product features are available yet. Create a feature and link feedback to it before asking grounded questions.'
            );
          }
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              'Could not load assistant conversations.'
          );
        }
      } finally {
        if (!cancelled) setIsInitializing(false);
      }
    }

    initialize();

    return () => {
      cancelled = true;
    };
  }, [user?.user_id]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  }, [messages, isLoading]);

  const handleFeatureChange = (featureId) => {
    if (!activeId) return;

    setError(null);

    setConversations((previous) =>
      previous.map((conversation) =>
        conversation.id === activeId
          ? { ...conversation, featureId }
          : conversation
      )
    );
  };

  const handleNewConversation = async () => {
    if (!user?.user_id || isLoading) return;

    setError(null);

    try {
      const defaultFeature = chooseDefaultFeature(features);
      const featureId = getFeatureId(defaultFeature);

      const conversation =
        await assistantService.createConversation({
          userId: user.user_id,
          title: 'New Assistant Chat',
          featureId,
        });

      setConversations((previous) => [
        conversation,
        ...previous,
      ]);
      setActiveId(conversation.id);

      if (!featureId) {
        setError(
          'Conversation created, but no product feature is available. Grounded answers may not be possible.'
        );
      }

      if (window.innerWidth < 768) setSidebarOpen(false);
    } catch (err) {
      setError(
        err.message || 'Could not create a new conversation.'
      );
    }
  };

  const handleSelectConversation = async (id) => {
    setError(null);
    setActiveId(id);

    if (window.innerWidth < 768) setSidebarOpen(false);

    const selected = conversations.find(
      (conversation) => conversation.id === id
    );

    if (selected?.messages?.length) return;

    try {
      const conversation =
        await assistantService.getConversation(id);

      setConversations((previous) =>
        previous.map((item) =>
          item.id === id
            ? {
                ...conversation,
                featureId:
                  selected?.featureId || conversation.featureId,
              }
            : item
        )
      );
    } catch (err) {
      setError(
        err.message || 'Could not load conversation messages.'
      );
    }
  };

  const handleDeleteConversation = async (id) => {
    setError(null);

    try {
      await assistantService.deleteConversation(id);

      const remaining = conversations.filter(
        (conversation) => conversation.id !== id
      );

      setConversations(remaining);

      if (activeId === id) {
        if (remaining.length > 0) {
          setActiveId(remaining[0].id);
        } else {
          setActiveId(null);
          await handleNewConversation();
        }
      }
    } catch (err) {
      setError(
        err.message || 'Could not close this conversation.'
      );
    }
  };

  const handleSendMessage = async (text) => {
    const content = text.trim();

    if (!content || !activeConversation || isLoading) {
      return;
    }

    setError(null);

    const conversationId = activeConversation.id;

    // Respect the feature explicitly selected in the dropdown.
    // Never change it based on keywords in the message.
    const featureId = activeConversation.featureId;

    if (!featureId) {
      setError(
        'Select a product feature from the context dropdown before sending your question.'
      );
      return;
    }

    const userMessage = {
      id: `pending-${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString(),
    };

    setConversations((previous) =>
      previous.map((conversation) =>
        conversation.id === conversationId
          ? {
              ...conversation,
              title:
                conversation.messages.length === 0 ||
                conversation.title === 'New Assistant Chat'
                  ? content.slice(0, 36) +
                    (content.length > 36 ? '...' : '')
                  : conversation.title,
              messages: [
                ...conversation.messages,
                userMessage,
              ],
              updatedAt: new Date().toISOString(),
            }
          : conversation
      )
    );

    setIsLoading(true);

    try {
      const result = await assistantService.sendMessage({
        conversationId,
        message: content,
        featureId,
      });

      setConversations((previous) =>
        previous.map((conversation) => {
          if (conversation.id !== conversationId) {
            return conversation;
          }

          const currentMessages = conversation.messages.filter(
            (message) => message.id !== userMessage.id
          );

          return {
            ...conversation,
            featureId,
            messages: [
              ...currentMessages,
              result.userMessage || userMessage,
              result.assistantMessage,
            ],
            updatedAt: new Date().toISOString(),
          };
        })
      );
    } catch (err) {
      setError(
        `${err.message || 'Assistant response failed.'} Your message may already have been saved. Check the conversation before sending it again.`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const userName =
    user?.name ||
    (user?.email ? user.email.split('@')[0] : 'You');

  return (
    <div className="flex h-[calc(100vh-8.5rem)] rounded-xl border border-slate-200 bg-white overflow-hidden shadow-card">
      <ChatSidebar
        conversations={conversations}
        activeConversationId={activeId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen((open) => !open)}
      />

      <div className="flex-1 flex flex-col min-w-0 bg-white">
        <div className="min-h-13 px-4 py-2 border-b border-slate-200 flex items-center justify-between gap-3 bg-white flex-shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            <button
              type="button"
              onClick={() =>
                setSidebarOpen((open) => !open)
              }
              className="md:hidden p-1.5 text-slate-500 hover:text-slate-700 rounded-md hover:bg-slate-100"
              title="Toggle history"
            >
              {sidebarOpen ? (
                <PanelLeftClose className="w-4 h-4" />
              ) : (
                <PanelLeftOpen className="w-4 h-4" />
              )}
            </button>

            <div className="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0" />

            <h2 className="text-xs sm:text-sm font-bold text-slate-900 truncate">
              {activeConversation?.title || 'Product Assistant'}
            </h2>
          </div>

          <div className="flex items-center gap-2 flex-shrink-0">
            <label
              htmlFor="assistant-feature"
              className="hidden sm:block text-[11px] text-slate-500"
            >
              Context:
            </label>

            <select
              id="assistant-feature"
              aria-label="Select product feature context"
              value={activeConversation?.featureId || ''}
              onChange={(event) =>
                handleFeatureChange(event.target.value)
              }
              disabled={
                isInitializing ||
                isLoading ||
                features.length === 0 ||
                !activeConversation
              }
              className="max-w-[180px] sm:max-w-[260px] rounded-md border border-slate-200 bg-white px-2 py-1.5 text-[11px] text-slate-700 outline-none focus:border-emerald-500"
              title="Choose the product feature used to ground assistant answers"
            >
              {features.length === 0 && (
                <option value="">No features available</option>
              )}

              {features.map((feature) => (
                <option
                  key={getFeatureId(feature)}
                  value={getFeatureId(feature)}
                >
                  {getFeatureLabel(feature)}
                  {getEvidenceCount(feature) > 0
                    ? ` (${getEvidenceCount(feature)} feedback)`
                    : ' (no linked feedback)'}
                </option>
              ))}
            </select>

            <span className="hidden lg:inline-flex items-center gap-1 text-[11px] font-medium text-emerald-800 bg-emerald-50 px-2 py-1 rounded-full border border-emerald-200/60">
              <Sparkles className="w-3 h-3 text-emerald-600" />
              MongoDB Chat
            </span>
          </div>
        </div>

        {error && (
          <div className="mx-4 mt-3 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-start gap-2 text-xs text-rose-800 flex-shrink-0">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {isInitializing ? (
            <div className="text-center text-sm text-slate-500 py-10">
              Loading your conversations...
            </div>
          ) : messages.length === 0 ? (
            <EmptyChatState onSelectPrompt={handleSendMessage} />
          ) : (
            messages.map((message) => (
              <ChatMessage
                key={message.id}
                message={message}
                userName={userName}
              />
            ))
          )}

          {isLoading && (
            <div className="flex gap-3 py-3 px-2 sm:px-4 rounded-lg bg-slate-50/70 border border-slate-100">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="text-xs text-slate-500 pt-2">
                Analyzing product context...
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading || isInitializing}
          disabled={!activeConversation || isInitializing}
        />
      </div>
    </div>
  );
}
