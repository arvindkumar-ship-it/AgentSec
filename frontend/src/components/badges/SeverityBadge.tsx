import type { Severity } from "@/lib/types";

const SEVERITY_STYLES: Record<Severity, { dot: string; text: string }> = {
  CRITICAL: { dot: "bg-red-500", text: "text-red-600" },
  HIGH: { dot: "bg-orange-500", text: "text-orange-600" },
  MEDIUM: { dot: "bg-yellow-500", text: "text-yellow-600" },
  LOW: { dot: "bg-green-500", text: "text-green-600" },
};

/**
 * Renders like a log-line tag: a colored status dot + uppercase label.
 * Not a solid filled pill — keeps dense tables scannable.
 */
export function SeverityBadge({ severity }: { severity: Severity }) {
  const s = SEVERITY_STYLES[severity] ?? SEVERITY_STYLES.MEDIUM;
  return (
    <span className={`inline-flex items-center gap-1.5 text-[11px] font-medium tracking-wide ${s.text}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${s.dot}`} aria-hidden />
      {severity}
    </span>
  );
}