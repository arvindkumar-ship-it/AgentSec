import type { ScanReport } from "@/lib/types";
import { RiskBadge } from "../badges/RiskBadge";
import { ScoreGauge } from "../ScoreGauge";
import { getReportDownloadUrl } from "@/lib/api/reportApi";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, { dateStyle: "long", timeStyle: "short" });
}

export function ReportHeader({ report }: { report: ScanReport }) {
  return (
    <header className="flex flex-col gap-6 border-b border-gray-200 pb-8 md:flex-row md:items-center md:justify-between">
      <div>
        <div className="mb-2 text-xs uppercase tracking-widest text-gray-400">
          AgentSec / Security Scan Report
        </div>
        <h1 className="text-2xl font-semibold text-gray-900 md:text-3xl">
          {report.agent_name}
        </h1>
        <dl className="mt-3 flex flex-wrap gap-x-6 gap-y-1 text-xs text-gray-500">
          <div>
            <dt className="inline text-gray-400">agent_id </dt>
            <dd className="inline text-gray-700">{report.agent_id}</dd>
          </div>
          <div>
            <dt className="inline text-gray-400">scan_id </dt>
            <dd className="inline text-gray-700">{report.scan_id}</dd>
          </div>
          <div>
            <dt className="inline text-gray-400">type </dt>
            <dd className="inline text-gray-700">{report.scan_type}</dd>
          </div>
          <div>
            <dt className="inline text-gray-400">generated </dt>
            <dd className="inline text-gray-700">{formatDate(report.generated_at)}</dd>
          </div>
        </dl>
        <div className="mt-4">
            <a
              href={getReportDownloadUrl(report.scan_id)}
              className="inline-flex items-center gap-2 rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 transition hover:border-indigo-400 hover:text-indigo-600"
            >
              Download PDF
            </a>
      </div>
      </div>
      <div className="flex items-center gap-6">
        <ScoreGauge score={report.security_score} />
        <RiskBadge level={report.risk_level} />
      </div>
    </header>
  );
}