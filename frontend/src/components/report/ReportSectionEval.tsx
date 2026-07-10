import type { EvalResult } from "@/lib/types";
import { MetricCard, MetricGrid } from "../MetricCard";

export function ReportSectionEval({ evalResult }: { evalResult: EvalResult | null }) {
  if (!evalResult) return null;

  const rows = Object.entries(evalResult.category_breakdown ?? {}).map(([category, v]) => ({
    category,
    ...v,
    successRate: v.total > 0 ? (v.passed / v.total) * 100 : 0,
  }));

  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
        Evaluation &amp; benchmark
      </h2>
      <div className="mt-4">
        <MetricGrid>
          <MetricCard label="Eval pass rate" value={`${evalResult.pass_rate}%`} />
          <MetricCard label="Total tests" value={evalResult.total_tests} />
          <MetricCard label="Successful attacks" value={evalResult.successful_attacks} />
          <MetricCard label="Execution errors" value={evalResult.execution_errors} />
        </MetricGrid>
      </div>

      {rows.length > 0 && (
        <div className="mt-4 overflow-hidden rounded-lg border border-gray-200">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
                <th className="px-4 py-3 font-medium">Category</th>
                <th className="px-4 py-3 font-medium">Total</th>
                <th className="px-4 py-3 font-medium">Passed</th>
                <th className="px-4 py-3 font-medium">Failed</th>
                <th className="px-4 py-3 font-medium">Success rate</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.category} className="border-b border-gray-100 last:border-0">
                  <td className="px-4 py-3 capitalize text-gray-900">
                    {row.category.replace(/_/g, " ")}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{row.total}</td>
                  <td className="px-4 py-3 text-green-600">{row.passed}</td>
                  <td className="px-4 py-3 text-red-600">{row.failed}</td>
                  <td className="px-4 py-3 text-gray-900">{row.successRate.toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {evalResult.note && <p className="mt-3 text-xs italic text-gray-500">{evalResult.note}</p>}
    </section>
  );
}