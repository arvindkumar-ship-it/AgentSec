"use client";
import { useEffect, useState } from "react";
import { agentSecAPI } from "@/lib/api";

export default function UsageCard() {
  const [usage, setUsage] = useState<any>(null);

  useEffect(() => {
    agentSecAPI.getUsage().then((res) => setUsage(res.data)).catch(() => {});
  }, []);

  if (!usage) return null;

  return (
    <div className="bg-panel border border-border rounded-2xl p-4 space-y-2 mb-4">
      <h3 className="font-semibold text-sm text-muted">Today's Usage</h3>
      <div className="flex justify-between text-sm text-gray-900">
        <span>Scans</span><span>{usage.scans.used} / {usage.scans.limit}</span>
      </div>
      <div className="flex justify-between text-sm text-gray-900">
        <span>Evals</span><span>{usage.evals.used} / {usage.evals.limit}</span>
      </div>
      <div className="flex justify-between text-sm text-gray-900">
        <span>Storage</span><span>{usage.storage_mb.used} / {usage.storage_mb.limit} MB</span>
      </div>
    </div>
  );
}