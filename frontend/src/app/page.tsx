// // "use client";
// // import { useState, useEffect } from "react";
// // import { Shield, Scan, Activity, AlertTriangle, CheckCircle, XCircle, ChevronRight, Zap } from "lucide-react";
// // import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
// // import Navbar from "@/components/Navbar"
// // import agentSecAPI from "@/lib/api";
// // import Link from "next/link";

// // // ─── Score Ring ────────────────────────────────────────────────────────────
// // function ScoreRing({ score }: { score: number }) {
// //   const r = 40;
// //   const circ = 2 * Math.PI * r;
// //   const offset = circ - (score / 100) * circ;
// //   const color = score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444";

// //   return (
// //     <div className="relative w-28 h-28 flex items-center justify-center">
// //       <svg width="112" height="112" className="absolute">
// //         <circle cx="56" cy="56" r={r} fill="none" stroke="#1e2330" strokeWidth="8" />
// //         <circle
// //           cx="56" cy="56" r={r} fill="none"
// //           stroke={color} strokeWidth="8"
// //           strokeDasharray={circ}
// //           strokeDashoffset={offset}
// //           strokeLinecap="round"
// //           style={{ transform: "rotate(-90deg)", transformOrigin: "56px 56px", transition: "stroke-dashoffset 1s ease" }}
// //         />
// //       </svg>
// //       <div className="text-center z-10">
// //         <div className="text-2xl font-bold" style={{ color }}>{score}</div>
// //         <div className="text-xs text-gray-500">/ 100</div>
// //       </div>
// //     </div>
// //   );
// // }

// // // ─── Stat Card ─────────────────────────────────────────────────────────────
// // function StatCard({ label, value, sub, color = "text-white" }: any) {
// //   return (
// //     <div className="bg-panel border border-border rounded-xl p-5">
// //       <div className={`text-3xl font-bold font-mono ${color}`}>{value}</div>
// //       <div className="text-sm text-gray-400 mt-1">{label}</div>
// //       {sub && <div className="text-xs text-gray-600 mt-0.5">{sub}</div>}
// //     </div>
// //   );
// // }

// // // ─── Main Page ─────────────────────────────────────────────────────────────
// // export default function Dashboard() {
// //   const [agentId, setAgentId] = useState("my-agent-001");
// //   const [inputId, setInputId] = useState("my-agent-001");
// //   const [data, setData] = useState<any>(null);
// //   const [loading, setLoading] = useState(false);
// //   const [agents, setAgents] = useState<any[]>([]);

// //   useEffect(() => {
// //     agentSecAPI.listAgents().then(r => setAgents(r.data.agents || [])).catch(() => {});
// //   }, []);

// //   const loadDashboard = async () => {
// //     setLoading(true);
// //     try {
// //       const r = await agentSecAPI.getDashboard(agentId);
// //       setData(r.data);
// //     } catch (e) {
// //       console.error(e);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   useEffect(() => { loadDashboard(); }, [agentId]);

// //   const trendData = data?.eval_trend?.map((t: any) => ({
// //     date: new Date(t.run_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
// //     pass_rate: t.pass_rate,
// //   })) || [];

// //   return (
// //     <div className="min-h-screen bg-surface">
// //       {/* ── Nav ── */}
// //       <Navbar />
// //         <div className="flex items-center gap-3">
// //           <Shield className="text-accent" size={24} />
// //           <span className="text-lg font-semibold tracking-tight">AgentSec</span>
// //           <span className="text-xs text-muted bg-border px-2 py-0.5 rounded-full ml-1">v1.0</span>
// //         </div>
// //         <div className="flex items-center gap-6 text-sm text-gray-400">
// //           <Link href="/" className="text-white font-medium">Dashboard</Link>
// //           <Link href="/scan" className="hover:text-white transition-colors">Scan</Link>
// //           <Link href="/shield" className="hover:text-white transition-colors">Shield</Link>
// //           <Link href="/eval" className="hover:text-white transition-colors">Eval</Link>
// //         </div>
// //       </nav>

