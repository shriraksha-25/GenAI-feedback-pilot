import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  FileText,
  Lightbulb,
  MessageSquare,
  Minus,
  Sparkles,
  Target,
  TrendingUp,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

function Insights() {
  const navigate = useNavigate();

  // Temporary mock data
  // Later this can be replaced with the FastAPI response.
  const insights = {
    feedbackAnalyzed: 24,
    issuesIdentified: 8,
    featureRequestsCount: 6,
    themesDetected: 5,

    sentiment: {
      positive: 62,
      neutral: 25,
      negative: 13,
    },

    issues: [
      {
        issue: "Slow response time",
        mentions: 12,
        priority: "High",
      },
      {
        issue: "Difficult navigation",
        mentions: 8,
        priority: "High",
      },
      {
        issue: "Missing product information",
        mentions: 5,
        priority: "Medium",
      },
    ],

    features: [
      {
        feature: "Faster search",
        requests: 9,
        priority: "High",
      },
      {
        feature: "Personalized recommendations",
        requests: 7,
        priority: "High",
      },
      {
        feature: "Mobile notifications",
        requests: 4,
        priority: "Medium",
      },
    ],

    themes: [
      "Performance",
      "User Experience",
      "Search",
      "Personalization",
      "Mobile Experience",
    ],

    opportunities: [
      {
        number: "01",
        title: "Improve product performance",
        description:
          "Address recurring complaints about slow response times.",
        priority: "High",
      },
      {
        number: "02",
        title: "Simplify navigation",
        description:
          "Improve the user journey and make important features easier to find.",
        priority: "High",
      },
      {
        number: "03",
        title: "Improve search experience",
        description:
          "Introduce faster and more relevant product search.",
        priority: "Medium",
      },
    ],
  };

  return (
    <div className="space-y-8">
      {/* ================= HEADER ================= */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-blue-600">
            AI Analysis
          </p>

          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-slate-900">
            Customer Insights
          </h1>

          <p className="mt-1 max-w-2xl text-sm text-slate-500">
            Explore AI-generated insights from customer feedback.
          </p>
        </div>

        <div className="flex w-fit items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2">
          <CheckCircle2 size={16} className="text-emerald-600" />

          <span className="text-xs font-medium text-emerald-700">
            Analysis complete
          </span>
        </div>
      </div>

      {/* ================= METRIC CARDS ================= */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={MessageSquare}
          value={insights.feedbackAnalyzed}
          title="Feedback Analyzed"
          description="Customer responses processed"
        />

        <MetricCard
          icon={AlertCircle}
          value={insights.issuesIdentified}
          title="Issues Identified"
          description="Pain points detected"
        />

        <MetricCard
          icon={Lightbulb}
          value={insights.featureRequestsCount}
          title="Feature Requests"
          description="Potential product improvements"
        />

        <MetricCard
          icon={Target}
          value={insights.themesDetected}
          title="Themes Detected"
          description="Recurring patterns found"
        />
      </div>

      {/* ================= SENTIMENT + AI SUMMARY ================= */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* SENTIMENT */}
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Customer Sentiment
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Overall sentiment across analyzed feedback
              </p>
            </div>

            <TrendingUp size={18} className="text-blue-600" />
          </div>

          <div className="mt-6 flex items-end gap-2">
            <span className="text-4xl font-semibold text-slate-900">
              {insights.sentiment.positive}%
            </span>

            <span className="mb-1 text-xs font-medium text-emerald-600">
              Positive
            </span>
          </div>

          {/* Sentiment Distribution */}
          <div className="mt-5 flex h-3 w-full overflow-hidden rounded-full bg-slate-100">
            <div
              className="bg-emerald-500"
              style={{
                width: `${insights.sentiment.positive}%`,
              }}
            />

            <div
              className="bg-slate-300"
              style={{
                width: `${insights.sentiment.neutral}%`,
              }}
            />

            <div
              className="bg-red-400"
              style={{
                width: `${insights.sentiment.negative}%`,
              }}
            />
          </div>

          {/* Sentiment Details */}
          <div className="mt-6 grid grid-cols-3 gap-4">
            <SentimentItem
              icon={TrendingUp}
              label="Positive"
              value={`${insights.sentiment.positive}%`}
            />

            <SentimentItem
              icon={Minus}
              label="Neutral"
              value={`${insights.sentiment.neutral}%`}
            />

            <SentimentItem
              icon={AlertCircle}
              label="Negative"
              value={`${insights.sentiment.negative}%`}
            />
          </div>
        </div>

        {/* AI SUMMARY */}
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50">
              <Sparkles size={17} className="text-blue-600" />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                AI Summary
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Key findings from customer feedback
              </p>
            </div>
          </div>

          <p className="mt-5 text-sm leading-6 text-slate-600">
            Customers are generally positive about the product, but
            performance and navigation remain the most common concerns.
            Faster search and better personalization are the strongest
            feature opportunities identified from the feedback.
          </p>

          <div className="mt-6 flex items-center gap-2 text-xs font-medium text-blue-600">
            <Sparkles size={14} />
            AI-generated insight
          </div>
        </div>
      </div>

      {/* ================= ISSUES + FEATURE REQUESTS ================= */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* ISSUES TABLE */}
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">
              <AlertCircle size={17} className="text-red-500" />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Issues & Pain Points
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Problems mentioned most frequently by customers
              </p>
            </div>
          </div>

          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[400px] text-left">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="pb-3 text-xs font-medium text-slate-400">
                    Issue
                  </th>

                  <th className="pb-3 text-xs font-medium text-slate-400">
                    Mentions
                  </th>

                  <th className="pb-3 text-xs font-medium text-slate-400">
                    Priority
                  </th>
                </tr>
              </thead>

              <tbody>
                {insights.issues.map((item) => (
                  <tr
                    key={item.issue}
                    className="border-b border-slate-50 last:border-0"
                  >
                    <td className="py-4 text-sm font-medium text-slate-700">
                      {item.issue}
                    </td>

                    <td className="py-4 text-sm text-slate-500">
                      {item.mentions}
                    </td>

                    <td className="py-4">
                      <PriorityBadge priority={item.priority} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* FEATURE REQUESTS TABLE */}
        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50">
              <Lightbulb size={17} className="text-amber-500" />
            </div>

            <div>
              <h2 className="text-sm font-semibold text-slate-900">
                Feature Requests
              </h2>

              <p className="mt-1 text-xs text-slate-500">
                Product improvements requested by customers
              </p>
            </div>
          </div>

          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[400px] text-left">
              <thead>
                <tr className="border-b border-slate-100">
                  <th className="pb-3 text-xs font-medium text-slate-400">
                    Feature
                  </th>

                  <th className="pb-3 text-xs font-medium text-slate-400">
                    Requests
                  </th>

                  <th className="pb-3 text-xs font-medium text-slate-400">
                    Priority
                  </th>
                </tr>
              </thead>

              <tbody>
                {insights.features.map((item) => (
                  <tr
                    key={item.feature}
                    className="border-b border-slate-50 last:border-0"
                  >
                    <td className="py-4 text-sm font-medium text-slate-700">
                      {item.feature}
                    </td>

                    <td className="py-4 text-sm text-slate-500">
                      {item.requests}
                    </td>

                    <td className="py-4">
                      <PriorityBadge priority={item.priority} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ================= COMMON THEMES ================= */}
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <div className="flex items-start justify-between">
          <div>
            <h2 className="text-sm font-semibold text-slate-900">
              Common Themes
            </h2>

            <p className="mt-1 text-xs text-slate-500">
              Recurring topics identified across customer feedback
            </p>
          </div>

          <FileText size={18} className="text-slate-400" />
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
          {insights.themes.map((theme, index) => (
            <div
              key={theme}
              className="border border-slate-200 bg-slate-50 p-4 transition hover:border-blue-200 hover:bg-blue-50"
            >
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                Theme 0{index + 1}
              </p>

              <p className="mt-2 text-sm font-medium text-slate-700">
                {theme}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* ================= PRIORITY OPPORTUNITIES ================= */}
      <div className="rounded-xl border border-slate-200 bg-white p-6">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-blue-600">
            Recommended Actions
          </p>

          <h2 className="mt-1 text-base font-semibold text-slate-900">
            Priority Opportunities
          </h2>

          <p className="mt-1 text-xs text-slate-500">
            Opportunities that can have the strongest product impact
          </p>
        </div>

        <div className="mt-6 space-y-3">
          {insights.opportunities.map((item) => (
            <div
              key={item.number}
              className="flex gap-4 border border-slate-200 p-4 transition hover:border-blue-200"
            >
              <span className="text-xs font-semibold text-slate-400">
                {item.number}
              </span>

              <div className="min-w-0 flex-1">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <h3 className="text-sm font-medium text-slate-800">
                    {item.title}
                  </h3>

                  <PriorityBadge priority={item.priority} />
                </div>

                <p className="mt-1 text-xs leading-5 text-slate-500">
                  {item.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* ================= PLANNING CTA ================= */}
      <div className="flex flex-col gap-4 border border-blue-100 bg-blue-50 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-sm font-semibold text-slate-900">
            Ready to turn insights into requirements?
          </h2>

          <p className="mt-1 text-xs text-slate-600">
            Use these insights to start planning product improvements.
          </p>
        </div>

        <button
          type="button"
          onClick={() => navigate("/planning")}
          className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
        >
          Start Planning
          <ArrowRight size={16} />
        </button>
      </div>
    </div>
  );
}


/* =========================================================
   REUSABLE COMPONENTS
========================================================= */

function MetricCard({
  icon: Icon,
  value,
  title,
  description,
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 transition hover:border-slate-300">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-blue-50">
        <Icon size={17} className="text-blue-600" />
      </div>

      <p className="mt-5 text-2xl font-semibold text-slate-900">
        {value}
      </p>

      <p className="mt-1 text-sm font-medium text-slate-700">
        {title}
      </p>

      <p className="mt-1 text-xs text-slate-400">
        {description}
      </p>
    </div>
  );
}


function SentimentItem({
  icon: Icon,
  label,
  value,
}) {
  return (
    <div>
      <div className="flex items-center gap-1.5 text-xs text-slate-400">
        <Icon size={13} />
        {label}
      </div>

      <p className="mt-1 text-sm font-semibold text-slate-800">
        {value}
      </p>
    </div>
  );
}


function PriorityBadge({ priority }) {
  const styles = {
    High: "bg-red-50 text-red-600",
    Medium: "bg-amber-50 text-amber-600",
    Low: "bg-slate-100 text-slate-600",
  };

  return (
    <span
      className={`inline-flex rounded-md px-2 py-1 text-[10px] font-semibold ${
        styles[priority] || styles.Low
      }`}
    >
      {priority}
    </span>
  );
}


export default Insights;