// import axios from "axios";

// const API = axios.create({
//   baseURL: typeof window !== "undefined" && window.location.hostname !== "localhost"
//     ? "https://agentsec-backend.onrender.com" 
//     : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"),
//   timeout: 600000, // 10 min — full scans (attacks + multiturn + doc injection + blackbox) genuinely take time
// });

// export const agentSecAPI = {
//   // ── Scan ─────────────────────────────────────────────────
//   runScan: (data: any) => API.post("/scan/run", data),
//   getScanReports: (agentId: string) => API.get(`/scan/reports/${agentId}`),
//   getScanReport: (agentId: string, scanId: string) =>
//     API.get(`/scan/reports/${agentId}/${scanId}`),

//   // ── Shield ────────────────────────────────────────────────
//   registerShield: (data: any) => API.post("/shield/register", data),
//   getShieldLogs: (agentId: string, hours = 24) =>
//     API.get(`/shield/logs/${agentId}?hours=${hours}`),
//   getShieldStats: (agentId: string) => API.get(`/shield/stats/${agentId}`),
//   getCheckpoints: (agentId: string) => API.get(`/shield/checkpoints/${agentId}`),
//   revertCheckpoint: (agentId: string, checkpointId: string) =>
//     API.post("/shield/revert", { agent_id: agentId, checkpoint_id: checkpointId }),

//   // ── Eval ──────────────────────────────────────────────────
//   runEval: (data: any) => API.post("/eval/run", data),
//   getEvalTrend: (agentId: string, days = 30) =>
//     API.get(`/eval/trend/${agentId}?days=${days}`),
//   checkRegression: (agentId: string) => API.get(`/eval/regression/${agentId}`),
//   getEvalHistory: (agentId: string) => API.get(`/eval/history/${agentId}`),

//   // ── Dashboard ─────────────────────────────────────────────
//   getDashboard: (agentId: string) => API.get(`/dashboard/summary/${agentId}`),
//   listAgents: () => API.get("/dashboard/agents"),
// };

// export default agentSecAPI;


import axios from "axios";
import { authStorage } from "./auth";

const API = axios.create({
  baseURL: typeof window !== "undefined" && window.location.hostname !== "localhost"
    ? "https://agentsec-backend.onrender.com"
    : (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"),
  timeout: 600000,
});

API.interceptors.request.use((config) => {
  const token = authStorage.getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

API.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      authStorage.clearToken();
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const agentSecAPI = {
  // ── Auth ──────────────────────────────────────────────────
  register: (data: any) => API.post("/auth/register", data),
  login: (data: any) => API.post("/auth/login", data),
  me: () => API.get("/auth/me"),

  // ── Scan ─────────────────────────────────────────────────
  runScan: (data: any) => API.post("/scan/run", data),
  getScanReports: (agentId: string) => API.get(`/scan/reports/${agentId}`),
  getScanReport: (agentId: string, scanId: string) => API.get(`/scan/reports/${agentId}/${scanId}`),

  // ── Shield ────────────────────────────────────────────────
  registerShield: (data: any) => API.post("/shield/register", data),
  getShieldLogs: (agentId: string, hours = 24) => API.get(`/shield/logs/${agentId}?hours=${hours}`),
  getShieldStats: (agentId: string) => API.get(`/shield/stats/${agentId}`),
  getCheckpoints: (agentId: string) => API.get(`/shield/checkpoints/${agentId}`),
  revertCheckpoint: (agentId: string, checkpointId: string) => API.post("/shield/revert", { agent_id: agentId, checkpoint_id: checkpointId }),

  // ── Eval ──────────────────────────────────────────────────
  runEval: (data: any) => API.post("/eval/run", data),
  getEvalTrend: (agentId: string, days = 30) => API.get(`/eval/trend/${agentId}?days=${days}`),
  checkRegression: (agentId: string) => API.get(`/eval/regression/${agentId}`),
  getEvalHistory: (agentId: string) => API.get(`/eval/history/${agentId}`),

  // ── Dashboard ─────────────────────────────────────────────
  getDashboard: (agentId: string) => API.get(`/dashboard/summary/${agentId}`),
  listAgents: () => API.get("/dashboard/agents"),
  getUsage: () => API.get("/dashboard/usage"),

  // ── Policy Engine ─────────────────────────────────────────
  getPolicies: () => API.get("/policies"),
  updatePolicy: (key: string, value: any) => API.put(`/policies/${key}`, { value }),

  // ── Billing ───────────────────────────────────────────────
  changePlan: (planName: string) => API.post("/billing/plan-change", { plan_name: planName }),
  getSSOConfig: () => API.get("/billing/sso-config"),
  setSSOConfig: (data: any) => API.post("/billing/sso-config", data),
  createOrder: (planName: string) => API.post("/billing/create-order", { plan_name: planName }),
  verifyPayment: (data: any) => API.post("/billing/verify-payment", data),

  // ── Admin ─────────────────────────────────────────────────
  listOrganizations: () => API.get("/admin/organizations"),
  suspendOrg: (orgId: string) => API.post(`/admin/organizations/${orgId}/suspend`),
  reactivateOrg: (orgId: string) => API.post(`/admin/organizations/${orgId}/reactivate`),
  offboardOrg: (orgId: string) => API.post(`/admin/organizations/${orgId}/offboard`),

  // ── Audit ─────────────────────────────────────────────────
  getAuditLogs: (params?: any) => API.get("/audit-logs", { params }),
  exportAuditLogs: () => API.get("/audit-logs/export", { responseType: "blob" }),
};

export default agentSecAPI;