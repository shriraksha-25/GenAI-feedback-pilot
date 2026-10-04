import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import Button from './Button';

export default function ErrorState({
  title = 'Something went wrong',
  message = 'An unexpected error occurred while processing your request.',
  onRetry,
  isRetrying = false,
  className = '',
}) {
  return (
    <div
      role="alert"
      className={`p-6 rounded-lg border border-rose-200 bg-rose-50/50 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${className}`}
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-full bg-rose-100 text-rose-600 flex-shrink-0 mt-0.5 sm:mt-0">
          <AlertCircle className="w-5 h-5" />
        </div>
        <div>
          <h4 className="text-sm font-semibold text-rose-900">{title}</h4>
          <p className="text-sm text-rose-700 mt-0.5 leading-relaxed">{message}</p>
        </div>
      </div>

      {onRetry && (
        <Button
          variant="outline"
          size="sm"
          onClick={onRetry}
          isLoading={isRetrying}
          loadingText="Retrying..."
          icon={RefreshCw}
          className="bg-white border-rose-200 text-rose-800 hover:bg-rose-50 flex-shrink-0"
        >
          Retry
        </Button>
      )}
    </div>
  );
}