// //       <div className="max-w-7xl mx-auto px-8 py-8">
// //         {/* ── Agent Selector ── */}
// //         <div className="flex items-center gap-3 mb-8">
// //           <div className="flex-1 max-w-sm flex gap-2">
// //             <input
// //               value={inputId}
// //               onChange={e => setInputId(e.target.value)}
// //               placeholder="Enter Agent ID..."
// //               className="flex-1 bg-panel border border-border rounded-lg px-4 py-2 text-sm font-mono focus:outline-none focus:border-accent"
// //             />
// //             <button
// //               onClick={() => setAgentId(inputId)}
// //               className="bg-accent hover:bg-accent-dim px-4 py-2 rounded-lg text-sm font-medium transition-colors"
// //             >
// //               Load
// //             </button>
// //           </div>
// //           {agents.length > 0 && (
// //             <select
// //               onChange={e => { setInputId(e.target.value); setAgentId(e.target.value); }}
// //               className="bg-panel border border-border rounded-lg px-3 py-2 text-sm text-gray-400 focus:outline-none focus:border-accent"
// //             >
// //               <option value="">Recent agents...</option>
// //               {agents.map((a: any) => (
// //                 <option key={a.agent_id} value={a.agent_id}>
// //                   {a.agent_name} ({a.agent_id})
// //                 </option>
// //               ))}
// //             </select>
// //           )}
// //         </div>

// //         {loading && (
// //           <div className="text-center py-20 text-gray-500">
// //             <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
// //             Loading dashboard...
// //           </div>
// //         )}

// //         {!loading && data && (
// //           <>
// //             {/* ── Regression Alert ── */}
// //             {data.regression?.regression_detected && (
// //               <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-center gap-3">
// //                 <AlertTriangle className="text-red-400 shrink-0" size={20} />
// //                 <div>
// //                   <span className="text-red-400 font-medium">Regression Detected</span>
// //                   <span className="text-gray-400 text-sm ml-2">{data.regression.alert}</span>
// //                 </div>
// //               </div>
// //             )}

// //             {/* ── Top Row ── */}
// //             <div className="grid grid-cols-4 gap-4 mb-6">
// //               {/* Security Score */}
// //               <div className="col-span-1 bg-panel border border-border rounded-xl p-6 flex flex-col items-center justify-center">
// //                 <div className="text-xs text-gray-500 mb-3 uppercase tracking-widest">Security Score</div>
// //                 <ScoreRing score={data.latest_scan?.security_score ?? 0} />
// //                 <div className={`mt-3 text-sm font-medium px-3 py-1 rounded-full ${
// //                   data.latest_scan?.risk_level === "CRITICAL" ? "severity-CRITICAL" :
// //                   data.latest_scan?.risk_level === "HIGH" ? "severity-HIGH" :
// //                   data.latest_scan?.risk_level === "MEDIUM" ? "severity-MEDIUM" : "severity-LOW"
// //                 }`}>
// //                   {data.latest_scan?.risk_level ?? "N/A"}
// //                 </div>
// //               </div>

// //               {/* Stats */}
// //               <div className="col-span-3 grid grid-cols-3 gap-4">
// //                 <StatCard
// //                   label="Attacks Blocked (24h)"
// //                   value={data.shield?.total_blocked ?? 0}
// //                   color="text-red-400"
// //                   sub="by Agent Shield"
// //                 />
// //                 <StatCard
// //                   label="Eval Pass Rate"
// //                   value={`${data.latest_eval?.pass_rate ?? "—"}%`}
// //                   color="text-green-400"
// //                   sub={`${data.latest_eval?.total_tests ?? 0} tests run`}
// //                 />
// //                 <StatCard
// //                   label="Consistency Score"
// //                   value={`${data.latest_eval?.consistency_score ?? "—"}%`}
// //                   color="text-indigo-400"
// //                   sub="response stability"
// //                 />
// //               </div>
// //             </div>

// //             {/* ── Trend Chart ── */}
// //             {trendData.length > 1 && (
// //               <div className="bg-panel border border-border rounded-xl p-6 mb-6">
// //                 <h3 className="text-sm font-medium text-gray-400 mb-4">Pass Rate Trend (14 days)</h3>
// //                 <ResponsiveContainer width="100%" height={180}>
// //                   <LineChart data={trendData}>
// //                     <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
// //                     <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} />
// //                     <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} unit="%" />
// //                     <Tooltip
// //                       contentStyle={{ backgroundColor: "#13161d", border: "1px solid #1e2330", borderRadius: "8px" }}
// //                       labelStyle={{ color: "#9ca3af" }}
// //                     />
// //                     <Line type="monotone" dataKey="pass_rate" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1", r: 3 }} />
// //                   </LineChart>
// //                 </ResponsiveContainer>
// //               </div>
// //             )}

