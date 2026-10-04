import React from 'react';
import { Link } from 'react-router-dom';
import Button from '../components/common/Button';
import { Compass, Home, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-canvas flex flex-col items-center justify-center p-6 text-center">
      <div className="w-12 h-12 rounded-lg bg-emerald-100/70 border border-emerald-200 text-emerald-700 flex items-center justify-center mb-4">
        <Compass className="w-6 h-6" />
      </div>

      <span className="text-xs font-semibold uppercase tracking-wider text-emerald-700 mb-1">
        404 — Page Not Found
      </span>

      <h1 className="text-2xl font-bold text-slate-900 mb-2">
        We couldn't find the page you're looking for
      </h1>

      <p className="text-sm text-slate-500 max-w-md mb-6 leading-relaxed">
        The requested URL may have moved or doesn't exist. Please check the address or return to your workspace dashboard.
      </p>

      <div className="flex items-center gap-3">
        <Link to="/">
          <Button variant="primary" size="md" icon={Home}>
            Return to Dashboard
          </Button>
        </Link>
        <button
          type="button"
          onClick={() => window.history.back()}
          className="inline-flex items-center gap-1.5 text-xs text-slate-600 hover:text-slate-900 font-medium px-3 py-2"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Go back</span>
        </button>
      </div>
    </div>
  );
}
