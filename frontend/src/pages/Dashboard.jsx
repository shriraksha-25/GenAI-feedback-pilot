import {
  ArrowRight,
  BarChart3,
  CheckCircle2,
  CircleAlert,
  Lightbulb,
  MessageSquare,
  Plus,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  return (
    <div className="mx-auto max-w-7xl">

      {/* Page heading */}

      <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">

        <div>

          <p className="mb-2 text-xs font-medium text-blue-600">
            Product workspace
          </p>

          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            Product overview
          </h1>

          <p className="mt-2 max-w-2xl text-sm text-slate-500">
            Monitor customer feedback and turn it into actionable
            product decisions.
          </p>

        </div>

        <button
          onClick={() => navigate("/feedback")}
          className="inline-flex w-fit items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
        >
          <Plus size={16} />
          Add feedback
        </button>

      </div>


      {/* Statistics */}

      <div className="mb-6 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

        {/* Total feedback */}

        <div className="rounded-lg border border-slate-200 bg-white p-5">

          <div className="flex items-center justify-between">

            <p className="text-sm text-slate-500">
              Total feedback
            </p>

            <MessageSquare
              size={17}
              className="text-slate-400"
            />

          </div>

          <p className="mt-4 text-3xl font-semibold text-slate-900">
            0
          </p>

          <p className="mt-1 text-xs text-slate-400">
            No feedback submitted
          </p>

        </div>


        {/* Issues */}

        <div className="rounded-lg border border-slate-200 bg-white p-5">

          <div className="flex items-center justify-between">

            <p className="text-sm text-slate-500">
              Issues identified
            </p>

            <CircleAlert
              size={17}
              className="text-slate-400"
            />

          </div>

          <p className="mt-4 text-3xl font-semibold text-slate-900">
            0
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Waiting for analysis
          </p>

        </div>


        {/* Feature requests */}

        <div className="rounded-lg border border-slate-200 bg-white p-5">

          <div className="flex items-center justify-between">

            <p className="text-sm text-slate-500">
              Feature requests
            </p>

            <Lightbulb
              size={17}
              className="text-slate-400"
            />

          </div>

          <p className="mt-4 text-3xl font-semibold text-slate-900">
            0
          </p>

          <p className="mt-1 text-xs text-slate-400">
            No requests identified
          </p>

        </div>


        {/* Pending actions */}

        <div className="rounded-lg border border-slate-200 bg-white p-5">

          <div className="flex items-center justify-between">

            <p className="text-sm text-slate-500">
              Pending actions
            </p>

            <CheckCircle2
              size={17}
              className="text-slate-400"
            />

          </div>

          <p className="mt-4 text-3xl font-semibold text-slate-900">
            0
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Nothing requires attention
          </p>

        </div>

      </div>


      {/* Main analytics section */}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* Feedback activity */}

        <div className="rounded-lg border border-slate-200 bg-white lg:col-span-2">

          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">

            <div>

              <h2 className="text-sm font-semibold text-slate-900">
                Feedback activity
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Customer feedback received over time
              </p>

            </div>

            <BarChart3
              size={17}
              className="text-slate-400"
            />

          </div>


          <div className="flex h-72 items-center justify-center p-6">

            <div className="text-center">

              <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-slate-100">

                <BarChart3
                  size={18}
                  className="text-slate-400"
                />

              </div>

              <p className="text-sm font-medium text-slate-700">
                No activity yet
              </p>

              <p className="mt-1 text-xs text-slate-400">
                Feedback trends will appear here after customers
                submit feedback.
              </p>

            </div>

          </div>

        </div>


        {/* Sentiment */}

        <div className="rounded-lg border border-slate-200 bg-white">

          <div className="border-b border-slate-100 px-5 py-4">

            <h2 className="text-sm font-semibold text-slate-900">
              Customer sentiment
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Sentiment across analyzed feedback
            </p>

          </div>


          <div className="p-5">

            <div className="mb-7 flex justify-center">

              <div className="flex h-36 w-36 items-center justify-center rounded-full border-[12px] border-slate-100">

                <div className="text-center">

                  <p className="text-2xl font-semibold text-slate-900">
                    0%
                  </p>

                  <p className="mt-1 text-[10px] text-slate-400">
                    analyzed
                  </p>

                </div>

              </div>

            </div>


            <div className="space-y-4">

              <SentimentRow
                label="Positive"
                value="0%"
                indicator="bg-green-500"
              />

              <SentimentRow
                label="Neutral"
                value="0%"
                indicator="bg-slate-400"
              />

              <SentimentRow
                label="Negative"
                value="0%"
                indicator="bg-red-500"
              />

            </div>

          </div>

        </div>

      </div>


      {/* Recent information */}

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-2">

        {/* Recent feedback */}

        <div className="rounded-lg border border-slate-200 bg-white">

          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">

            <div>

              <h2 className="text-sm font-semibold text-slate-900">
                Recent feedback
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Latest customer responses
              </p>

            </div>

            <button
              onClick={() => navigate("/feedback")}
              className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700"
            >
              View all
              <ArrowRight size={13} />
            </button>

          </div>


          <div className="flex min-h-52 items-center justify-center p-6">

            <div className="text-center">

              <MessageSquare
                size={24}
                className="mx-auto mb-3 text-slate-300"
              />

              <p className="text-sm font-medium text-slate-700">
                No feedback yet
              </p>

              <p className="mt-1 text-xs text-slate-400">
                Submitted customer feedback will appear here.
              </p>

              <button
                onClick={() => navigate("/feedback")}
                className="mt-4 text-xs font-medium text-blue-600 hover:text-blue-700"
              >
                Add your first feedback
              </button>

            </div>

          </div>

        </div>


        {/* AI insights */}

        <div className="rounded-lg border border-slate-200 bg-white">

          <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">

            <div>

              <h2 className="text-sm font-semibold text-slate-900">
                Product insights
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Important patterns found in feedback
              </p>

            </div>

            <button
              onClick={() => navigate("/insights")}
              className="flex items-center gap-1 text-xs font-medium text-blue-600 hover:text-blue-700"
            >
              View insights
              <ArrowRight size={13} />
            </button>

          </div>


          <div className="flex min-h-52 items-center justify-center p-6">

            <div className="text-center">

              <Lightbulb
                size={24}
                className="mx-auto mb-3 text-slate-300"
              />

              <p className="text-sm font-medium text-slate-700">
                No insights available
              </p>

              <p className="mt-1 max-w-xs text-xs leading-5 text-slate-400">
                AI-generated issues, feature requests, and trends
                will appear after feedback is analyzed.
              </p>

            </div>

          </div>

        </div>

      </div>


      {/* Workflow */}

      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-5">

        <div className="mb-5">

          <h2 className="text-sm font-semibold text-slate-900">
            Product workflow
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            How feedback moves through the workspace
          </p>

        </div>


        <div className="grid grid-cols-1 gap-3 md:grid-cols-4">

          <WorkflowStep
            number="01"
            title="Collect feedback"
            description="Gather customer responses."
          />

          <WorkflowStep
            number="02"
            title="AI analysis"
            description="Identify issues and requests."
          />

          <WorkflowStep
            number="03"
            title="Plan"
            description="Prioritize product opportunities."
          />

          <WorkflowStep
            number="04"
            title="Requirements"
            description="Create actionable requirements."
          />

        </div>

      </div>

    </div>
  );
}


/* =========================================
   SENTIMENT ROW
========================================= */

function SentimentRow({ label, value, indicator }) {
  return (
    <div className="flex items-center justify-between">

      <div className="flex items-center gap-2">

        <span
          className={`h-2 w-2 rounded-full ${indicator}`}
        />

        <span className="text-xs text-slate-600">
          {label}
        </span>

      </div>

      <span className="text-xs font-medium text-slate-800">
        {value}
      </span>

    </div>
  );
}


/* =========================================
   WORKFLOW STEP
========================================= */

function WorkflowStep({ number, title, description }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">

      <p className="text-[10px] font-semibold tracking-wider text-blue-600">
        {number}
      </p>

      <p className="mt-2 text-xs font-semibold text-slate-800">
        {title}
      </p>

      <p className="mt-1 text-[11px] leading-4 text-slate-500">
        {description}
      </p>

    </div>
  );
}

export default Dashboard;