// //             {/* ── Quick Actions ── */}
// //             <div className="grid grid-cols-3 gap-4">
// //               {[
// //                 { href: "/scan", icon: Zap, label: "Run New Scan", sub: "Full static + dynamic analysis", color: "text-indigo-400" },
// //                 { href: "/shield", icon: Shield, label: "View Shield Logs", sub: "Runtime audit trail", color: "text-green-400" },
// //                 { href: "/eval", icon: Activity, label: "Run Eval", sub: "Adversarial testing", color: "text-orange-400" },
// //               ].map(({ href, icon: Icon, label, sub, color }) => (
// //                 <Link key={href} href={href}>
// //                   <div className="bg-panel border border-border hover:border-accent/50 rounded-xl p-5 flex items-center gap-4 cursor-pointer transition-colors group">
// //                     <Icon className={color} size={24} />
// //                     <div className="flex-1">
// //                       <div className="text-sm font-medium">{label}</div>
// //                       <div className="text-xs text-gray-500 mt-0.5">{sub}</div>
// //                     </div>
// //                     <ChevronRight className="text-gray-600 group-hover:text-gray-400 transition-colors" size={16} />
// //                   </div>
// //                 </Link>
// //               ))}
// //             </div>

// //             {/* ── Executive Summary ── */}
// //             {data.latest_scan?.executive_summary && (
// //               <div className="mt-6 bg-panel border border-border rounded-xl p-6">
// //                 <h3 className="text-sm font-medium text-gray-400 mb-2">Latest Scan — Executive Summary</h3>
// //                 <p className="text-sm text-gray-300 leading-relaxed">{data.latest_scan.executive_summary}</p>
// //               </div>
// //             )}
// //           </>
// //         )}

// //         {!loading && !data && (
// //           <div className="text-center py-20">
// //             <Shield className="mx-auto text-gray-700 mb-4" size={48} />
// //             <p className="text-gray-500 mb-2">No data found for this agent.</p>
// //             <p className="text-gray-600 text-sm">Run your first scan to get started.</p>
// //             <Link href="/scan">
// //               <button className="mt-4 bg-accent hover:bg-accent-dim px-6 py-2.5 rounded-lg text-sm font-medium transition-colors">
// //                 Start First Scan
// //               </button>
// //             </Link>
// //           </div>
// //         )}
// //       </div>
// //     </div>
// //   );
// // }
// //-----------------------------------------------------------------------------------------------------------------------------------------------



// "use client";
// import { useState, useEffect } from "react";
// import { Shield, Scan, Activity, AlertTriangle, CheckCircle, XCircle, ChevronRight, Zap } from "lucide-react";
// import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
// import Navbar from "@/components/Navbar"
// import agentSecAPI from "@/lib/api";
// import Link from "next/link";
// import RouteGuard from "@/components/RouteGuard";
// import UsageCard from "@/components/UsageCard";

// // ─── Score Ring ────────────────────────────────────────────────────────────
// function ScoreRing({ score }: { score: number }) {
//   const r = 40;
//   const circ = 2 * Math.PI * r;
//   const offset = circ - (score / 100) * circ;
//   const color = score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444";

//   return (
//     <div className="relative w-28 h-28 flex items-center justify-center">
//       <svg width="112" height="112" className="absolute">
//         <circle cx="56" cy="56" r={r} fill="none" stroke="#1e2330" strokeWidth="8" />
//         <circle
//           cx="56" cy="56" r={r} fill="none"
//           stroke={color} strokeWidth="8"
//           strokeDasharray={circ}
//           strokeDashoffset={offset}
//           strokeLinecap="round"
//           style={{ transform: "rotate(-90deg)", transformOrigin: "56px 56px", transition: "stroke-dashoffset 1s ease" }}
//         />
//       </svg>
//       <div className="text-center z-10">
//         <div className="text-2xl font-bold" style={{ color }}>{score}</div>
//         <div className="text-xs text-gray-500">/ 100</div>
//       </div>
//     </div>
//   );
// }

// // ─── Stat Card ─────────────────────────────────────────────────────────────
// function StatCard({ label, value, sub, color = "text-white" }: any) {
//   return (
//     <div className="bg-panel border border-border rounded-xl p-5">
//       <div className={`text-3xl font-bold font-mono ${color}`}>{value}</div>
//       <div className="text-sm text-gray-400 mt-1">{label}</div>
//       {sub && <div className="text-xs text-gray-600 mt-0.5">{sub}</div>}
//     </div>
//   );
// }

