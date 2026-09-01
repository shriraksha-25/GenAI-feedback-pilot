function Badge({ children, type = "default" }) {
  const styles = {
    default: "bg-gray-100 text-gray-600",

    positive: "bg-green-50 text-green-700",

    negative: "bg-red-50 text-red-700",

    neutral: "bg-gray-100 text-gray-600",

    high: "bg-red-50 text-red-700",

    medium: "bg-amber-50 text-amber-700",

    low: "bg-green-50 text-green-700",
  };

  return (
    <span
      className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${
        styles[type] || styles.default
      }`}
    >
      {children}
    </span>
  );
}

export default Badge;