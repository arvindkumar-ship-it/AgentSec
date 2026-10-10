# Security boundary repairs

Repair branch: `fix/internship-audit-20261010`. Changes are scoped to audit findings; no deployment or live provider action is included.

## Changed

Strict judge schemas reject string booleans. Unknown or failed judgements stay unmeasured; static-only scans have no invented security score. Agent ownership and Mongo reads are organisation-scoped. Platform administration requires a server-controlled allowlist. Shield checks the full normalized arguments, blocks failed outbound reviews, and enforces an iteration budget. Scan targets require an exact server-configured HTTPS allowlist with public DNS validation and pinned connections. Paid plans require a captured, organisation-bound payment for a server-issued, single-use order. Work reservations enforce daily and active-work limits and refund unsuccessful work. Policy overrides, SSO-only login, webhooks and tool rollback are explicitly unavailable. Frontend dependencies were upgraded to supported Next 16/React 19 and Tailwind 4.

## Verification

`pytest -q; cd frontend && npm ci && npm run build && npm audit`

Commands are entry points, not a claim that every live integration was executed. See the repair bundle for actual results.

## Setup and remaining evidence

Apply Alembic migrations through a6d20261012 on a backed-up development PostgreSQL instance before serving requests. Production settings require a random 32+ character SECRET_KEY. Set PLATFORM_ADMIN_EMAILS explicitly. SCAN_ALLOWED_ORIGINS is empty by default: only allow HTTPS origins you own or have permission to assess. Quota leases expire after 15 minutes; jobs are bounded to 10 minutes. A process crash can leave a daily reservation consumed; reconcile it manually rather than replaying unknown effects. Offline tests use SQLite and replace paid providers: PostgreSQL row-lock races, Mongo integration, real gateway calls, model judging accuracy and multi-instance Shield state remain unverified. Redis/LLM output cannot establish that an agent is secure. Existing legacy SSO secrets require rotation/removal. Per-process Shield sessions require sticky routing or a shared-state implementation before scaling.