// // ─── Main Page ─────────────────────────────────────────────────────────────
// export default function Dashboard() {
//   const [agentId, setAgentId] = useState("my-agent-001");
//   const [inputId, setInputId] = useState("my-agent-001");
//   const [data, setData] = useState<any>(null);
//   const [loading, setLoading] = useState(false);
//   const [agents, setAgents] = useState<any[]>([]);

//   useEffect(() => {
//     agentSecAPI.listAgents().then(r => setAgents(r.data.agents || [])).catch(() => {});
//   }, []);

//   const loadDashboard = async () => {
//     setLoading(true);
//     try {
//       const r = await agentSecAPI.getDashboard(agentId);
//       setData(r.data);
//     } catch (e) {
//       console.error(e);
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => { loadDashboard(); }, [agentId]);

//   const trendData = data?.eval_trend?.map((t: any) => ({
//     date: new Date(t.run_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
//     pass_rate: t.pass_rate,
//   })) || [];

//   return (
//     <RouteGuard>
//     <div className="min-h-screen">
//       {/* ── Nav ── */}
//       <Navbar />
// <div className="max-w-7xl mx-auto px-8 pt-4"><UsageCard /></div>
//       <div className="max-w-7xl mx-auto px-8 py-8">
//         {/* ── Agent Selector ── */}
//         <div className="flex items-center gap-3 mb-8">
//           <div className="flex-1 max-w-sm flex gap-2">
//             <input
//               value={inputId}
//               onChange={e => setInputId(e.target.value)}
//               placeholder="Enter Agent ID..."
//               className="flex-1 bg-panel border border-border rounded-lg px-4 py-2 text-sm font-mono focus:outline-none focus:border-accent"
//             />
//             <button
//               onClick={() => setAgentId(inputId)}
//               className="bg-accent hover:bg-accent-dim px-4 py-2 rounded-lg text-sm font-medium transition-colors"
//             >
//               Load
//             </button>
//           </div>
//           {agents.length > 0 && (
//             <select
//               onChange={e => { setInputId(e.target.value); setAgentId(e.target.value); }}
//               className="bg-panel border border-border rounded-lg px-3 py-2 text-sm text-gray-400 focus:outline-none focus:border-accent"
//             >
//               <option value="">Recent agents...</option>
//               {agents.map((a: any) => (
//                 <option key={a.agent_id} value={a.agent_id}>
//                   {a.agent_name} ({a.agent_id})
//                 </option>
//               ))}
//             </select>
//           )}
//         </div>

//         {loading && (
//           <div className="text-center py-20 text-gray-500">
//             <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
//             Loading dashboard...
//           </div>
//         )}

//         {!loading && data && (
//           <>
//             {/* ── Regression Alert ── */}
//             {data.regression?.regression_detected && (
//               <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-center gap-3">
//                 <AlertTriangle className="text-red-400 shrink-0" size={20} />
//                 <div>
//                   <span className="text-red-400 font-medium">Regression Detected</span>
//                   <span className="text-gray-400 text-sm ml-2">{data.regression.alert}</span>
//                 </div>
//               </div>
//             )}

//             {/* ── Top Row ── */}
//             <div className="grid grid-cols-4 gap-4 mb-6">
//               {/* Security Score */}
//               <div className="col-span-1 bg-panel border border-border rounded-xl p-6 flex flex-col items-center justify-center">
//                 <div className="text-xs text-gray-500 mb-3 uppercase tracking-widest">Security Score</div>
//                 <ScoreRing score={data.latest_scan?.security_score ?? 0} />
//                 <div className={`mt-3 text-sm font-medium px-3 py-1 rounded-full ${
//                   data.latest_scan?.risk_level === "CRITICAL" ? "severity-CRITICAL" :
//                   data.latest_scan?.risk_level === "HIGH" ? "severity-HIGH" :
//                   data.latest_scan?.risk_level === "MEDIUM" ? "severity-MEDIUM" : "severity-LOW"
//                 }`}>
//                   {data.latest_scan?.risk_level ?? "N/A"}
//                 </div>
//               </div>

