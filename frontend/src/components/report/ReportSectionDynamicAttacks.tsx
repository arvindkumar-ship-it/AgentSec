"use client";

import { useMemo, useState } from "react";
import type { Attack, Severity } from "@/lib/types";
import { AttackRow } from "./AttackRow";

const SEVERITIES: Severity[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export function ReportSectionDynamicAttacks({
  successful,
  needsReview,
}: {
  successful: Attack[];
  needsReview: Attack[];
}) {
  const [tab, setTab] = useState<"successful" | "review">("successful");
  const [severityFilter, setSeverityFilter] = useState<Severity | "ALL">("ALL");

  const active = tab === "successful" ? successful : needsReview;
  const filtered = useMemo(
    () => (severityFilter === "ALL" ? active : active.filter((a) => a.severity === severityFilter)),
    [active, severityFilter]
  );

  return (
    <section>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
          Dynamic attacks
        </h2>
        <div className="flex items-center gap-1 rounded-md border border-gray-200 p-1">
          {SEVERITIES.concat("ALL" as Severity).map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev as Severity | "ALL")}
              className={`rounded px-2.5 py-1 text-[11px] uppercase tracking-wide transition ${
                severityFilter === sev
                  ? "bg-gray-100 text-gray-900"
                  : "text-gray-500 hover:text-gray-900"
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 flex gap-6 border-b border-gray-200 text-sm">
        <button
          onClick={() => setTab("successful")}
          className={`-mb-px border-b-2 pb-2 ${
            tab === "successful"
              ? "border-red-500 text-gray-900"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Confirmed successful ({successful.length})
        </button>
        <button
          onClick={() => setTab("review")}
          className={`-mb-px border-b-2 pb-2 ${
            tab === "review"
              ? "border-indigo-500 text-gray-900"
              : "border-transparent text-gray-500 hover:text-gray-900"
          }`}
        >
          Needs manual review ({needsReview.length})
        </button>
      </div>

      <div className="mt-4 overflow-hidden rounded-lg border border-gray-200">
        {filtered.length === 0 ? (
          <div className="px-6 py-10 text-center text-sm text-gray-500">
            No attacks match this filter.
          </div>
        ) : (
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50 text-left text-xs uppercase tracking-wide text-gray-500">
                <th className="px-4 py-3 font-medium">Category</th>
                <th className="px-4 py-3 font-medium">Severity</th>
                <th className="px-4 py-3 font-medium">Payload</th>
                <th className="px-4 py-3 font-medium">Verdict</th>
                <th className="px-4 py-3 font-medium">Confidence</th>
                <th className="px-4 py-3 font-medium">Review</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((attack, idx) => (
                <AttackRow key={idx} attack={attack} />
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}