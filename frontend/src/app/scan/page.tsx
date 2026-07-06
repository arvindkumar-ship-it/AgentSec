"use client";
import { useState } from "react";
import { Shield, ChevronLeft, CheckCircle, XCircle, AlertTriangle, MessageSquare, FileText } from "lucide-react";
import agentSecAPI from "@/lib/api";
import Link from "next/link";

const CATEGORIES = [
  "prompt_injection", "insecure_output", "data_exfiltration",
  "excessive_agency", "denial_of_service", "memory_poisoning",
  "indirect_injection", "jailbreak", "auth_bypass"
];

function SeverityBadge({ sev }: { sev: string }) {
  const colors: Record<string, string> = {
    CRITICAL: "bg-red-500/20 text-red-400 border border-red-500/30",
    HIGH: "bg-orange-500/20 text-orange-400 border border-orange-500/30",
    MEDIUM: "bg-yellow-500/20 text-yellow-400 border border-yellow-500/30",
    LOW: "bg-green-500/20 text-green-400 border border-green-500/30",
  };
  return <span className={`text-xs px-2 py-0.5 rounded-full ${colors[sev] || "bg-gray-500/20 text-gray-400"}`}>{sev}</span>;
}

function VerdictIcon({ success, needs_review }: { success: boolean; needs_review?: boolean }) {
  if (needs_review) return <AlertTriangle className="text-yellow-400 shrink-0" size={15} />;
  return success
    ? <XCircle className="text-red-400 shrink-0" size={15} />
    : <CheckCircle className="text-green-400 shrink-0" size={15} />;
}

function StaticFinding({ f }: { f: any }) {
  return (
    <div className="bg-surface border border-border rounded-lg p-4">
      <div className="flex items-start justify-between gap-2 mb-1">
        <span className="text-sm font-medium">{f.name || f.description || f.pattern}</span>
        <div className="flex gap-1 shrink-0">
          <SeverityBadge sev={f.severity} />
          {f.confidence === "heuristic" && (
            <span className="text-xs px-2 py-0.5 rounded-full bg-gray-500/10 text-gray-500 border border-gray-500/20">heuristic</span>
          )}
        </div>
      </div>
      <p className="text-xs text-gray-500 mb-2">{f.type}</p>
      {f.fix && <div className="bg-green-500/5 border border-green-500/20 rounded p-2.5 mt-2"><p className="text-xs text-green-400"><span className="font-medium">Fix: </span>{f.fix}</p></div>}
    </div>
  );
}

function AttackCard({ r }: { r: any }) {
  const success = r.verdict?.success;
  const needs_review = r.verdict?.needs_review;
  return (
    <div className={`border rounded-lg p-4 ${success ? "border-red-500/30 bg-red-500/5" : needs_review ? "border-yellow-500/30 bg-yellow-500/5" : "border-border bg-surface"}`}>
      <div className="flex items-center gap-2 mb-2">
        <VerdictIcon success={success} needs_review={needs_review} />
        <span className="text-sm font-medium">{success ? "Attack Succeeded" : needs_review ? "Needs Review" : "Blocked"}</span>
        <SeverityBadge sev={r.severity} />
        <span className="text-xs text-gray-500 ml-auto font-mono">{r.category}</span>
        {r.verdict?.agreement && <span className="text-xs text-gray-600">{r.verdict.agreement} signals</span>}
      </div>
      <p className="text-xs font-mono bg-surface border border-border rounded p-2 mb-2 text-gray-300">{r.payload}</p>
      {r.verdict?.reason && <p className="text-xs text-gray-500">{r.verdict.reason}</p>}
      {success && r.verdict?.recommendation && (
        <div className="mt-2 bg-orange-500/10 border border-orange-500/20 rounded p-2">
          <p className="text-xs text-orange-400"><span className="font-medium">Fix: </span>{r.verdict.recommendation}</p>
        </div>
      )}
    </div>
  );
}

