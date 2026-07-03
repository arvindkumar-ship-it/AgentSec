import axios from "axios";

const API = axios.create({
  // baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  baseURL: typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "https://agentsec-backend.onrender.com" 
    : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"),
  timeout: 120000, // 2 min — scans can take time
});

export const agentSecAPI = {
  // ── Scan ─────────────────────────────────────────────────
  runScan: (data: any) => API.post("/scan/run", data),
  getScanReports: (agentId: string) => API.get(`/scan/reports/${agentId}`),
  getScanReport: (agentId: string, scanId: string) =>
    API.get(`/scan/reports/${agentId}/${scanId}`),

  // ── Shield ────────────────────────────────────────────────
  registerShield: (data: any) => API.post("/shield/register", data),
  getShieldLogs: (agentId: string, hours = 24) =>
    API.get(`/shield/logs/${agentId}?hours=${hours}`),
  getShieldStats: (agentId: string) => API.get(`/shield/stats/${agentId}`),
  getCheckpoints: (agentId: string) => API.get(`/shield/checkpoints/${agentId}`),
  revertCheckpoint: (agentId: string, checkpointId: string) =>
    API.post("/shield/revert", { agent_id: agentId, checkpoint_id: checkpointId }),

  // ── Eval ──────────────────────────────────────────────────
  runEval: (data: any) => API.post("/eval/run", data),
  getEvalTrend: (agentId: string, days = 30) =>
    API.get(`/eval/trend/${agentId}?days=${days}`),
  checkRegression: (agentId: string) => API.get(`/eval/regression/${agentId}`),
  getEvalHistory: (agentId: string) => API.get(`/eval/history/${agentId}`),

  // ── Dashboard ─────────────────────────────────────────────
  getDashboard: (agentId: string) => API.get(`/dashboard/summary/${agentId}`),
  listAgents: () => API.get("/dashboard/agents"),
};

export default agentSecAPI;
