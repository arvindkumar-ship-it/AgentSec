"use client";
import { useState, useEffect } from "react";
import { Activity, ChevronLeft, AlertTriangle, CheckCircle } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";
import agentSecAPI from "@/lib/api";
import Link from "next/link";

const CATEGORIES = [
  "prompt_injection", "jailbreak", "data_exfiltration",
  "excessive_agency", "auth_bypass", "memory_poisoning"
];

export default function EvalPage() {
  const [form, setForm] = useState({
    agent_id: "my-agent-001",
    agent_name: "",
    endpoint_url: "",
    auth_header: "",
    categories: [] as string[],
    consistency_checks: 3,
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [trend, setTrend] = useState<any[]>([]);
  const [regression, setRegression] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);

  const loadData = async () => {
    try {
      const [trendR, regR, histR] = await Promise.all([
        agentSecAPI.getEvalTrend(form.agent_id, 30),
        agentSecAPI.checkRegression(form.agent_id),
        agentSecAPI.getEvalHistory(form.agent_id),
      ]);
      setTrend(trendR.data.trend || []);
      setRegression(regR.data);
      setHistory(histR.data.history || []);
    } catch (e) {}
  };

  useEffect(() => { loadData(); }, [form.agent_id]);

  const runEval = async () => {
    setLoading(true);
    setResult(null);
    try {
      const r = await agentSecAPI.runEval(form);
      setResult(r.data.result);
      loadData();
    } catch (e: any) {
      alert("Eval failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const toggleCategory = (c: string) => {
    setForm(f => ({
      ...f,
      categories: f.categories.includes(c) ? f.categories.filter(x => x !== c) : [...f.categories, c]
    }));
  };

  const trendChartData = trend.map(t => ({
    date: new Date(t.run_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    pass_rate: t.pass_rate,
  }));

  const breakdownData = result ? Object.entries(result.category_breakdown || {}).map(([cat, data]: any) => ({
    category: cat.replace("_", " "),
    passed: data.passed,
    failed: data.failed,
  })) : [];

  return (
    <div className="min-h-screen">
      <nav className="border-b border-border bg-panel px-8 py-4 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-white transition-colors"><ChevronLeft size={20} /></Link>
      
        <span className="font-semibold">Agent Eval</span>
        <span className="text-xs text-gray-500">— Continuous adversarial testing</span>
      </nav>

      <div className="max-w-7xl mx-auto px-8 py-8">
        {/* ── Regression Alert ── */}
        {regression?.regression_detected && (
          <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-center gap-3">
            <AlertTriangle className="text-red-400" size={20} />
            <div>
              <span className="text-red-400 font-medium">Regression Detected!</span>
              <span className="text-gray-400 text-sm ml-2">{regression.alert}</span>
              <span className="text-gray-500 text-xs ml-2">({regression.previous_pass_rate}% → {regression.latest_pass_rate}%)</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-6">
          {/* ── Config ── */}
          <div className="space-y-4">
            <h2 className="text-xs text-gray-500 uppercase tracking-widest">Eval Configuration</h2>

            {[
              { label: "Agent ID *", key: "agent_id", mono: true },
              { label: "Agent Name *", key: "agent_name" },
              { label: "Endpoint URL *", key: "endpoint_url" },
              { label: "Auth Header", key: "auth_header" },
            ].map(({ label, key, mono }) => (
              <div key={key}>
                <label className="block text-xs text-gray-500 mb-1.5">{label}</label>
                <input
                  value={(form as any)[key]}
                  onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                  className={`w-full bg-panel border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-accent ${mono ? "font-mono" : ""}`}
                />
              </div>
            ))}

            <div>
              <label className="block text-xs text-gray-500 mb-1.5">Consistency Checks: {form.consistency_checks}</label>
              <input
                type="range" min={1} max={5} value={form.consistency_checks}
                onChange={e => setForm(f => ({ ...f, consistency_checks: Number(e.target.value) }))}
                className="w-full accent-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-500 mb-2">Attack Categories</label>
              <div className="flex flex-wrap gap-2">
                {CATEGORIES.map(c => (
                  <button
                    key={c}
                    onClick={() => toggleCategory(c)}
                    className={`text-xs px-2.5 py-1 rounded-full border transition-colors font-mono ${
                      form.categories.includes(c) ? "bg-accent/20 border-accent text-accent" : "border-border text-gray-500"
                    }`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={runEval}
              disabled={loading || !form.agent_id || !form.endpoint_url}
              className="w-full bg-orange-600 hover:bg-orange-700 disabled:opacity-50 py-3 rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2"
            >
              {loading ? (
                <><div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> Running Eval...</>
              ) : (
                "Run Eval Now"
                )}
            </button>

            {/* History */}
            {history.length > 0 && (
              <div className="bg-panel border border-border rounded-xl p-4">
                <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-3">Run History</h3>
                <div className="space-y-2">
                  {history.slice(0, 5).map((h, i) => (
                    <div key={i} className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">{new Date(h.run_at).toLocaleDateString()}</span>
                      <span className={`font-mono font-bold ${h.pass_rate >= 80 ? "text-green-400" : h.pass_rate >= 60 ? "text-yellow-400" : "text-red-400"}`}>
                        {h.pass_rate}%
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* ── Results ── */}
          <div className="col-span-2 space-y-5">
            {/* Trend Chart */}
            {trendChartData.length > 1 && (
              <div className="bg-panel border border-border rounded-xl p-5">
                <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-4">Pass Rate Trend</h3>
                <ResponsiveContainer width="100%" height={160}>
                  <LineChart data={trendChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                    <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} />
                    <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} unit="%" />
                    <Tooltip contentStyle={{ backgroundColor: "#13161d", border: "1px solid #1e2330", borderRadius: "8px" }} />
                    <Line type="monotone" dataKey="pass_rate" stroke="#f97316" strokeWidth={2} dot={{ fill: "#f97316", r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}

            {loading && (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="animate-spin w-10 h-10 border-2 border-orange-400 border-t-transparent rounded-full mb-4" />
                <p className="text-sm text-gray-400">Running adversarial eval...</p>
              </div>
            )}

            {result && (
              <>
                {/* Summary */}
                <div className="grid grid-cols-4 gap-3">
                  {[
                    { label: "Pass Rate", val: `${result.pass_rate}%`, color: result.pass_rate >= 80 ? "text-green-400" : result.pass_rate >= 60 ? "text-yellow-400" : "text-red-400" },
                    { label: "Consistency", val: `${result.consistency_score}%`, color: "text-indigo-400" },
                    { label: "Tests Run", val: result.total_tests, color: "text-white" },
                    { label: "Vulnerabilities", val: result.successful_attacks, color: result.successful_attacks > 0 ? "text-red-400" : "text-green-400" },
                  ].map(({ label, val, color }) => (
                    <div key={label} className="bg-panel border border-border rounded-xl p-4 text-center">
                      <div className={`text-2xl font-bold font-mono ${color}`}>{val}</div>
                      <div className="text-xs text-gray-500 mt-1">{label}</div>
                    </div>
                  ))}
                </div>

                {/* Category Breakdown */}
                {breakdownData.length > 0 && (
                  <div className="bg-panel border border-border rounded-xl p-5">
                    <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-4">Category Breakdown</h3>
                    <ResponsiveContainer width="100%" height={180}>
                      <BarChart data={breakdownData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
                        <XAxis dataKey="category" tick={{ fill: "#6b7280", fontSize: 10 }} />
                        <YAxis tick={{ fill: "#6b7280", fontSize: 11 }} />
                        <Tooltip contentStyle={{ backgroundColor: "#13161d", border: "1px solid #1e2330", borderRadius: "8px" }} />
                        <Legend />
                        <Bar dataKey="passed" fill="#22c55e" name="Blocked" radius={[3, 3, 0, 0]} />
                        <Bar dataKey="failed" fill="#ef4444" name="Succeeded" radius={[3, 3, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Failed Attacks */}
                {result.failed_attacks?.length > 0 && (
                  <div className="bg-panel border border-border rounded-xl p-5">
                    <h3 className="text-xs text-gray-500 uppercase tracking-widest mb-3">Successful Attacks (Fix These)</h3>
                    <div className="space-y-2 max-h-64 overflow-y-auto">
                      {result.failed_attacks.map((a: any, i: number) => (
                        <div key={i} className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
                          <div className="flex items-center gap-2 mb-1">
                            <span className={`text-xs px-2 py-0.5 rounded-full severity-${a.severity}`}>{a.severity}</span>
                            <span className="text-xs text-gray-400 font-mono">{a.category}</span>
                          </div>
                          <p className="text-xs text-gray-300 font-mono">{a.payload}</p>
                          {a.reason && <p className="text-xs text-gray-500 mt-1">{a.reason}</p>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
