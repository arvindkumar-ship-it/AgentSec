import type { ScanReport } from "@/lib/types";
import { MetricCard, MetricGrid } from "../MetricCard";

export function ReportSectionStatistics({ report }: { report: ScanReport }) {
  const s = report.statistics;
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
        Security statistics
      </h2>
      <div className="mt-4">
        <MetricGrid>
          <MetricCard label="Total attacks" value={s.total_attacks} />
          <MetricCard label="Successful" value={s.successful_attacks} tone="critical" />
          <MetricCard label="Failed" value={s.failed_attacks} />
          <MetricCard label="Needs review" value={s.needs_review_attacks} />
          <MetricCard label="Pass rate" value={s.pass_rate} />
          <MetricCard label="Static findings" value={s.static_findings} />
          <MetricCard label="Critical count" value={s.critical_count} tone="critical" />
        </MetricGrid>
      </div>
      <p className="mt-3 text-xs text-gray-500">
        {s.total_attacks_including_multiturn} total attacks including multi-turn chains ·{" "}
        {s.total_successful_including_multiturn} successful including multi-turn.
      </p>
    </section>
  );
}