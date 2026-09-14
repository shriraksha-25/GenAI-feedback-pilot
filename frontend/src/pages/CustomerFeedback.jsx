import {
  FileText,
  MessageSquare,
  Upload,
  X,
  ArrowRight,
} from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function CustomerFeedback() {
  const navigate = useNavigate();

  const [feedback, setFeedback] = useState("");
  const [file, setFile] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];

    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const removeFile = () => {
    setFile(null);
  };

  const handleAnalyze = async () => {
    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/feedback/",
        {
          feedback_text: feedback,
        }
      );

      console.log("Backend response:", response.data);

      navigate("/insights");
    } catch (error) {
      console.error("Error sending feedback:", error);
    }
  };

  return (
    <div className="mx-auto max-w-7xl">

      {/* PAGE HEADER */}

      <div className="mb-8">

        <p className="mb-2 text-xs font-medium text-blue-600">
          Product workspace
        </p>

        <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
          Customer feedback
        </h1>

        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
          Add customer feedback manually or upload a file to analyze
          product issues, requests, and opportunities.
        </p>

      </div>

      {/* FEEDBACK INPUT */}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* TEXT FEEDBACK */}

        <div className="rounded-lg border border-slate-200 bg-white lg:col-span-2">

          <div className="border-b border-slate-100 px-5 py-4">

            <div className="flex items-start gap-3">

              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                <MessageSquare size={17} />
              </div>

              <div>

                <h2 className="text-sm font-semibold text-slate-900">
                  Enter feedback
                </h2>

                <p className="mt-1 text-xs text-slate-500">
                  Paste customer comments, reviews, or support responses.
                </p>

              </div>

            </div>

          </div>

          <div className="p-5">

            <label
              htmlFor="feedback"
              className="mb-2 block text-xs font-medium text-slate-700"
            >
              Customer feedback
            </label>

            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Paste or type customer feedback here..."
              rows={12}
              className="w-full resize-none rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-50"
            />

            <div className="mt-3 flex items-center justify-between">

              <p className="text-xs text-slate-400">
                {feedback.length} characters
              </p>

              <p className="text-xs text-slate-400">
                You can also upload a feedback file.
              </p>

            </div>

          </div>

        </div>

        {/* FILE UPLOAD */}

        <div className="rounded-lg border border-slate-200 bg-white">

          <div className="border-b border-slate-100 px-5 py-4">

            <h2 className="text-sm font-semibold text-slate-900">
              Upload feedback
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Upload a file containing multiple customer responses.
            </p>

          </div>

          <div className="p-5">

            <label
              htmlFor="feedback-file"
              className="flex cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-slate-300 bg-slate-50 px-5 py-10 text-center transition hover:border-blue-300 hover:bg-blue-50/30"
            >

              <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-white text-slate-400 ring-1 ring-slate-200">
                <Upload size={19} />
              </div>

              <p className="text-sm font-medium text-slate-700">
                Choose a file
              </p>

              <p className="mt-1 text-xs text-slate-400">
                CSV, TXT, PDF or DOCX
              </p>

              <span className="mt-4 rounded-md border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600">
                Browse files
              </span>

              <input
                id="feedback-file"
                type="file"
                accept=".csv,.txt,.pdf,.doc,.docx"
                onChange={handleFileChange}
                className="hidden"
              />

            </label>

            {file && (
              <div className="mt-4 flex items-center justify-between rounded-lg border border-slate-200 bg-white p-3">

                <div className="flex min-w-0 items-center gap-3">

                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-500">
                    <FileText size={15} />
                  </div>

                  <div className="min-w-0">

                    <p className="truncate text-xs font-medium text-slate-700">
                      {file.name}
                    </p>

                    <p className="mt-0.5 text-[10px] text-slate-400">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>

                  </div>

                </div>

                <button
                  type="button"
                  onClick={removeFile}
                  className="ml-3 flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                >
                  <X size={14} />
                </button>

              </div>
            )}

          </div>

        </div>

      </div>

      {/* ANALYSIS ACTION */}

      <div className="mt-6 rounded-lg border border-slate-200 bg-white">

        <div className="flex flex-col gap-4 p-5 sm:flex-row sm:items-center sm:justify-between">

          <div>

            <h2 className="text-sm font-semibold text-slate-900">
              Analyze feedback
            </h2>

            <p className="mt-1 text-xs leading-5 text-slate-500">
              Submit the feedback to identify sentiment, issues,
              feature requests, and common themes.
            </p>

          </div>

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!feedback.trim()}
            className="inline-flex w-fit items-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            Analyze with AI
            <ArrowRight size={15} />
          </button>

        </div>

      </div>

      {/* INFORMATION */}

      <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-3">

        <InfoCard
          number="01"
          title="Collect"
          description="Add customer comments or upload a feedback file."
        />

        <InfoCard
          number="02"
          title="Analyze"
          description="AI identifies sentiment, issues, requests, and themes."
        />

        <InfoCard
          number="03"
          title="Act"
          description="Use the insights to plan product improvements."
        />

      </div>

    </div>
  );
}

function InfoCard({
  number,
  title,
  description,
}) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-5">

      <p className="text-[10px] font-semibold tracking-wider text-blue-600">
        {number}
      </p>

      <h3 className="mt-2 text-sm font-semibold text-slate-800">
        {title}
      </h3>

      <p className="mt-1 text-xs leading-5 text-slate-500">
        {description}
      </p>

    </div>
  );
}

export default CustomerFeedback;

