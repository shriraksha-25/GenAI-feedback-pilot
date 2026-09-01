import { ArrowDown, ArrowUp } from "lucide-react";

function StatCard({
  title,
  value,
  change,
  changeType,
  description,
}) {
  const isPositive = changeType === "positive";

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-5 transition hover:border-gray-300 hover:shadow-sm">

      <p className="text-sm font-medium text-gray-500">
        {title}
      </p>

      <div className="mt-3 flex items-end justify-between">
        <h3 className="text-2xl font-bold tracking-tight text-gray-900">
          {value}
        </h3>

        <div
          className={`flex items-center gap-1 text-xs font-semibold ${
            isPositive ? "text-green-600" : "text-red-600"
          }`}
        >
          {isPositive ? (
            <ArrowUp size={14} />
          ) : (
            <ArrowDown size={14} />
          )}

          {change}
        </div>
      </div>

      <p className="mt-2 text-xs text-gray-400">
        {description}
      </p>
    </div>
  );
}

export default StatCard;