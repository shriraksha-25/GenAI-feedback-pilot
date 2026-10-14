import React, { useState } from 'react';
import { Bot, User, Copy, Check, Sparkles } from 'lucide-react';

/**
 * Formats basic markdown elements (headings, bold, lists, quotes, tables) cleanly in React
 */
function MarkdownRenderer({ content }) {
  if (!content) return null;

  const lines = content.split('\n');

  return (
    <div className="space-y-2 text-xs text-slate-800 leading-relaxed font-normal">
      {lines.map((line, idx) => {
        const trimmed = line.trim();

        // Level 3 heading
        if (trimmed.startsWith('### ')) {
          return (
            <h3 key={idx} className="text-sm font-bold text-slate-900 mt-3 mb-1 flex items-center gap-1.5">
              {trimmed.replace('### ', '')}
            </h3>
          );
        }

        // Level 4 heading
        if (trimmed.startsWith('#### ')) {
          return (
            <h4 key={idx} className="text-xs font-bold text-slate-900 uppercase tracking-wider mt-2.5 mb-1 text-emerald-800">
              {trimmed.replace('#### ', '')}
            </h4>
          );
        }

        // Blockquote
        if (trimmed.startsWith('> ')) {
          return (
            <blockquote key={idx} className="border-l-2 border-emerald-500 pl-3 py-1 my-1.5 bg-emerald-50/50 rounded-r text-slate-700 italic">
              {trimmed.replace('> ', '')}
            </blockquote>
          );
        }

        // Bullet point
        if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
          const bulletText = trimmed.slice(2);
          return (
            <div key={idx} className="flex items-start gap-2 pl-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 flex-shrink-0" />
              <span>{formatInlineMarkdown(bulletText)}</span>
            </div>
          );
        }

        // Numbered list item
        if (/^\d+\.\s/.test(trimmed)) {
          const numMatch = trimmed.match(/^(\d+\.)\s(.*)/);
          if (numMatch) {
            return (
              <div key={idx} className="flex items-start gap-2 pl-2">
                <span className="font-semibold text-emerald-700 flex-shrink-0">{numMatch[1]}</span>
                <span>{formatInlineMarkdown(numMatch[2])}</span>
              </div>
            );
          }
        }

        // Horizontal separator or empty line
        if (trimmed === '---') {
          return <hr key={idx} className="my-2 border-slate-200" />;
        }

        if (trimmed === '') {
          return <div key={idx} className="h-1" />;
        }

        // Normal paragraph
        return <p key={idx}>{formatInlineMarkdown(line)}</p>;
      })}
    </div>
  );
}

/**
 * Replaces **bold** and `code` with styled spans
 */
function formatInlineMarkdown(text) {
  if (!text) return '';

  const parts = [];
  let remaining = text;
  let keyIdx = 0;

  // Regex to match **bold** or `code` or *italic*
  const pattern = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;
  let match;
  let lastIndex = 0;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const token = match[0];
    if (token.startsWith('**') && token.endsWith('**')) {
      parts.push(
        <strong key={keyIdx++} className="font-semibold text-slate-900">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('`') && token.endsWith('`')) {
      parts.push(
        <code key={keyIdx++} className="px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 font-mono text-[11px] border border-slate-200">
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      parts.push(
        <em key={keyIdx++} className="italic text-slate-700">
          {token.slice(1, -1)}
        </em>
      );
    }
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts.length > 0 ? parts : text;
}

export default function ChatMessage({ message, userName = 'You' }) {
  const isAssistant = message.role === 'assistant';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const timeFormatted = message.timestamp
    ? new Date(message.timestamp).toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
      })
    : '';

  return (
    <div
      className={`flex gap-3 py-3 px-2 sm:px-4 rounded-lg transition-colors group ${
        isAssistant ? 'bg-slate-50/70 border border-slate-100' : 'bg-transparent'
      }`}
    >
      {/* Avatar */}
      <div className="flex-shrink-0">
        {isAssistant ? (
          <div className="w-8 h-8 rounded-lg bg-emerald-600 text-white flex items-center justify-center shadow-xs">
            <Bot className="w-4 h-4" />
          </div>
        ) : (
          <div className="w-8 h-8 rounded-lg bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center">
            {userName.charAt(0).toUpperCase()}
          </div>
        )}
      </div>

      {/* Message Body */}
      <div className="flex-1 min-w-0 space-y-1">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-slate-900">
              {isAssistant ? 'FeedbackForge AI' : userName}
            </span>
            {isAssistant && (
              <span className="text-[10px] bg-violet-100 text-violet-700 font-semibold px-1.5 py-0.2 rounded-full flex items-center gap-1">
                <Sparkles className="w-2.5 h-2.5" /> Intelligence Engine
              </span>
            )}
            <span className="text-[10px] text-slate-400">{timeFormatted}</span>
          </div>

          {/* Action button */}
          <button
            type="button"
            onClick={handleCopy}
            title="Copy message"
            className="opacity-0 group-hover:opacity-100 p-1 text-slate-400 hover:text-slate-600 rounded hover:bg-white transition-opacity"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-600" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {/* Content */}
        <div className="pt-0.5">
          {isAssistant ? (
            <MarkdownRenderer content={message.content} />
          ) : (
            <p className="text-xs text-slate-800 whitespace-pre-wrap leading-relaxed font-medium">
              {message.content}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
