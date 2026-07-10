import type { EvalResult } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

/** GET /agentsec/evals?agent_id=...&scan_id=... — latest eval tied to a scan, or null */
export async function getEvalForScan(agentId: string, scanId: string): Promise<EvalResult | null> {
  const res = await fetch(
    `${API_BASE}/agentsec/evals?agent_id=${encodeURIComponent(agentId)}&scan_id=${encodeURIComponent(scanId)}`,
    { cache: "no-store" }
  );
  if (!res.ok) return null;
  const list: EvalResult[] = await res.json();
  return list[0] ?? null;
}

/** GET /agentsec/evals?agent_id=... — full eval history for the Evaluations tab */
export async function getEvalsForAgent(agentId: string): Promise<EvalResult[]> {
  const res = await fetch(`${API_BASE}/agentsec/evals?agent_id=${encodeURIComponent(agentId)}`, {
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}