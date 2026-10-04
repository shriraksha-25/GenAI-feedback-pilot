import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, X, Sparkles, CheckCircle2 } from 'lucide-react';
import Button from '../common/Button';
import { validateUploadedFile } from '../../utils/validators';
import { formatFileSize } from '../../utils/formatters';

export default function FeedbackForm({ onSubmitText, onUploadFile, isSubmitting }) {
  const [text, setText] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [formError, setFormError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  const fileInputRef = useRef(null);

  const MAX_CHARS = 5000;

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validationErr = validateUploadedFile(file);
    if (validationErr) {
      setFileError(validationErr);
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setFileError(null);
    setSelectedFile(file);
    setFormError(null);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setFileError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleClear = () => {
    setText('');
    handleRemoveFile();
    setFormError(null);
    setSuccessMessage(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    setSuccessMessage(null);

    const hasText = text.trim().length > 0;
    const hasFile = Boolean(selectedFile);

    if (!hasText && !hasFile) {
      setFormError('Please enter feedback text or upload a document to analyze.');
      return;
    }

    try {
      if (hasFile) {
        await onUploadFile(selectedFile);
        setSuccessMessage(`File "${selectedFile.name}" uploaded and submitted for analysis.`);
      } else {
        await onSubmitText(text);
        setSuccessMessage('Feedback recorded and queued for AI analysis.');
      }
      handleClear();
    } catch (err) {
      setFormError(err.message || 'Failed to submit feedback. Please try again.');
    }
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 shadow-subtle p-5 sm:p-6 mb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b border-slate-100 gap-2">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">New Feedback Ingestion</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Submit raw customer notes, support conversations, or upload transcript documents.
          </p>
        </div>
        <span className="text-[11px] font-medium text-slate-400">
          Supported: CSV, TXT, PDF, DOC, DOCX
        </span>
      </div>

      {formError && (
        <div className="mb-4 p-3 rounded-md bg-rose-50 border border-rose-200 text-xs text-rose-800">
          {formError}
        </div>
      )}

      {successMessage && (
        <div className="mb-4 p-3 rounded-md bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Feedback Textarea */}
        <div className="space-y-1.5">
          <div className="flex justify-between items-center text-xs">
            <label htmlFor="feedback-text" className="font-medium text-slate-700">
              Customer Feedback Text
            </label>
            <span
              className={`font-mono text-[11px] ${
                text.length > MAX_CHARS ? 'text-rose-600 font-semibold' : 'text-slate-400'
              }`}
            >
              {text.length} / {MAX_CHARS}
            </span>
          </div>

          <textarea
            id="feedback-text"
            rows={5}
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              if (formError) setFormError(null);
            }}
            placeholder="Paste raw customer feedback, interview transcripts, NPS comments, or support tickets here..."
            disabled={isSubmitting}
            className="w-full p-3 text-sm text-slate-800 placeholder:text-slate-400 rounded-md border border-slate-300 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors disabled:bg-slate-50"
          />
        </div>

        {/* File Upload Area */}
        <div className="pt-1">
          {!selectedFile ? (
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border border-dashed border-slate-300 rounded-md p-4 text-center hover:border-slate-400 hover:bg-slate-50/50 transition-colors cursor-pointer"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv,.txt,.pdf,.doc,.docx"
                onChange={handleFileChange}
                className="hidden"
                disabled={isSubmitting}
              />
              <UploadCloud className="w-6 h-6 mx-auto text-slate-400 mb-1.5" />
              <p className="text-xs font-medium text-slate-700">
                Click to attach batch feedback file or drop document here
              </p>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Up to 15MB (.csv, .txt, .pdf, .doc, .docx)
              </p>
            </div>
          ) : (
            <div className="flex items-center justify-between p-3 rounded-md bg-slate-50 border border-slate-200">
              <div className="flex items-center gap-3 min-w-0">
                <div className="p-2 rounded bg-white border border-slate-200 text-slate-600 flex-shrink-0">
                  <FileText className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="flex flex-col min-w-0">
                  <span className="text-xs font-medium text-slate-800 truncate">
                    {selectedFile.name}
                  </span>
                  <div className="flex items-center gap-2 text-[11px] text-slate-500">
                    <span className="uppercase font-mono">
                      {selectedFile.name.split('.').pop()}
                    </span>
                    <span>•</span>
                    <span>{formatFileSize(selectedFile.size)}</span>
                  </div>
                </div>
              </div>

              <button
                type="button"
                onClick={handleRemoveFile}
                disabled={isSubmitting}
                className="p-1 text-slate-400 hover:text-rose-600 rounded hover:bg-white transition-colors"
                aria-label="Remove attached file"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          )}

          {fileError && (
            <p className="text-xs text-rose-600 mt-1 font-medium">{fileError}</p>
          )}
        </div>

        {/* Buttons */}
        <div className="flex items-center justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleClear}
            disabled={isSubmitting || (!text && !selectedFile)}
          >
            Clear
          </Button>

          <Button
            type="submit"
            variant="primary"
            size="sm"
            icon={Sparkles}
            isLoading={isSubmitting}
            loadingText="Analyzing with AI..."
          >
            Analyze with AI
          </Button>
        </div>
      </form>
    </div>
  );
}
