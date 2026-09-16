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
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";


const EMPTY_INSIGHTS = {
  feedbackAnalyzed: 0,
  issuesIdentified: 0,
  featureRequestsCount: 0,
  themesDetected: 0,

  sentiment: {
    positive: 0,
    neutral: 0,
    negative: 0,
  },

  issues: [],
  features: [],
  themes: [],
  opportunities: [],
};


function getPriority(count, maxCount) {
  if (!maxCount || !count) {
    return "Low";
  }

  const ratio = count / maxCount;

  if (ratio >= 0.67) {
    return "High";
  }

  if (ratio >= 0.34) {
    return "Medium";
  }

  return "Low";
}


function mapDashboardToInsights(dashboard) {
  const themes = dashboard?.themes || [];
  const painPoints = dashboard?.pain_points || [];
  const featureRequests = dashboard?.feature_requests || [];
  const sentiments = dashboard?.sentiments || [];

  const sentimentCounts = {
    positive: 0,
    neutral: 0,
    negative: 0,
  };

  sentiments.forEach((item) => {
    const name = String(item?._id || "").toLowerCase();

    if (name in sentimentCounts) {
      sentimentCounts[name] += Number(item?.count || 0);
    }
  });

  const totalSentiments =
    sentimentCounts.positive +
    sentimentCounts.neutral +
    sentimentCounts.negative;

  const sentimentPercentages =
    totalSentiments > 0
      ? {
          positive: Math.round(
            (sentimentCounts.positive / totalSentiments) * 100
          ),
          neutral: Math.round(
            (sentimentCounts.neutral / totalSentiments) * 100
          ),
          negative: Math.round(
            (sentimentCounts.negative / totalSentiments) * 100
          ),
        }
      : {
          positive: 0,
          neutral: 0,
          negative: 0,
        };

  const maximumPainPointCount = Math.max(
    0,
    ...painPoints.map((item) => Number(item?.count || 0))
  );

  const maximumFeatureCount = Math.max(
    0,
    ...featureRequests.map((item) => Number(item?.count || 0))
  );

  const issues = painPoints.map((item) => {
    const count = Number(item?.count || 0);

    return {
      issue: item?._id || "Unknown issue",
      mentions: count,
      priority: getPriority(count, maximumPainPointCount),
    };
  });

  const features = featureRequests.map((item) => {
    const count = Number(item?.count || 0);

    return {
      feature: item?._id || "Unknown feature request",
      requests: count,
      priority: getPriority(count, maximumFeatureCount),
    };
  });

  const opportunities = features.slice(0, 3).map((item, index) => ({
    number: String(index + 1).padStart(2, "0"),
    title: item.feature,
    description:
      item.requests === 1
        ? "Identified from 1 analyzed customer feedback item."
        : `Identified from ${item.requests} analyzed customer feedback items.`,
    priority: item.priority,
  }));

  return {
    feedbackAnalyzed: Number(dashboard?.total_analyzed || 0),

    issuesIdentified: painPoints.reduce(
      (total, item) => total + Number(item?.count || 0),
      0
    ),

    featureRequestsCount: featureRequests.reduce(
      (total, item) => total + Number(item?.count || 0),
      0
    ),

    themesDetected: themes.length,

    sentiment: sentimentPercentages,

    issues,

    features,

    themes: themes.map((item) => item?._id).filter(Boolean),

    opportunities,
  };
}


function buildSummary(insights) {
  if (insights.feedbackAnalyzed === 0) {
    return (
      "No analyzed feedback is available yet. Once the database is " +
      "connected and feedback is stored, AI-generated themes, pain points, " +
      "and feature opportunities will appear here."
    );
  }

  const parts = [
    `${insights.feedbackAnalyzed} customer feedback item${
      insights.feedbackAnalyzed === 1 ? "" : "s"
    } analyzed.`,
  ];

  if (insights.themes.length > 0) {
    parts.push(`The leading theme is "${insights.themes[0]}".`);
  }

  if (insights.issues.length > 0) {
    parts.push(
      `The most frequently identified pain point is "${insights.issues[0].issue}".`
    );
  }

  if (insights.features.length > 0) {
    parts.push(
      `The strongest feature opportunity currently is "${insights.features[0].feature}".`
    );
  }

  return parts.join(" ");
}