function MultiturnCard({ r }: { r: any }) {
  const [open, setOpen] = useState(false);
  const success = r.verdict?.success;
  const needs_review = r.verdict?.needs_review;
  return (
    <div className={`border rounded-lg p-4 ${success ? "border-red-500/30 bg-red-500/5" : needs_review ? "border-yellow-500/30 bg-yellow-500/5" : "border-border bg-surface"}`}>
      <div className="flex items-center gap-2 mb-2">
        <VerdictIcon success={success} needs_review={needs_review} />
        <span className="text-sm font-medium">{r.chain_name?.replace(/_/g, " ")}</span>
        <SeverityBadge sev={r.severity} />
        <span className="text-xs text-gray-500 ml-auto font-mono">{r.category}</span>
      </div>
      {r.verdict?.reason && <p className="text-xs text-gray-500 mb-2">{r.verdict.reason}</p>}
      {r.execution_failed && <p className="text-xs text-red-400">Execution failed: {r.error}</p>}
      {r.transcript && r.transcript.length > 0 && (
        <button onClick={() => setOpen(!open)} className="text-xs text-indigo-400 hover:text-indigo-300 mt-1">
          {open ? "Hide" : "Show"} {r.transcript.length}-turn transcript
        </button>
      )}
      {open && (
        <div className="mt-3 space-y-2 border-t border-border pt-3">
          {r.transcript.map((t: any, i: number) => (
            <div key={i}>
              <p className="text-xs text-gray-500 font-medium mb-0.5">Turn {t.turn} — User:</p>
              <p className="text-xs font-mono bg-surface border border-border rounded p-2 mb-1 text-gray-300">{t.user}</p>
              <p className="text-xs text-gray-500 font-medium mb-0.5">Agent:</p>
              <p className="text-xs font-mono bg-surface border border-border rounded p-2 text-gray-400">{t.assistant?.slice(0, 300)}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function DocInjectionCard({ r }: { r: any }) {
  const success = r.verdict?.success;
  const needs_review = r.verdict?.needs_review;
  return (
    <div className={`border rounded-lg p-4 ${success ? "border-red-500/30 bg-red-500/5" : needs_review ? "border-yellow-500/30 bg-yellow-500/5" : "border-border bg-surface"}`}>
      <div className="flex items-center gap-2 mb-2">
        <VerdictIcon success={success} needs_review={needs_review} />
        <span className="text-sm font-medium">{r.name?.replace(/_/g, " ")}</span>
        <SeverityBadge sev={r.severity} />
      </div>
      <p className="text-xs text-gray-500 mb-1">Benign question asked: <span className="text-gray-400 italic">{r.benign_question}</span></p>
      {r.verdict?.reason && <p className="text-xs text-gray-500 mt-1">{r.verdict.reason}</p>}
      {r.execution_failed && <p className="text-xs text-red-400">Execution failed</p>}
    </div>
  );
}


function BlackboxCard({ f }: { f: any }) {
  return (
    <div className={`border rounded-lg p-4 ${f.severity === "CRITICAL" ? "border-red-500/30 bg-red-500/5" : f.severity === "HIGH" ? "border-orange-500/30 bg-orange-500/5" : "border-yellow-500/30 bg-yellow-500/5"}`}>
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className={f.severity === "CRITICAL" ? "text-red-400" : f.severity === "HIGH" ? "text-orange-400" : "text-yellow-400"} size={15} />
        <SeverityBadge sev={f.severity} />
        <span className="text-xs text-gray-500 ml-auto font-mono">{f.confidence}</span>
      </div>
      <p className="text-sm text-gray-300 mb-1">{f.finding}</p>
      <p className="text-xs text-gray-600">{f.what_was_tested}</p>
      {f.evidence && <p className="text-xs text-gray-500 mt-1 font-mono truncate">{f.evidence}</p>}
    </div>
  );
}

type TabType = "static" | "attacks" | "multiturn" | "docinjection" | "blackbox" | "fixes";

export default function ScanPage() {
  const [form, setForm] = useState({
    agent_id: "my-agent-001",
    agent_name: "",
    system_prompt: "",
    endpoint_url: "",
    auth_header: "",
    source_code: "",
    rag_enabled: false,
    run_multiturn: true,
    run_document_injection: true,
    run_blackbox_probes: true,
    categories: [] as string[],
    use_form_data: false,
    form_extra_fields_text: "",
  });
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<TabType>("static");

  const toggleCategory = (c: string) =>
    setForm(f => ({ ...f, categories: f.categories.includes(c) ? f.categories.filter(x => x !== c) : [...f.categories, c] }));

  const runScan = async () => {
    setLoading(true);
    setReport(null);
    try {
      let form_extra_fields = null;
      if (form.use_form_data && form.form_extra_fields_text.trim()) {
        try {
          form_extra_fields = JSON.parse(form.form_extra_fields_text);
        } catch {
          alert("Form Extra Fields must be valid JSON, e.g. {\"defender\": \"baseline\"}");
          setLoading(false);
          return;
        }
      }
      const { form_extra_fields_text, ...rest } = form;
      const payload = { ...rest, form_extra_fields };
      const r = await agentSecAPI.runScan(payload);
      setReport(r.data.report);
      setActiveTab("static");
    } catch (e: any) {
      alert("Scan failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setLoading(false);
    }
  };

  const scoreColor = !report ? "" :
    report.security_score >= 80 ? "text-green-400" :
    report.security_score >= 60 ? "text-yellow-400" : "text-red-400";

  const TABS: { key: TabType; label: string; count?: number }[] = report ? [
    { key: "static", label: `Static (${report.static_findings?.length ?? 0})` },
    { key: "attacks", label: `Attacks (${report.statistics?.successful_attacks ?? 0} found)` },
    { key: "multiturn", label: `Multi-Turn (${report.multiturn_attacks?.successful_attacks ?? 0} found)` },
    { key: "docinjection", label: `Doc Injection (${report.document_injection?.successful_attacks ?? 0} found)` },
    { key: "blackbox", label: `Black-Box (${report.blackbox_probes?.findings?.length ?? 0} findings)` },
    { key: "fixes", label: `Fixes (${report.top_fixes?.length ?? 0})` },
  ] : [];

  return (
    <div className="min-h-screen">
      <nav className="border-b border-border bg-panel px-8 py-4 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-white transition-colors"><ChevronLeft size={20} /></Link>
      
        <span className="font-semibold">Agent Scan</span>
        <span className="text-xs text-gray-500">— Pre-deploy security analysis</span>
      </nav>

      <div className="max-w-6xl mx-auto px-8 py-8 grid grid-cols-2 gap-8">
        {/* ── Config Form ── */}
        <div className="space-y-4">
          <h2 className="text-xs text-gray-500 uppercase tracking-widest">Scan Configuration</h2>

          {[
            { label: "Agent ID *", key: "agent_id", mono: true, ph: "my-agent-001" },
            { label: "Agent Name *", key: "agent_name", ph: "My Customer Support Agent" },
            { label: "Endpoint URL", key: "endpoint_url", ph: "https://my-agent.com/chat" },
            { label: "Auth Header", key: "auth_header", ph: "Bearer your-token" },
          ].map(({ label, key, mono, ph }) => (
            <div key={key}>
              <label className="block text-xs text-gray-500 mb-1.5">{label}</label>
              <input
                value={(form as any)[key]}
                onChange={e => setForm(f => ({ ...f, [key]: e.target.value }))}
                placeholder={ph}
                className={`w-full bg-panel border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:border-accent ${mono ? "font-mono" : ""}`}
              />
            </div>
          ))}

          <div>
            <label className="block text-xs text-gray-500 mb-1.5">System Prompt *</label>
            <textarea
              value={form.system_prompt}
              onChange={e => setForm(f => ({ ...f, system_prompt: e.target.value }))}
              placeholder="You are a helpful customer support assistant for Acme Corp..."
              rows={4}
              className="w-full bg-panel border border-border rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent resize-none"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1.5">Source Code (optional)</label>
            <textarea
              value={form.source_code}
              onChange={e => setForm(f => ({ ...f, source_code: e.target.value }))}
              placeholder="Paste your agent's Python code here for static analysis..."
              rows={3}
              className="w-full bg-panel border border-border rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent resize-none"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-2">Attack Categories (empty = all)</label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map(c => (
                <button key={c} onClick={() => toggleCategory(c)}
                  className={`text-xs px-2.5 py-1 rounded-full border transition-colors font-mono ${form.categories.includes(c) ? "bg-accent/20 border-accent text-accent" : "border-border text-gray-500 hover:border-gray-500"}`}>
                  {c}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            {([
              { key: "rag_enabled", label: "RAG enabled (adds memory poisoning tests)" },
              { key: "run_multiturn", label: "Run multi-turn manipulation chains" },
              { key: "run_document_injection", label: "Run document/indirect injection tests" },
              { key: "run_blackbox_probes", label: "Run black-box behavioral probes (no source code needed)" },
              { key: "use_form_data", label: "Send attacks as form-data instead of JSON (e.g. for Gandalf-style APIs)" },
            ] as { key: keyof typeof form; label: string }[]).map(({ key, label }) => (
              <div key={key} className="flex items-center gap-3">
                <button onClick={() => setForm(f => ({ ...f, [key]: !f[key] }))}
                  className={`w-10 h-5 rounded-full transition-colors relative ${(form as any)[key] ? "bg-accent" : "bg-border"}`}>
                  <div className={`absolute top-0.5 w-4 h-4 rounded-full bg-white transition-all ${(form as any)[key] ? "left-5" : "left-0.5"}`} />
                </button>
                <span className="text-sm text-gray-400">{label}</span>
              </div>
            ))}
          </div>

          {form.use_form_data && (
            <div>
              <label className="block text-xs text-gray-500 mb-1.5">Form Extra Fields (JSON)</label>
              <textarea
                value={form.form_extra_fields_text}
                onChange={e => setForm(f => ({ ...f, form_extra_fields_text: e.target.value }))}
                placeholder='{"defender": "baseline"}'
                rows={2}
                className="w-full bg-panel border border-border rounded-lg px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent resize-none"
              />
            </div>
          )}

          <button onClick={runScan} disabled={loading || !form.agent_id || !form.agent_name}
            className="w-full bg-accent hover:bg-accent-dim disabled:opacity-50 disabled:cursor-not-allowed py-3 rounded-xl text-sm font-semibold transition-colors flex items-center justify-center gap-2">
            {loading
              ? <><div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" /> Running Full Scan...</>
              : "Run Security Scan"}
          </button>
        </div>

        {/* ── Results ── */}
        <div>
          {!report && !loading && (
            <div className="flex flex-col items-center justify-center h-full text-center py-20 text-gray-600">
              {/* <Zap size={40} className="mb-3 text-gray-700" /> */}
              <p className="text-sm">Configure your agent and run a scan</p>
              <p className="text-xs mt-1">Includes single-shot, multi-turn, and document injection tests</p>
            </div>
          )}

          {loading && (
            <div className="flex flex-col items-center justify-center h-full py-20">
              <div className="animate-spin w-10 h-10 border-2 border-accent border-t-transparent rounded-full mb-4" />
              <p className="text-sm text-gray-400">Running full scan...</p>
              <p className="text-xs text-gray-600 mt-1">Single-shot + multi-turn + doc injection — may take 2-4 min</p>
            </div>
          )}

          {report && (
            <div className="space-y-4">
              {/* Score Summary */}
              <div className="bg-panel border border-border rounded-xl p-5">
                <div className="flex items-center justify-between mb-1">
                  <div>
                    <h3 className="font-semibold">{report.agent_name}</h3>
                    {!report.dynamic_testing_performed && (
                      <p className="text-xs text-yellow-400 mt-0.5">Static analysis only — no endpoint tested</p>
                    )}
                  </div>
                  <span className={`text-4xl font-bold font-mono ${scoreColor}`}>
                    {report.security_score}<span className="text-base text-gray-600">/100</span>
                  </span>
                </div>
                <p className="text-sm text-gray-400 mb-3">{report.executive_summary}</p>
                <div className="grid grid-cols-4 gap-2 text-center">
                  {[
                    { label: "Static Findings", val: report.statistics?.static_findings },
                    { label: "Single-Shot", val: `${report.statistics?.failed_attacks ?? 0}/${report.statistics?.total_attacks ?? 0}` },
                    { label: "Multi-Turn", val: `${(report.multiturn_attacks?.total_chains ?? 0) - (report.multiturn_attacks?.successful_attacks ?? 0)}/${report.multiturn_attacks?.total_chains ?? 0}` },
                    { label: "Doc Injection", val: `${(report.document_injection?.total_tests ?? 0) - (report.document_injection?.successful_attacks ?? 0)}/${report.document_injection?.total_tests ?? 0}` },
                  ].map(({ label, val }) => (
                    <div key={label} className="bg-surface rounded-lg p-2">
                      <div className="text-base font-bold font-mono text-white">{val}</div>
                      <div className="text-xs text-gray-500 mt-0.5 leading-tight">{label}</div>
                    </div>
                  ))}
                </div>
                {/* Attack generation transparency */}
                {report.attack_generation && !report.attack_generation.contextual_generation_succeeded && (
                  <div className="mt-3 bg-yellow-500/5 border border-yellow-500/20 rounded p-2">
                    <p className="text-xs text-yellow-400">
                      Adaptive attack generation fell back to base payloads: {report.attack_generation.failure_reason}
                    </p>
                  </div>
                )}
                {report.execution_errors?.count > 0 && (
                  <div className="mt-2 bg-gray-500/5 border border-gray-500/20 rounded p-2">
                    <p className="text-xs text-gray-500">{report.execution_errors.note}</p>
                  </div>
                )}
              </div>

              {/* Tabs */}
              <div className="flex gap-1 bg-panel border border-border rounded-lg p-1 flex-wrap">
                {TABS.map(tab => (
                  <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                    className={`flex-1 py-1.5 rounded text-xs font-medium transition-colors ${activeTab === tab.key ? "bg-accent text-white" : "text-gray-500 hover:text-white"}`}>
                    {tab.label}
                  </button>
                ))}
              </div>

              <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                {activeTab === "static" && report.static_findings?.map((f: any, i: number) => <StaticFinding key={i} f={f} />)}

                {activeTab === "attacks" && report.successful_attacks?.map((r: any, i: number) => <AttackCard key={i} r={r} />)}
                {activeTab === "attacks" && (!report.successful_attacks || report.successful_attacks.length === 0) && (
                  <div className="text-center py-10 text-green-400 text-sm">No single-shot attacks succeeded</div>
                )}

                {activeTab === "multiturn" && report.multiturn_attacks?.results?.map((r: any, i: number) => <MultiturnCard key={i} r={r} />)}
                {activeTab === "multiturn" && !report.multiturn_attacks?.results?.length && (
                  <div className="text-center py-10 text-gray-500 text-sm">Multi-turn results not available (requires endpoint_url)</div>
                )}

                {activeTab === "docinjection" && report.document_injection?.results?.map((r: any, i: number) => <DocInjectionCard key={i} r={r} />)}
                {activeTab === "docinjection" && !report.document_injection?.results?.length && (
                  <div className="text-center py-10 text-gray-500 text-sm">Document injection results not available (requires endpoint_url)</div>
                )}

                {activeTab === "blackbox" && (report.blackbox_probes?.findings?.length > 0
                  ? report.blackbox_probes.findings.map((f: any, i: number) => <BlackboxCard key={i} f={f} />)
                  : <div className="text-center py-10 text-gray-500 text-sm">No behavioral anomalies detected (requires endpoint_url)</div>
                )}

                {activeTab === "fixes" && report.top_fixes?.map((fix: any, i: number) => (
                  <div key={i} className="bg-panel border border-border rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs bg-accent/20 text-accent px-2 py-0.5 rounded-full">#{fix.priority}</span>
                      <span className="text-sm font-medium">{fix.issue}</span>
                    </div>
                    <p className="text-sm text-gray-400 mb-2">{fix.fix}</p>
                    {fix.example && <pre className="text-xs font-mono bg-surface border border-border rounded p-3 text-green-400 whitespace-pre-wrap">{fix.example}</pre>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}