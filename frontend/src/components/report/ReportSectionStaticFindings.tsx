import type { StaticFinding } from "@/lib/types";
import { SeverityBadge } from "../badges/SeverityBadge";

export function ReportSectionStaticFindings({ findings }: { findings: StaticFinding[] }) {
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
        Static guardrail findings
      </h2>
      <div className="mt-4 overflow-hidden rounded-lg border border-gray-200">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
              <th className="px-4 py-3 font-medium">Finding</th>
              <th className="px-4 py-3 font-medium">Type</th>
              <th className="px-4 py-3 font-medium">Severity</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">Recommended fix</th>
            </tr>
          </thead>
          <tbody>
            {findings.map((f, idx) => (
              <tr key={idx} className="border-b border-gray-100 last:border-0 align-top">
                <td className="px-4 py-3 text-gray-900">{f.name}</td>
                <td className="px-4 py-3 text-xs text-gray-500">{f.type}</td>
                <td className="px-4 py-3">
                  <SeverityBadge severity={f.severity} />
                </td>
                <td className="px-4 py-3 text-gray-500">{f.confidence}</td>
                <td className="px-4 py-3 max-w-md text-gray-500">{f.fix}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}