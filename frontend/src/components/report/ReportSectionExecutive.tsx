import type { ScanReport } from "@/lib/types";

export function ReportSectionExecutive({ report }: { report: ScanReport }) {
  const s = report.statistics;
  const bullets = [
    `${s.successful_attacks} of ${s.total_attacks} attacks succeeded (${s.critical_count} critical).`,
    `${s.needs_review_attacks} verdicts flagged for manual review.`,
    `${s.static_findings} static guardrail gaps found in the system prompt.`,
  ];

  return (
    <section className="border-l-2 border-indigo-300 pl-5">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
        Executive summary
      </h2>
      <p className="mt-3 max-w-3xl text-sm leading-relaxed text-gray-600">
        {report.executive_summary}
      </p>
      <ul className="mt-4 space-y-1.5 text-sm text-gray-800">
        {bullets.map((b) => (
          <li key={b} className="flex gap-2">
            <span className="text-indigo-500">›</span>
            {b}
          </li>
        ))}
      </ul>
    </section>
  );
}