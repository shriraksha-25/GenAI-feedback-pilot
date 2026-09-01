import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { sentimentData } from "../../data/dummyData";

const COLORS = ["#111827", "#9CA3AF", "#D1D5DB"];

function SentimentOverview() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6">

      <div>
        <h3 className="text-base font-semibold text-gray-900">
          Sentiment Distribution
        </h3>

        <p className="mt-1 text-sm text-gray-500">
          Overall sentiment from analyzed feedback.
        </p>
      </div>

      <div className="mt-4 h-56">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>

            <Pie
              data={sentimentData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {sentimentData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>

            <Tooltip />

          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="space-y-3">
        {sentimentData.map((item, index) => (
          <div
            key={item.name}
            className="flex items-center justify-between"
          >
            <div className="flex items-center gap-2">

              <span
                className="h-2.5 w-2.5 rounded-full"
                style={{
                  backgroundColor: COLORS[index],
                }}
              />

              <span className="text-sm text-gray-600">
                {item.name}
              </span>
            </div>

            <span className="text-sm font-semibold text-gray-900">
              {item.value}%
            </span>
          </div>
        ))}
      </div>

    </div>
  );
}

export default SentimentOverview;