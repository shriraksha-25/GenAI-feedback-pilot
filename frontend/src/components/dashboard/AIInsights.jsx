import { ArrowRight, Sparkles } from "lucide-react";

import { aiInsights } from "../../data/dummyData";
import Badge from "../common/Badge";

function AIInsights() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 p-6">

        <div className="flex items-center gap-3">

          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gray-900 text-white">
            <Sparkles size={17} />
          </div>

          <div>
            <h3 className="text-base font-semibold text-gray-900">
              AI Product Insights
            </h3>

            <p className="mt-1 text-sm text-gray-500">
              Recommendations generated from customer feedback.
            </p>
          </div>

        </div>

        <button className="flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-gray-900">
          View insights
          <ArrowRight size={15} />
        </button>

      </div>

      {/* Insights */}
      <div className="divide-y divide-gray-100">

        {aiInsights.map((insight, index) => (

          <div
            key={insight.id}
            className="flex gap-5 p-6 transition hover:bg-gray-50"
          >

            {/* Number */}
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gray-100 text-xs font-semibold text-gray-500">
              {String(index + 1).padStart(2, "0")}
            </div>

            {/* Content */}
            <div className="min-w-0 flex-1">

              <div className="flex flex-wrap items-center gap-2">

                <h4 className="text-sm font-semibold text-gray-900">
                  {insight.title}
                </h4>

                <Badge type="high">
                  {insight.impact}
                </Badge>

              </div>

              <p className="mt-2 max-w-3xl text-sm leading-6 text-gray-500">
                {insight.description}
              </p>

              <p className="mt-2 text-xs font-medium text-gray-400">
                Category: {insight.category}
              </p>

            </div>

          </div>

        ))}

      </div>
    </div>
  );
}

export default AIInsights;