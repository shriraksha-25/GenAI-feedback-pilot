import { ArrowRight } from "lucide-react";

import { recentFeedback } from "../../data/dummyData";
import Badge from "../common/Badge";

function getBadgeType(value) {
  return value.toLowerCase().replace("/", "");
}

function RecentFeedback() {
  return (
    <div className="rounded-xl border border-gray-200 bg-white">

      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-100 p-6">

        <div>
          <h3 className="text-base font-semibold text-gray-900">
            Recent Customer Feedback
          </h3>

          <p className="mt-1 text-sm text-gray-500">
            Latest feedback analyzed by the system.
          </p>
        </div>

        <button className="flex items-center gap-1 text-sm font-medium text-gray-600 transition hover:text-gray-900">
          View all
          <ArrowRight size={15} />
        </button>

      </div>

      {/* Table */}
      <div className="overflow-x-auto">

        <table className="w-full text-left">

          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">

              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Customer
              </th>

              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Feedback
              </th>

              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Sentiment
              </th>

              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Category
              </th>

              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Priority
              </th>

              <th className="px-6 py-3 text-xs font-semibold uppercase tracking-wide text-gray-400">
                Date
              </th>

            </tr>
          </thead>

          <tbody>
            {recentFeedback.map((item) => (

              <tr
                key={item.id}
                className="border-b border-gray-100 last:border-0 hover:bg-gray-50"
              >

                <td className="whitespace-nowrap px-6 py-4">
                  <span className="text-sm font-medium text-gray-900">
                    {item.customer}
                  </span>
                </td>

                <td className="max-w-sm px-6 py-4">
                  <p className="truncate text-sm text-gray-600">
                    {item.feedback}
                  </p>
                </td>

                <td className="whitespace-nowrap px-6 py-4">
                  <Badge
                    type={
                      item.sentiment === "Positive"
                        ? "positive"
                        : item.sentiment === "Negative"
                        ? "negative"
                        : "neutral"
                    }
                  >
                    {item.sentiment}
                  </Badge>
                </td>

                <td className="whitespace-nowrap px-6 py-4">
                  <span className="text-sm text-gray-600">
                    {item.category}
                  </span>
                </td>

                <td className="whitespace-nowrap px-6 py-4">
                  <Badge type={item.priority.toLowerCase()}>
                    {item.priority}
                  </Badge>
                </td>

                <td className="whitespace-nowrap px-6 py-4 text-sm text-gray-500">
                  {item.date}
                </td>

              </tr>

            ))}
          </tbody>

        </table>

      </div>
    </div>
  );
}

export default RecentFeedback;