function Insights() {
  const navigate = useNavigate();

  const [insights, setInsights] = useState(EMPTY_INSIGHTS);
  const [databaseStatus, setDatabaseStatus] = useState("loading");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  useEffect(() => {
    const controller = new AbortController();

    async function loadDashboardInsights() {
      try {
        setLoading(true);
        setError("");

        const response = await fetch(
          `${API_BASE_URL}/insights/dashboard`,
          {
            method: "GET",
            headers: {
              Accept: "application/json",
            },
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          throw new Error(
            `Dashboard API returned status ${response.status}`
          );
        }

        const data = await response.json();

        setDatabaseStatus(
          data?.database_status || "unavailable"
        );

        setInsights(
          mapDashboardToInsights(data?.dashboard || {})
        );
      } catch (requestError) {
        if (requestError.name === "AbortError") {
          return;
        }

        console.error(
          "Failed to load product insights:",
          requestError
        );

        setDatabaseStatus("unavailable");
        setInsights(EMPTY_INSIGHTS);
        setError(
          "Unable to load insights from the backend."
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadDashboardInsights();

    return () => {
      controller.abort();
    };
  }, []);


  const aiSummary = buildSummary(insights);


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


        {loading ? (
          <div className="flex w-fit items-center gap-2 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2">
            <Sparkles
              size={16}
              className="text-blue-600"
            />

            <span className="text-xs font-medium text-blue-700">
              Loading analysis...
            </span>
          </div>
        ) : databaseStatus === "connected" ? (
          <div className="flex w-fit items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-3 py-2">
            <CheckCircle2
              size={16}
              className="text-emerald-600"
            />

            <span className="text-xs font-medium text-emerald-700">
              Analysis complete
            </span>
          </div>
        ) : (
          <div className="flex w-fit items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2">
            <AlertCircle
              size={16}
              className="text-amber-600"
            />

            <span className="text-xs font-medium text-amber-700">
              Database unavailable
            </span>
          </div>
        )}
      </div>


      {/* ================= ERROR ================= */}

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-center gap-2">
            <AlertCircle
              size={16}
              className="text-red-500"
            />

            <p className="text-sm text-red-600">
              {error}
            </p>
          </div>
        </div>
      )}


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

            <TrendingUp
              size={18}
              className="text-blue-600"
            />
          </div>


          <div className="mt-6 flex items-end gap-2">
            <span className="text-4xl font-semibold text-slate-900">
              {insights.sentiment.positive}%
            </span>

            <span className="mb-1 text-xs font-medium text-emerald-600">
              Positive
            </span>
          </div>


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
              <Sparkles
                size={17}
                className="text-blue-600"
              />
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
            {aiSummary}
          </p>


          <div className="mt-6 flex items-center gap-2 text-xs font-medium text-blue-600">
            <Sparkles size={14} />
            AI-generated insight
          </div>
        </div>
      </div>


      {/* ================= ISSUES + FEATURES ================= */}

      <div className="grid gap-6 lg:grid-cols-2">

        {/* ISSUES */}

        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-red-50">
              <AlertCircle
                size={17}
                className="text-red-500"
              />
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
                {insights.issues.length > 0 ? (
                  insights.issues.map((item, index) => (
                    <tr
                      key={`${item.issue}-${index}`}
                      className="border-b border-slate-50 last:border-0"
                    >
                      <td className="py-4 text-sm font-medium text-slate-700">
                        {item.issue}
                      </td>

                      <td className="py-4 text-sm text-slate-500">
                        {item.mentions}
                      </td>

                      <td className="py-4">
                        <PriorityBadge
                          priority={item.priority}
                        />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="3"
                      className="py-8 text-center text-sm text-slate-400"
                    >
                      No pain points available yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>


        {/* FEATURES */}

        <div className="rounded-xl border border-slate-200 bg-white p-6">
          <div className="flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-50">
              <Lightbulb
                size={17}
                className="text-amber-500"
              />
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
                {insights.features.length > 0 ? (
                  insights.features.map((item, index) => (
                    <tr
                      key={`${item.feature}-${index}`}
                      className="border-b border-slate-50 last:border-0"
                    >
                      <td className="py-4 text-sm font-medium text-slate-700">
                        {item.feature}
                      </td>

                      <td className="py-4 text-sm text-slate-500">
                        {item.requests}
                      </td>

                      <td className="py-4">
                        <PriorityBadge
                          priority={item.priority}
                        />
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td
                      colSpan="3"
                      className="py-8 text-center text-sm text-slate-400"
                    >
                      No feature requests available yet.
                    </td>
                  </tr>
                )}
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

          <FileText
            size={18}
            className="text-slate-400"
          />
        </div>


        {insights.themes.length > 0 ? (
          <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
            {insights.themes.map((theme, index) => (
              <div
                key={`${theme}-${index}`}
                className="border border-slate-200 bg-slate-50 p-4 transition hover:border-blue-200 hover:bg-blue-50"
              >
                <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">
                  Theme {String(index + 1).padStart(2, "0")}
                </p>

                <p className="mt-2 text-sm font-medium text-slate-700">
                  {theme}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-6 border border-dashed border-slate-200 p-6 text-center">
            <p className="text-sm text-slate-400">
              No themes available yet.
            </p>
          </div>
        )}
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
            Opportunities identified from recurring customer requests
          </p>
        </div>


        {insights.opportunities.length > 0 ? (
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

                    <PriorityBadge
                      priority={item.priority}
                    />
                  </div>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    {item.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-6 border border-dashed border-slate-200 p-6 text-center">
            <p className="text-sm text-slate-400">
              No product opportunities available yet.
            </p>
          </div>
        )}
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
        <Icon
          size={17}
          className="text-blue-600"
        />
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