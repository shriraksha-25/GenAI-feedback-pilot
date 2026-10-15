import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, CornerDownLeft } from 'lucide-react';
import Button from '../common/Button';

export default function ChatInput({ onSendMessage, isLoading, disabled }) {
  const [input, setInput] = useState('');
  const textareaRef = useRef(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading || disabled) return;

    onSendMessage(input.trim());
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="bg-white border-t border-slate-200 p-3 sm:p-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl p-2 focus-within:border-emerald-500 focus-within:bg-white focus-within:ring-1 focus-within:ring-emerald-500 transition-all">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask AI Assistant about customer issues, feature requests, or draft a PRD..."
            disabled={isLoading || disabled}
            className="w-full bg-transparent resize-none border-0 text-xs text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-0 leading-relaxed max-h-36 py-1 px-1"
          />

          <div className="flex items-center gap-1.5 flex-shrink-0">
            <button
              type="submit"
              disabled={!input.trim() || isLoading || disabled}
              className={`p-2 rounded-lg text-white transition-all flex items-center justify-center ${
                !input.trim() || isLoading || disabled
                  ? 'bg-slate-300 cursor-not-allowed text-slate-100'
                  : 'bg-emerald-600 hover:bg-emerald-700 active:scale-95 shadow-xs'
              }`}
              title="Send message (Enter)"
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-emerald-600" />
            FeedbackForge AI Context Active
          </span>
          <span className="hidden sm:inline">
            Press <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] text-slate-600">Enter ↵</kbd> to send, <kbd className="px-1 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] text-slate-600">Shift + Enter</kbd> for newline
          </span>
        </div>
      </form>
    </div>
  );
}
