import type { TopFix } from "@/lib/types";

export function ReportSectionTopFixes({ fixes }: { fixes: TopFix[] }) {
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
        Top remediation actions
      </h2>
      <ol className="mt-4 space-y-3">
        {fixes.map((fx) => (
          <li key={fx.priority} className="flex gap-4 rounded-lg border border-gray-200 bg-white p-4">
            <span className="text-lg font-semibold text-indigo-500">
              {String(fx.priority).padStart(2, "0")}
            </span>
            <div className="min-w-0">
              <div className="font-medium text-gray-900">{fx.issue}</div>
              <p className="mt-1 text-sm text-gray-500">{fx.fix}</p>
              {fx.example && (
                <pre className="mt-2 whitespace-pre-wrap break-words rounded bg-gray-50 border border-gray-100 p-2 text-xs text-gray-500">
                  {fx.example}
                </pre>
              )}
            </div>
          </li>
        ))}
      </ol>
    </section>
  );
}