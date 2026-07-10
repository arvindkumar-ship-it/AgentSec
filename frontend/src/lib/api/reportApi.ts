import type { ScanReportResponse } from "../types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

/** GET /agentsec/reports/{scanId} — full combined scan report */
export async function getScanReport(scanId: string): Promise<ScanReportResponse> {
  const res = await fetch(`${API_BASE}/agentsec/reports/${encodeURIComponent(scanId.trim())}/json`, {
    cache: "no-store",
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(body?.detail ?? `Failed to load report (${res.status})`, res.status);
  }
  return res.json();
}

/** Builds the direct download URL for the PDF export button */
export function getReportDownloadUrl(scanId: string): string {
  return `${API_BASE}/agentsec/reports/${encodeURIComponent(scanId.trim())}/download`;
}