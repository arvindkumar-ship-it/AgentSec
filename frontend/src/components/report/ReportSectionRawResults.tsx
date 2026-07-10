"use client";

import { useState } from "react";
import type { RawResult } from "@/lib/types";
import { SeverityBadge } from "../badges/SeverityBadge";

function RawResultCard({ result }: { result: RawResult }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="rounded-lg border border-gray-200 bg-white">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left"
      >
        <div className="flex min-w-0 items-center gap-3">
          <SeverityBadge severity={result.severity} />
          <span className="truncate text-sm text-gray-900">{result.description}</span>
        </div>
        <span className="shrink-0 text-xs text-gray-400">{open ? "−" : "+"}</span>
      </button>
      {open && (
        <div className="space-y-3 border-t border-gray-100 px-4 py-4 text-sm">
          <div>
            <div className="mb-1 text-xs uppercase tracking-wide text-gray-500">Payload</div>
            <pre className="whitespace-pre-wrap break-words rounded bg-gray-50 border border-gray-100 p-3 text-xs text-gray-900">
              {result.payload}
            </pre>
          </div>
          <div>
            <div className="mb-1 text-xs uppercase tracking-wide text-gray-500">Agent response</div>
            <pre className="whitespace-pre-wrap break-words rounded bg-gray-50 border border-gray-100 p-3 text-xs text-gray-900">
              {result.agent_response}
            </pre>
          </div>
          <div className="text-gray-500">
            <span className="text-gray-900">{result.verdict.success ? "Success" : "Blocked"}</span>
            {" · confidence "}
            <span>{result.verdict.confidence}%</span>
            {" · "}
            {result.verdict.reason}
          </div>
        </div>
      )}
    </div>
  );
}

export function ReportSectionRawResults({ results }: { results: RawResult[] }) {
  return (
    <section>
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-900">
        Raw attack results
        <span className="ml-2 text-gray-400">({results.length})</span>
      </h2>
      <div className="mt-4 space-y-2">
        {results.map((r, idx) => (
          <RawResultCard key={idx} result={r} />
        ))}
      </div>
    </section>
  );
}