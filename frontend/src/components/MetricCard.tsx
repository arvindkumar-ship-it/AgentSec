export function MetricCard({
  label,
  value,
  tone = "default",
}: {
  label: string;
  value: string | number;
  tone?: "default" | "critical";
}) {
  return (
    <div className="min-w-[140px] flex-1 rounded-lg border border-gray-200 bg-white px-5 py-4 shadow-sm">
      <div
        className={`text-2xl font-semibold ${tone === "critical" ? "text-red-600" : "text-gray-900"}`}
      >
        {value}
      </div>
      <div className="mt-1 text-xs uppercase tracking-wide text-gray-500">{label}</div>
    </div>
  );
}

export function MetricGrid({ children }: { children: React.ReactNode }) {
  return <div className="flex flex-wrap gap-3">{children}</div>;
}