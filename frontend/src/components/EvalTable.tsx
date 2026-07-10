import type { EvalResult } from "@/lib/types";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}

export function EvalTable({ evals }: { evals: EvalResult[] }) {
  if (evals.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 px-6 py-10 text-center text-sm text-gray-500">
        No evaluation runs yet.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <th className="px-4 py-3 font-medium">Run at</th>
            <th className="px-4 py-3 font-medium">Pass rate</th>
            <th className="px-4 py-3 font-medium">Total tests</th>
            <th className="px-4 py-3 font-medium">Execution errors</th>
            <th className="px-4 py-3 font-medium">Note</th>
          </tr>
        </thead>
        <tbody>
          {evals.map((ev, idx) => (
            <tr key={ev.eval_id ?? idx} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <td className="px-4 py-3 text-gray-500">{formatDate(ev.run_at)}</td>
              <td className="px-4 py-3 text-gray-900">{ev.pass_rate}%</td>
              <td className="px-4 py-3 text-gray-900">{ev.total_tests}</td>
              <td className="px-4 py-3 text-gray-900">{ev.execution_errors}</td>
              <td className="px-4 py-3 max-w-xs truncate text-gray-500">{ev.note ?? "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}