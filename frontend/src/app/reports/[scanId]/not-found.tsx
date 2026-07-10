import Link from "next/link";

export default function ReportNotFound() {
  return (
    <main className="mx-auto flex max-w-5xl flex-col items-center justify-center px-6 py-24 text-center">
      <div className="text-xs uppercase tracking-widest text-gray-400">404</div>
      <h1 className="mt-2 text-2xl font-semibold text-gray-900">Scan not found</h1>
      <p className="mt-2 max-w-md text-sm text-gray-500">
        No report exists for this scan_id. Double-check the ID, or run a new scan on this agent.
      </p>
      <Link
        href="/"
        className="mt-6 rounded-md border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:border-indigo-400 hover:text-indigo-600"
      >
        Back to dashboard
      </Link>
    </main>
  );
}