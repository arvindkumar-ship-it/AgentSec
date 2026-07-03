"use client";
import { useState, useEffect } from "react";
import { Shield, ChevronLeft, RotateCcw, CheckCircle, XCircle, AlertCircle } from "lucide-react";
import agentSecAPI from "@/lib/api";
import Link from "next/link";

function EventBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    SUCCESS: "text-green-400 bg-green-500/10 border-green-500/30",
    BLOCKED: "text-red-400 bg-red-500/10 border-red-500/30",
    POLICY_VIOLATION: "text-orange-400 bg-orange-500/10 border-orange-500/30",
    OUTBOUND_WARN: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30",
    OUTBOUND_BLOCK: "text-red-400 bg-red-500/10 border-red-500/30",
    TOOL_ERROR: "text-gray-400 bg-gray-500/10 border-gray-500/30",
  };
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full border font-mono ${colors[type] || "text-gray-400 bg-gray-500/10 border-gray-500/30"}`}>
      {type}
    </span>
  );
}

export default function ShieldPage() {
  const [agentId, setAgentId] = useState("my-agent-001");
  const [logs, setLogs] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [checkpoints, setCheckpoints] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [hours, setHours] = useState(24);
  const [policy, setPolicy] = useState(`{
  "blocked_tools": [],
  "allowed_tools": [],
  "require_human_confirmation": ["send_email", "delete_record"],
  "max_cost_per_session_usd": 5.0,
  "max_iterations": 50
}`);

  const load = async () => {
    setLoading(true);
    try {
      const [logsR, statsR, cpR] = await Promise.all([
        agentSecAPI.getShieldLogs(agentId, hours),
        agentSecAPI.getShieldStats(agentId),
        agentSecAPI.getCheckpoints(agentId),
      ]);
      setLogs(logsR.data.logs || []);
      setStats(statsR.data);
      setCheckpoints(cpR.data.checkpoints || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [agentId, hours]);

  const registerShield = async () => {
    try {
      const parsed = JSON.parse(policy);
      const r = await agentSecAPI.registerShield({ agent_id: agentId, agent_name: agentId, policy: parsed });
      alert("Shield registered! See console for SDK usage.");
      console.log(r.data.sdk_usage.python);
    } catch (e: any) {
      alert("Error: " + e.message);
    }
  };

  const revertCheckpoint = async (cpId: string) => {
    if (!confirm("Revert to this checkpoint?")) return;
    try {
      const r = await agentSecAPI.revertCheckpoint(agentId, cpId);
      alert(r.data.message);
      load();
    } catch (e: any) {
      alert("Error: " + e.message);
    }
  };

  return (
    <div className="min-h-screen bg-surface">
      <nav className="border-b border-border bg-panel px-8 py-4 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-white transition-colors"><ChevronLeft size={20} /></Link>
        <Shield className="text-green-400" size={20} />
        <span className="font-semibold">Agent Shield</span>
        <span className="text-xs text-gray-500">— Runtime protection & audit</span>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-8">
        {/* ── Controls ── */}
        <div className="flex gap-3 mb-6">
          <input
            value={agentId}
            onChange={e => setAgentId(e.target.value)}
            placeholder="Agent ID"
            className="bg-panel border border-border rounded-lg px-4 py-2 text-sm font-mono focus:outline-none focus:border-accent w-64"
          />
          <select
            value={hours}
            onChange={e => setHours(Number(e.target.value))}
            className="bg-panel border border-border rounded-lg px-3 py-2 text-sm text-gray-400 focus:outline-none focus:border-accent"
          >
            <option value={1}>Last 1h</option>
            <option value={6}>Last 6h</option>
            <option value={24}>Last 24h</option>
            <option value={168}>Last 7d</option>
          </select>
          <button onClick={load} className="bg-panel border border-border hover:border-accent px-4 py-2 rounded-lg text-sm transition-colors">Refresh</button>
        </div>

        <div className="grid grid-cols-3 gap-6">
          {/* ── Left: Stats + Register ── */}
          <div className="space-y-5">
            {stats && (
              <div className="bg-panel border border-border rounded-xl p-5">
                <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-4">Shield Activity ({hours}h)</h3>
                <div className="space-y-3">
                  {[
                    { label: "Allowed", val: stats.total_allowed, color: "text-green-400" },
                    { label: "Blocked", val: stats.total_blocked, color: "text-red-400" },
                    ...Object.entries(stats.events || {}).map(([k, v]) => ({ label: k, val: v, color: "text-gray-400" }))
                  ].slice(0, 6).map(({ label, val, color }) => (
                    <div key={label} className="flex items-center justify-between">
                      <span className="text-sm text-gray-400">{label}</span>
                      <span className={`font-mono font-bold ${color}`}>{String(val)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="bg-panel border border-border rounded-xl p-5">
              <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-3">Register Shield</h3>
              <textarea
                value={policy}
                onChange={e => setPolicy(e.target.value)}
                rows={8}
                className="w-full bg-surface border border-border rounded-lg px-3 py-2.5 text-xs font-mono focus:outline-none focus:border-accent resize-none mb-3"
              />
              <button
                onClick={registerShield}
                className="w-full bg-green-600 hover:bg-green-700 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Register + Get SDK Code
              </button>
            </div>
          </div>

          {/* ── Center: Logs ── */}
          <div className="col-span-1">
            <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-3">Audit Logs ({logs.length})</h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {loading && <div className="text-center py-10 text-gray-600 text-sm">Loading...</div>}
              {!loading && logs.length === 0 && (
                <div className="text-center py-10 text-gray-600 text-sm">
                  No logs yet. Register your agent and run it.
                </div>
              )}
              {logs.map((log, i) => (
                <div key={i} className="bg-panel border border-border rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <EventBadge type={log.event_type} />
                    <span className="text-xs font-mono text-gray-400">{log.tool_name}</span>
                    <span className="text-xs text-gray-600 ml-auto">{new Date(log.timestamp).toLocaleTimeString()}</span>
                  </div>
                  {log.error && <p className="text-xs text-red-400 mt-1">{log.error}</p>}
                  {log.action && <p className="text-xs text-gray-500 font-mono truncate mt-1">{log.action}</p>}
                </div>
              ))}
            </div>
          </div>

          {/* ── Right: Checkpoints ── */}
          <div>
            <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-3">Checkpoints — Undo</h3>
            <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
              {checkpoints.length === 0 && (
                <div className="text-center py-10 text-gray-600 text-sm">
                  No checkpoints yet. Checkpoints are created before each tool call.
                </div>
              )}
              {checkpoints.map((cp, i) => (
                <div key={i} className={`bg-panel border rounded-lg p-3 ${cp.reverted ? "border-gray-700 opacity-50" : "border-border"}`}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-mono text-gray-400">{cp.tool_name}</span>
                    {!cp.reverted && (
                      <button
                        onClick={() => revertCheckpoint(cp.checkpoint_id)}
                        className="flex items-center gap-1 text-xs text-orange-400 hover:text-orange-300 transition-colors"
                      >
                        <RotateCcw size={12} /> Revert
                      </button>
                    )}
                    {cp.reverted && <span className="text-xs text-gray-600">Reverted</span>}
                  </div>
                  <p className="text-xs text-gray-600 font-mono">{cp.checkpoint_id.slice(0, 16)}...</p>
                  <p className="text-xs text-gray-600 mt-1">{new Date(cp.created_at).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