//               {/* Stats */}
//               <div className="col-span-3 grid grid-cols-3 gap-4">
//                 <StatCard
//                   label="Attacks Blocked (24h)"
//                   value={data.shield?.total_blocked ?? 0}
//                   color="text-red-400"
//                   sub="by Agent Shield"
//                 />
//                 <StatCard
//                   label="Eval Pass Rate"
//                   value={`${data.latest_eval?.pass_rate ?? "—"}%`}
//                   color="black-400"
//                   sub={`${data.latest_eval?.total_tests ?? 0} tests run`}
//                 />
//                 <StatCard
//                   label="Consistency Score"
//                   value={`${data.latest_eval?.consistency_score ?? "—"}%`}
//                   color="text-indigo-400"
//                   sub="response stability"
//                 />
//               </div>
//             </div>

//             {/* ── Trend Chart ── */}
//             {trendData.length > 1 && (
//               <div className="bg-panel border border-border rounded-xl p-6 mb-6">
//                 <h3 className="text-sm font-medium text-gray-400 mb-4">Pass Rate Trend (14 days)</h3>
//                 <ResponsiveContainer width="100%" height={180}>
//                   <LineChart data={trendData}>
//                     <CartesianGrid strokeDasharray="3 3" stroke="#1e2330" />
//                     <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} />
//                     <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} unit="%" />
//                     <Tooltip
//                       contentStyle={{ backgroundColor: "#13161d", border: "1px solid #1e2330", borderRadius: "8px" }}
//                       labelStyle={{ color: "#9ca3af" }}
//                     />
//                     <Line type="monotone" dataKey="pass_rate" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1", r: 3 }} />
//                   </LineChart>
//                 </ResponsiveContainer>
//               </div>
//             )}

//             {/* ── Quick Actions ── */}
//             <div className="grid grid-cols-4 gap-4">
//               {[
//                 { href: "/scan", icon: Zap, label: "Run New Scan", sub: "Full static + dynamic analysis", color: "text-indigo-400" },
//                 { href: "/shield", icon: Shield, label: "View Shield Logs", sub: "Runtime audit trail", color: "text-green-400" },
//                 { href: "/eval", icon: Activity, label: "Run Eval", sub: "Adversarial testing", color: "text-orange-400" },
//                 { href: `/reports/${data.latest_scan?.scan_id}`, icon: Scan, label: "View Full Report", sub: "Detailed attack breakdown", color: "text-blue-400" },
//               ].map(({ href, icon: Icon, label, sub, color }) => (
//                 <Link key={href} href={href}>
//                   <div className="bg-panel border border-border hover:border-accent/50 rounded-xl p-5 flex items-center gap-4 cursor-pointer transition-colors group">
//                     <Icon className={color} size={24} />
//                     <div className="flex-1">
//                       <div className="text-sm font-medium">{label}</div>
//                       <div className="text-xs text-gray-500 mt-0.5">{sub}</div>
//                     </div>
//                     <ChevronRight className="text-gray-600 group-hover:text-gray-400 transition-colors" size={16} />
//                   </div>
//                 </Link>
//               ))}
//             </div>

//             {/* ── Executive Summary ── */}
//             {data.latest_scan?.executive_summary && (
//               <div className="mt-6 bg-panel border border-border rounded-xl p-6">
//                 <h3 className="text-sm font-medium text-black-400 mb-2">Latest Scan — Executive Summary</h3>
//                 <p className="text-sm text-gray-300 leading-relaxed">{data.latest_scan.executive_summary}</p>
//                 <Link
//                   href={`/reports/${data.latest_scan?.scan_id}`}
//                   className="mt-4 inline-flex items-center gap-1 text-sm text-accent hover:underline"
//                 >
//                   View full report <ChevronRight size={14} />
//                 </Link>
//               </div>
//             )}
//           </>
//         )}

//         {!loading && !data && (
//           <div className="text-center py-20">
//             <Shield className="mx-auto text-gray-700 mb-4" size={48} />
//             <p className="text-gray-500 mb-2">No data found for this agent.</p>
//             <p className="text-gray-600 text-sm">Run your first scan to get started.</p>
//             <Link href="/scan">
//               <button className="mt-4 bg-accent hover:bg-accent-dim px-6 py-2.5 rounded-lg text-sm font-medium transition-colors">
//                 Start First Scan
//               </button>
//             </Link>
//           </div>
//         )}
//       </div>
//     </div>
//     </RouteGuard>
//   );
// }







