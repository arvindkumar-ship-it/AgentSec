import type { ScanRun } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

/** GET /agentsec/scans?agent_id=... — list of scan runs for an agent */
export async function getScansForAgent(agentId: string): Promise<ScanRun[]> {
  const res = await fetch(`${API_BASE}/agentsec/scans?agent_id=${encodeURIComponent(agentId)}`, {
    cache: "no-store",
  });
  if (!res.ok) return [];
  return res.json();
}