"use client";

import { useState } from "react";
import type { Attack } from "@/lib/types";
import { SeverityBadge } from "../badges/SeverityBadge";

function truncate(text: string, max: number) {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

export function AttackRow({ attack }: { attack: Attack }) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <tr
        onClick={() => setOpen((o) => !o)}
        className="cursor-pointer border-b border-gray-100 last:border-0 hover:bg-gray-50"
      >
        <td className="px-4 py-3 text-gray-900">{attack.category.replace(/_/g, " ")}</td>
        <td className="px-4 py-3">
          <SeverityBadge severity={attack.severity} />
        </td>
        <td className="px-4 py-3 text-xs text-gray-500">{truncate(attack.payload, 70)}</td>
        <td className="px-4 py-3">
          <span className={attack.verdict.success ? "text-red-600" : "text-green-600"}>
            {attack.verdict.success ? "Success" : "Blocked"}
          </span>
        </td>
        <td className="px-4 py-3 text-gray-500">{attack.verdict.confidence}%</td>
        <td className="px-4 py-3 text-gray-500">
          {attack.verdict.needs_review ? "Needs review" : "—"}
        </td>
      </tr>
      {open && (
        <tr className="border-b border-gray-100 bg-gray-50 last:border-0">
          <td colSpan={6} className="px-4 py-4">
            <div className="mb-3">
              <div className="mb-1 text-xs uppercase tracking-wide text-gray-500">Payload</div>
              <pre className="whitespace-pre-wrap break-words rounded-md bg-white border border-gray-200 p-3 text-xs text-gray-900">
                {attack.payload}
              </pre>
            </div>
            <div className="grid gap-3 text-sm sm:grid-cols-2">
              <div>
                <span className="text-gray-500">Reason: </span>
                <span className="text-gray-900">{attack.verdict.reason}</span>
              </div>
              <div>
                <span className="text-gray-500">Judge agreement: </span>
                <span className="text-gray-900">{attack.verdict.agreement}</span>
              </div>
              {attack.verdict.extracted_info && (
                <div className="sm:col-span-2">
                  <span className="text-gray-500">Extracted info: </span>
                  <span className="text-red-600">{attack.verdict.extracted_info}</span>
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
}