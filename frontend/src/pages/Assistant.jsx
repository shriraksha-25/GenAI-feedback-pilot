import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import assistantService from '../services/assistantService';
import ChatSidebar from '../components/chat/ChatSidebar';
import ChatMessage from '../components/chat/ChatMessage';
import ChatInput from '../components/chat/ChatInput';
import EmptyChatState from '../components/chat/EmptyChatState';
import { Bot, Sparkles, AlertCircle, RefreshCw, PanelLeftOpen, PanelLeftClose } from 'lucide-react';
import Button from '../components/common/Button';

export default function Assistant() {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [lastUserMessage, setLastUserMessage] = useState(null);

  const messagesEndRef = useRef(null);

  // Initialize conversations
  useEffect(() => {
    const list = assistantService.getConversations();
    if (list.length === 0) {
      const initialThread = assistantService.createConversation('Product Insights Kickoff');
      setConversations([initialThread]);
      setActiveId(initialThread.id);
    } else {
      setConversations(list);
      setActiveId(list[0].id);
    }
  }, []);

  // Current active conversation
  const activeConversation = conversations.find((c) => c.id === activeId) || null;
  const messages = activeConversation?.messages || [];

  // Auto-scroll to bottom of messages container
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Handle creating a new conversation
  const handleNewConversation = () => {
    const newThread = assistantService.createConversation('New Assistant Chat');
    setConversations((prev) => [newThread, ...prev]);
    setActiveId(newThread.id);
    setError(null);
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  // Handle selecting a conversation
  const handleSelectConversation = (id) => {
    setActiveId(id);
    setError(null);
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  // Handle deleting a conversation
  const handleDeleteConversation = (id) => {
    const updated = assistantService.deleteConversation(id);
    setConversations(updated);

    if (activeId === id) {
      if (updated.length > 0) {
        setActiveId(updated[0].id);
      } else {
        const fallback = assistantService.createConversation('New Assistant Chat');
        setConversations([fallback]);
        setActiveId(fallback.id);
      }
    }
  };

  // Handle sending a message
  const handleSendMessage = async (text) => {
    if (!text.trim() || !activeConversation) return;

    setError(null);
    setLastUserMessage(text);

    const userMsg = {
      id: 'msg_user_' + Date.now(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    // Auto-update thread title if this is the first message or default title
    let updatedTitle = activeConversation.title;
    if (messages.length === 0 || activeConversation.title === 'New Assistant Chat') {
      updatedTitle = text.slice(0, 36) + (text.length > 36 ? '...' : '');
    }

    const updatedMessages = [...messages, userMsg];
    const updatedConversation = {
      ...activeConversation,
      title: updatedTitle,
      messages: updatedMessages,
      updatedAt: new Date().toISOString(),
    };

    // Update in-memory state and localStorage
    assistantService.saveConversation(updatedConversation);
    setConversations((prev) =>
      prev.map((c) => (c.id === activeId ? updatedConversation : c))
    );

    setIsLoading(true);

    try {
      const assistantMsg = await assistantService.sendMessage({
        conversationId: activeId,
        message: text,
        history: updatedMessages,
      });

      const finalMessages = [...updatedMessages, assistantMsg];
      const finalConversation = {
        ...updatedConversation,
        messages: finalMessages,
        updatedAt: new Date().toISOString(),
      };

      assistantService.saveConversation(finalConversation);
      setConversations((prev) =>
        prev.map((c) => (c.id === activeId ? finalConversation : c))
      );
    } catch (err) {
      setError(err.message || 'Failed to generate assistant response. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Retry sending last message
  const handleRetry = () => {
    if (lastUserMessage) {
      handleSendMessage(lastUserMessage);
    }
  };

  const userName = user?.name || user?.email ? (user.name || user.email.split('@')[0]) : 'You';

  return (
    <div className="flex h-[calc(100vh-8.5rem)] rounded-xl border border-slate-200 bg-white overflow-hidden shadow-card">
      {/* Conversation History Sidebar */}
      <ChatSidebar
        conversations={conversations}
        activeConversationId={activeId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
      />

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col min-w-0 bg-white">
        {/* Top Chat Header bar */}
        <div className="h-13 px-4 border-b border-slate-200 flex items-center justify-between bg-white flex-shrink-0">
          <div className="flex items-center gap-2 min-w-0">
            <button
              type="button"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="md:hidden p-1.5 text-slate-500 hover:text-slate-700 rounded-md hover:bg-slate-100"
              title="Toggle history"
            >
              {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
            </button>

            <div className="w-2 h-2 rounded-full bg-emerald-500 flex-shrink-0 animate-pulse" />
            <h2 className="text-xs sm:text-sm font-bold text-slate-900 truncate">
              {activeConversation?.title || 'Product Assistant'}
            </h2>
          </div>

          <div className="flex items-center gap-2">
            <span className="hidden sm:inline-flex items-center gap-1 text-[11px] font-medium text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200/60">
              <Sparkles className="w-3 h-3 text-emerald-600" />
              Connected to Workspace Data
            </span>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mx-4 mt-3 p-3 rounded-lg bg-rose-50 border border-rose-200 flex items-center justify-between gap-3 text-xs text-rose-800 flex-shrink-0">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{error}</span>
            </div>
            <button
              type="button"
              onClick={handleRetry}
              className="inline-flex items-center gap-1 font-semibold text-rose-700 hover:text-rose-900 hover:underline"
            >
              <RefreshCw className="w-3 h-3" /> Retry
            </button>
          </div>
        )}

        {/* Messages Feed or Empty State */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 ? (
            <EmptyChatState onSelectPrompt={handleSendMessage} />
          ) : (
            messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} userName={userName} />
            ))
          )}

          {/* Assistant Loading / Typing State */}
          {isLoading && (
            <div className="flex gap-3 py-3 px-2 sm:px-4 rounded-lg bg-slate-50/70 border border-slate-100 animate-fade-in">
              <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shadow-xs flex-shrink-0">
                <Bot className="w-4 h-4" />
              </div>
              <div className="flex-1 space-y-1.5 pt-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-900">FeedbackForge AI</span>
                  <span className="text-[10px] text-slate-400">analyzing feedback...</span>
                </div>
                <div className="flex items-center gap-1.5 py-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce" style={{ animationDelay: '0ms' }} />
                  <span className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce" style={{ animationDelay: '150ms' }} />
                  <span className="w-2 h-2 rounded-full bg-emerald-600 animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
          disabled={!activeConversation}
        />
      </div>
    </div>
  );
}
