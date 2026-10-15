import React from 'react';
import {
  Sparkles,
  Bot,
  AlertTriangle,
  Lightbulb,
  FileText,
  BarChart3,
  ArrowRight,
} from 'lucide-react';

const suggestedPrompts = [
  {
    icon: AlertTriangle,
    title: 'Analyze Friction Points',
    prompt: 'What are the top friction areas reported by customers across all feedback?',
    color: 'text-amber-600 bg-amber-50 border-amber-200',
  },
  {
    icon: FileText,
    title: 'Generate PRD Specification',
    prompt: 'Draft a complete PRD for 3D Secure checkout failures including user stories and acceptance criteria.',
    color: 'text-emerald-700 bg-emerald-50 border-emerald-200',
  },
  {
    icon: Lightbulb,
    title: 'Clustered Feature Requests',
    prompt: 'Which feature requests have the highest user demand and business impact?',
    color: 'text-violet-700 bg-violet-50 border-violet-200',
  },
  {
    icon: BarChart3,
    title: 'Customer Sentiment Trends',
    prompt: 'Summarize customer sentiment trends and recurring themes from recently ingested feedback.',
    color: 'text-teal-700 bg-teal-50 border-teal-200',
  },
];

export default function EmptyChatState({ onSelectPrompt }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-2xl mx-auto">
      {/* Brand Icon */}
      <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-emerald-600 to-teal-500 text-white flex items-center justify-center shadow-md mb-4">
        <Bot className="w-6 h-6" />
      </div>

      <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mb-2">
        <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
        Product Intelligence AI Assistant
      </div>

      <h2 className="text-xl font-bold text-slate-900 tracking-tight">
        How can I help your product workflow today?
      </h2>
      <p className="text-xs text-slate-500 max-w-md mt-1.5 leading-relaxed">
        Ask questions about customer voice, synthesize friction points, compare feature requests, or automatically write production-ready PRDs.
      </p>

      {/* Suggested prompts grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 w-full text-left">
        {suggestedPrompts.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectPrompt(item.prompt)}
              className="p-3.5 rounded-lg border border-slate-200 bg-white hover:border-emerald-300 hover:shadow-sm transition-all text-left group focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <div className={`p-1 rounded ${item.color}`}>
                    <Icon className="w-3.5 h-3.5" />
                  </div>
                  <span className="text-xs font-bold text-slate-800">
                    {item.title}
                  </span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-emerald-600 group-hover:translate-x-0.5 transition-all" />
              </div>
              <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                "{item.prompt}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}
