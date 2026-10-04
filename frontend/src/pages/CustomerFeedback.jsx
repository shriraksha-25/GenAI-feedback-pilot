import React, { useState, useEffect } from 'react';
import { feedbackService } from '../services/feedbackService';
import FeedbackForm from '../components/feedback/FeedbackForm';
import FeedbackTable from '../components/feedback/FeedbackTable';
import EmptyState from '../components/common/EmptyState';
import ErrorState from '../components/common/ErrorState';
import { TableSkeleton } from '../components/common/LoadingState';
import Button from '../components/common/Button';
import { MessageSquareQuote, RefreshCw, Sparkles } from 'lucide-react';

export default function CustomerFeedback() {
  const [feedbackList, setFeedbackList] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [analysisNotice, setAnalysisNotice] = useState(null);

  const loadFeedback = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await feedbackService.getFeedback();
      setFeedbackList(data);
    } catch (err) {
      setError(err.message || 'Unable to load customer feedback.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadFeedback();
  }, []);

  const handleSubmitText = async (text) => {
    setIsSubmitting(true);
    try {
      await feedbackService.submitFeedback({ text });
      await loadFeedback();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUploadFile = async (file) => {
    setIsSubmitting(true);
    try {
      await feedbackService.uploadFeedbackFile(file);
      await loadFeedback();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRunBatchAnalysis = async () => {
    setIsAnalyzing(true);
    setAnalysisNotice(null);
    try {
      await feedbackService.analyzeFeedback();
      setAnalysisNotice('AI analysis batch triggered successfully. Updating feedback records...');
      await loadFeedback();
    } catch (err) {
      setError(err.message || 'Failed to trigger batch AI analysis.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200/60 gap-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            Customer Feedback
          </h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Collect customer feedback and send it for AI-powered analysis.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={loadFeedback}
            icon={RefreshCw}
            disabled={isLoading}
          >
            Refresh
          </Button>

          {feedbackList.length > 0 && (
            <Button
              variant="ai"
              size="sm"
              onClick={handleRunBatchAnalysis}
              isLoading={isAnalyzing}
              loadingText="Analyzing Batch..."
              icon={Sparkles}
            >
              Analyze All Feedback
            </Button>
          )}
        </div>
      </div>

      {analysisNotice && (
        <div className="p-3.5 rounded-md bg-emerald-50 border border-emerald-200 text-xs text-emerald-800">
          {analysisNotice}
        </div>
      )}

      {error && (
        <ErrorState
          title="Feedback Service Error"
          message={error}
          onRetry={loadFeedback}
        />
      )}

      {/* Submission Form */}
      <FeedbackForm
        onSubmitText={handleSubmitText}
        onUploadFile={handleUploadFile}
        isSubmitting={isSubmitting}
      />

      {/* Feedback Records Section */}
      <div className="space-y-4">
        {isLoading ? (
          <TableSkeleton rows={5} cols={5} />
        ) : feedbackList.length === 0 ? (
          <EmptyState
            icon={MessageSquareQuote}
            title="No customer feedback yet"
            description="Submit your first piece of customer feedback above to start generating product insights."
          />
        ) : (
          <FeedbackTable items={feedbackList} />
        )}
      </div>
    </div>
  );
}
