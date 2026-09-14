import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

import { feedbackTrendData } from "../../data/dummyData";

function FeedbackOverview() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">

      <div className="mb-6">
        <h3 className="text-base font-semibold text-gray-900">
          Feedback Trends
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Customer feedback received over the last 8 months.
        </p>
      </div>

      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={feedbackTrendData}>
            
            <defs>
              <linearGradient
                id="feedbackGradient"
                x1="0"
                y1="0"
                x2="0"
                y2="1"
              >
                <stop
                  offset="5%"
                  stopColor="#111827"
                  stopOpacity={0.15}
                />

                <stop
                  offset="95%"
                  stopColor="#111827"
                  stopOpacity={0}
                />
              </linearGradient>
            </defs>

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
              stroke="#E5E7EB"
            />

            <XAxis
              dataKey="month"
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#9CA3AF", fontSize: 12 }}
            />

            <YAxis
              axisLine={false}
              tickLine={false}
              tick={{ fill: "#9CA3AF", fontSize: 12 }}
            />

            <Tooltip />

            <Area
              type="monotone"
              dataKey="feedback"
              stroke="#111827"
              strokeWidth={2}
              fill="url(#feedbackGradient)"
            />

          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default FeedbackOverview;