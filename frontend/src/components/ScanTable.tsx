import Link from "next/link";
import type { ScanRun } from "@/lib/types";
import { RiskBadge } from "./badges/RiskBadge";

function formatDate(iso: string) {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function ScanTable({ scans }: { scans: ScanRun[] }) {
  if (scans.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 px-6 py-10 text-center text-sm text-gray-500">
        No scans yet. Run a scan on this agent to see results here.
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-200">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
            <th className="px-4 py-3 font-medium">Scan ID</th>
            <th className="px-4 py-3 font-medium">Run date</th>
            <th className="px-4 py-3 font-medium">Risk</th>
            <th className="px-4 py-3 font-medium">Score</th>
            <th className="px-4 py-3 font-medium">Dynamic</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3" />
          </tr>
        </thead>
        <tbody>
          {scans.map((scan) => (
            <tr key={scan.id} className="border-b border-gray-100 last:border-0 hover:bg-gray-50">
              <td className="px-4 py-3 text-xs text-gray-900">{scan.id}</td>
              <td className="px-4 py-3 text-gray-500">{formatDate(scan.generated_at)}</td>
              <td className="px-4 py-3">
                <RiskBadge level={scan.risk_level} />
              </td>
              <td className="px-4 py-3 text-gray-900">{scan.security_score}</td>
              <td className="px-4 py-3 text-gray-500">
                {scan.dynamic_testing_performed ? "Yes" : "No"}
              </td>
              <td className="px-4 py-3 text-gray-500">{scan.status}</td>
              <td className="px-4 py-3 text-right">
                <Link href={`/reports/${scan.id}`} className="text-indigo-600 hover:underline">
                  View report →
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}