"use client";
import { useState, useEffect } from "react";
import { Shield, Scan, Activity, AlertTriangle, ChevronRight, Zap } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import Navbar from "@/components/Navbar";
import agentSecAPI from "@/lib/api";
import Link from "next/link";
import RouteGuard from "@/components/RouteGuard";
import UsageCard from "@/components/UsageCard";

function ScoreRing({ score }: { score: number }) {
  const r = 40;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 80 ? "#22c55e" : score >= 60 ? "#f59e0b" : "#ef4444";

  return (
    <div className="relative w-28 h-28 flex items-center justify-center">
      <svg width="112" height="112" className="absolute">
        <circle cx="56" cy="56" r={r} fill="none" stroke="#d9d6cf" strokeWidth="8" />
        <circle
          cx="56" cy="56" r={r} fill="none"
          stroke={color} strokeWidth="8"
          strokeDasharray={circ}
          strokeDashoffset={offset}
          strokeLinecap="round"
          style={{ transform: "rotate(-90deg)", transformOrigin: "56px 56px", transition: "stroke-dashoffset 1s ease" }}
        />
      </svg>
      <div className="text-center z-10">
        <div className="text-2xl font-bold" style={{ color }}>{score}</div>
        <div className="text-xs text-muted">/ 100</div>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, color = "text-gray-900" }: any) {
  return (
    <div className="bg-panel border border-border rounded-xl p-5">
      <div className={`text-3xl font-bold font-mono ${color}`}>{value}</div>
      <div className="text-sm text-muted mt-1">{label}</div>
      {sub && <div className="text-xs text-subtle mt-0.5">{sub}</div>}
    </div>
  );
}

