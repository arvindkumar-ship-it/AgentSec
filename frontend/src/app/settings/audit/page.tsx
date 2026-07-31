"use client";
import { useEffect, useState } from "react";
import RouteGuard from "@/components/RouteGuard";
import Navbar from "@/components/Navbar";
import { agentSecAPI } from "@/lib/api";

export default function AuditPage() {
  const [logs, setLogs] = useState<any[]>([]);
  useEffect(() => { agentSecAPI.getAuditLogs().then((r) => setLogs(r.data)); }, []);

  const exportCSV = async () => {
    const res = await agentSecAPI.exportAuditLogs();
    const url = URL.createObjectURL(new Blob([res.data]));
    const a = document.createElement("a");
    a.href = url; a.download = "audit_logs.csv"; a.click();
  };

  return (
    <RouteGuard adminOnly>
      <Navbar />
      <div className="p-6 max-w-6xl mx-auto text-gray-900">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Audit Logs</h1>
          <button onClick={exportCSV} className="bg-accent text-white px-4 py-2 rounded-full text-sm">Export CSV</button>
        </div>
        <div className="bg-panel border border-border rounded-2xl overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="text-left text-muted border-b border-border"><th className="p-3">Time</th><th className="p-3">Action</th><th className="p-3">Target</th></tr></thead>
            <tbody>
              {logs.map((l) => (
                <tr key={l.id} className="border-t border-border">
                  <td className="p-3">{new Date(l.created_at).toLocaleString()}</td>
                  <td className="p-3">{l.action}</td>
                  <td className="p-3">{l.target_id || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </RouteGuard>
  );
}