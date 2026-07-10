// Types mirror the exact shape returned by the FastAPI backend
// (see backend/services/report_builder.py + /agentsec/reports responses)

export type Severity = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type RiskLevel = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface Verdict {
  success: boolean;
  confidence: number;
  reason: string;
  extracted_info: string | null;
  needs_review: boolean;
  agreement: string;
}

export interface Attack {
  category: string;
  severity: Severity;
  payload: string;
  verdict: Verdict;
}

export interface RawResult extends Attack {
  description: string;
  agent_response: string;
  execution_failed: boolean;
}

export interface StaticFinding {
  type: string;
  name: string;
  severity: Severity;
  confidence: string;
  fix: string;
}

export interface TopFix {
  priority: number;
  issue: string;
  fix: string;
  example: string;
}

export interface Statistics {
  total_attacks: number;
  successful_attacks: number;
  failed_attacks: number;
  needs_review_attacks: number;
  pass_rate: string;
  static_findings: number;
  critical_count: number;
  high_count: number;
  total_attacks_including_multiturn: number;
  total_successful_including_multiturn: number;
}

export interface AttackGeneration {
  base_payload_count: number;
  contextual_generation_attempted: boolean;
  contextual_generation_succeeded: boolean;
  contextual_payload_count: number;
  contextual_payloads_rejected: number;
  failure_reason: string | null;
}

export interface ExecutionErrors {
  count: number;
  details: unknown[];
  note: string | null;
}

export interface MultiturnAttacks {
  total_chains: number;
  successful_attacks: number;
  results: unknown[];
}

export interface DocumentInjection {
  total_tests: number;
  successful_attacks: number;
  results: unknown[];
}

export interface ScanReport {
  agent_name: string;
  agent_id: string;
  scan_id: string;
  scan_type: string;
  generated_at: string;
  dynamic_testing_performed: boolean;
  security_score: number;
  risk_level: RiskLevel;
  executive_summary: string;
  statistics: Statistics;
  static_findings: StaticFinding[];
  successful_attacks: Attack[];
  needs_review_attacks: Attack[];
  top_fixes: TopFix[];
  raw_results: RawResult[];
  attack_generation: AttackGeneration;
  execution_errors: ExecutionErrors;
  blackbox_probes: Record<string, unknown>;
  multiturn_attacks: MultiturnAttacks;
  document_injection: DocumentInjection;
}

export interface ScanReportResponse {
  status: string;
  report: ScanReport;
}

export interface CategoryBreakdownEntry {
  total: number;
  passed: number;
  failed: number;
}

export interface EvalResult {
  eval_id?: string;
  agent_id: string;
  scan_id: string;
  run_at: string;
  pass_rate: number;
  total_tests: number;
  successful_attacks: number;
  execution_errors: number;
  category_breakdown: Record<string, CategoryBreakdownEntry>;
  note: string | null;
}

export interface ScanRun {
  id: string;
  agent_id: string;
  agent_name: string;
  generated_at: string;
  risk_level: RiskLevel;
  security_score: number;
  dynamic_testing_performed: boolean;
  status: string;
}