export default function Dashboard() {
  const [agentId, setAgentId] = useState("my-agent-001");
  const [inputId, setInputId] = useState("my-agent-001");
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [agents, setAgents] = useState<any[]>([]);

  useEffect(() => {
    agentSecAPI.listAgents().then((r) => setAgents(r.data.agents || [])).catch(() => {});
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      const r = await agentSecAPI.getDashboard(agentId);
      setData(r.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDashboard(); }, [agentId]);

  const trendData = data?.eval_trend?.map((t: any) => ({
    date: new Date(t.run_at).toLocaleDateString("en-IN", { month: "short", day: "numeric" }),
    pass_rate: t.pass_rate,
  })) || [];

  return (
    <RouteGuard>
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-7xl mx-auto px-8 pt-4"><UsageCard /></div>
        <div className="max-w-7xl mx-auto px-8 py-8">
          <div className="flex items-center gap-3 mb-8">
            <div className="flex-1 max-w-sm flex gap-2">
              <input
                value={inputId}
                onChange={(e) => setInputId(e.target.value)}
                placeholder="Enter Agent ID..."
                className="flex-1 bg-panel border border-border rounded-lg px-4 py-2 text-sm font-mono text-gray-900 focus:outline-none focus:border-accent"
              />
              <button
                onClick={() => setAgentId(inputId)}
                className="bg-accent text-white hover:opacity-90 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
              >
                Load
              </button>
            </div>
            {agents.length > 0 && (
              <select
                onChange={(e) => { setInputId(e.target.value); setAgentId(e.target.value); }}
                className="bg-panel border border-border rounded-lg px-3 py-2 text-sm text-muted focus:outline-none focus:border-accent"
              >
                <option value="">Recent agents...</option>
                {agents.map((a: any) => (
                  <option key={a.agent_id} value={a.agent_id}>{a.agent_name} ({a.agent_id})</option>
                ))}
              </select>
            )}
          </div>

          {loading && (
            <div className="text-center py-20 text-muted">
              <div className="animate-spin w-8 h-8 border-2 border-accent border-t-transparent rounded-full mx-auto mb-3" />
              Loading dashboard...
            </div>
          )}

          {!loading && data && (
            <>
              {data.regression?.regression_detected && (
                <div className="mb-6 bg-red-500/10 border border-red-500/30 rounded-xl px-5 py-4 flex items-center gap-3">
                  <AlertTriangle className="text-red-500 shrink-0" size={20} />
                  <div>
                    <span className="text-red-500 font-medium">Regression Detected</span>
                    <span className="text-muted text-sm ml-2">{data.regression.alert}</span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-4 gap-4 mb-6">
                <div className="col-span-1 bg-panel border border-border rounded-xl p-6 flex flex-col items-center justify-center">
                  <div className="text-xs text-muted mb-3 uppercase tracking-widest">Security Score</div>
                  <ScoreRing score={data.latest_scan?.security_score ?? 0} />
                  <div className={`mt-3 text-sm font-medium px-3 py-1 rounded-full ${
                    data.latest_scan?.risk_level === "CRITICAL" ? "severity-CRITICAL" :
                    data.latest_scan?.risk_level === "HIGH" ? "severity-HIGH" :
                    data.latest_scan?.risk_level === "MEDIUM" ? "severity-MEDIUM" : "severity-LOW"
                  }`}>
                    {data.latest_scan?.risk_level ?? "N/A"}
                  </div>
                </div>

                <div className="col-span-3 grid grid-cols-3 gap-4">
                  <StatCard label="Attacks Blocked (24h)" value={data.shield?.total_blocked ?? 0} color="text-red-500" sub="by Agent Shield" />
                  <StatCard label="Eval Pass Rate" value={`${data.latest_eval?.pass_rate ?? "—"}%`} color="text-gray-900" sub={`${data.latest_eval?.total_tests ?? 0} tests run`} />
                  <StatCard label="Consistency Score" value={`${data.latest_eval?.consistency_score ?? "—"}%`} color="text-indigo-500" sub="response stability" />
                </div>
              </div>

              {trendData.length > 1 && (
                <div className="bg-panel border border-border rounded-xl p-6 mb-6">
                  <h3 className="text-sm font-medium text-muted mb-4">Pass Rate Trend (14 days)</h3>
                  <ResponsiveContainer width="100%" height={180}>
                    <LineChart data={trendData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#d9d6cf" />
                      <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 11 }} />
                      <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} unit="%" />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#f4f2ee", border: "1px solid #d9d6cf", borderRadius: "8px" }}
                        labelStyle={{ color: "#4b5563" }}
                      />
                      <Line type="monotone" dataKey="pass_rate" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1", r: 3 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}

              <div className="grid grid-cols-4 gap-4">
                {[
                  { href: "/scan", icon: Zap, label: "Run New Scan", sub: "Full static + dynamic analysis", color: "text-indigo-500" },
                  { href: "/shield", icon: Shield, label: "View Shield Logs", sub: "Runtime audit trail", color: "text-green-500" },
                  { href: "/eval", icon: Activity, label: "Run Eval", sub: "Adversarial testing", color: "text-orange-500" },
                  { href: `/reports/${data.latest_scan?.scan_id}`, icon: Scan, label: "View Full Report", sub: "Detailed attack breakdown", color: "text-blue-500" },
                ].map(({ href, icon: Icon, label, sub, color }) => (
                  <Link key={href} href={href}>
                    <div className="bg-panel border border-border hover:border-accent/50 rounded-xl p-5 flex items-center gap-4 cursor-pointer transition-colors group">
                      <Icon className={color} size={24} />
                      <div className="flex-1">
                        <div className="text-sm font-medium text-gray-900">{label}</div>
                        <div className="text-xs text-muted mt-0.5">{sub}</div>
                      </div>
                      <ChevronRight className="text-subtle group-hover:text-gray-900 transition-colors" size={16} />
                    </div>
                  </Link>
                ))}
              </div>

              {data.latest_scan?.executive_summary && (
                <div className="mt-6 bg-panel border border-border rounded-xl p-6">
                  <h3 className="text-sm font-medium text-gray-900 mb-2">Latest Scan — Executive Summary</h3>
                  <p className="text-sm text-gray-700 leading-relaxed">{data.latest_scan.executive_summary}</p>
                  <Link href={`/reports/${data.latest_scan?.scan_id}`} className="mt-4 inline-flex items-center gap-1 text-sm text-accent hover:underline">
                    View full report <ChevronRight size={14} />
                  </Link>
                </div>
              )}
            </>
          )}

          {!loading && !data && (
            <div className="text-center py-20">
              <Shield className="mx-auto text-subtle mb-4" size={48} />
              <p className="text-muted mb-2">No data found for this agent.</p>
              <p className="text-subtle text-sm">Run your first scan to get started.</p>
              <Link href="/scan">
                <button className="mt-4 bg-accent text-white hover:opacity-90 px-6 py-2.5 rounded-lg text-sm font-medium transition-colors">
                  Start First Scan
                </button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </RouteGuard>
  );
}