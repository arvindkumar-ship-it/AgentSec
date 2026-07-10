import { notFound } from "next/navigation";
import { getScanReport, ApiError } from "@/lib/api/reportApi";
import { getEvalForScan } from "@/lib/api/evalApi";
import { ReportHeader } from "@/components/report/ReportHeader";
import { ReportSectionExecutive } from "@/components/report/ReportSectionExecutive";
import { ReportSectionStatistics } from "@/components/report/ReportSectionStatistics";
import { ReportSectionEval } from "@/components/report/ReportSectionEval";
import { ReportSectionStaticFindings } from "@/components/report/ReportSectionStaticFindings";
import { ReportSectionDynamicAttacks } from "@/components/report/ReportSectionDynamicAttacks";
import { ReportSectionTopFixes } from "@/components/report/ReportSectionTopFixes";
import { ReportSectionRawResults } from "@/components/report/ReportSectionRawResults";

export default async function ReportPage({ params }: { params: { scanId: string } }) {
  let scanReport;
  try {
    scanReport = await getScanReport(params.scanId);
  } catch (err) {
    if (err instanceof ApiError && err.status === 404) notFound();
    throw err;
  }

  const report = scanReport.report;
  const evalResult = await getEvalForScan(report.agent_id, report.scan_id);

  return (
    <main className="mx-auto max-w-5xl px-6 py-10">
      <ReportHeader report={report} />
      <div className="mt-10 space-y-12">
        <ReportSectionExecutive report={report} />
        <ReportSectionStatistics report={report} />
        <ReportSectionEval evalResult={evalResult} />
        <ReportSectionStaticFindings findings={report.static_findings} />
        <ReportSectionDynamicAttacks
          successful={report.successful_attacks}
          needsReview={report.needs_review_attacks}
        />
        <ReportSectionTopFixes fixes={report.top_fixes} />
        <ReportSectionRawResults results={report.raw_results} />
      </div>
    </main>
  );
}