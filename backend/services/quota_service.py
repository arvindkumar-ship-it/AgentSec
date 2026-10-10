import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from sqlalchemy import select, text, update, delete, func
from sqlalchemy.exc import IntegrityError
from types import SimpleNamespace
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from models.quota_models import Plan, PlanTierEnum, OrganizationPlan, OrganizationQuota, OrganizationUsageDaily, WorkReservation

FREE_PLAN_DEFAULTS = {
    "max_scans_per_day": 5,
    "max_evals_per_day": 5,
    "max_concurrent_scans": 2,
    "max_storage_mb": 500,
    "max_users": 3,
    "max_targets": 5,
}


async def _get_or_create_free_plan(db: AsyncSession) -> Plan:
    result = await db.execute(select(Plan).where(Plan.name == "free"))
    plan = result.scalar_one_or_none()
    if plan:
        return plan
    plan = Plan(id=uuid.uuid4(), name="free", tier=PlanTierEnum.free, monthly_price=None, description="Default free tier")
    db.add(plan)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        plan = (await db.execute(select(Plan).where(Plan.name == "free"))).scalar_one()
    await db.refresh(plan)
    return plan


async def get_or_create_org_quota(db: AsyncSession, org_id) -> OrganizationQuota:
    result = await db.execute(select(OrganizationQuota).where(OrganizationQuota.org_id == org_id))
    quota = result.scalar_one_or_none()
    if quota:
        return quota

    plan = await _get_or_create_free_plan(db)

    existing_link = await db.execute(select(OrganizationPlan).where(OrganizationPlan.org_id == org_id))
    if not existing_link.scalar_one_or_none():
        db.add(OrganizationPlan(id=uuid.uuid4(), org_id=org_id, plan_id=plan.id))

    quota = OrganizationQuota(id=uuid.uuid4(), org_id=org_id, plan_id=plan.id, **FREE_PLAN_DEFAULTS)
    db.add(quota)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        quota = (await db.execute(select(OrganizationQuota).where(OrganizationQuota.org_id == org_id))).scalar_one()
    await db.refresh(quota)
    return quota


async def get_or_create_today_usage(db: AsyncSession, org_id) -> OrganizationUsageDaily:
    today_dt = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    result = await db.execute(
        select(OrganizationUsageDaily).where(
            OrganizationUsageDaily.org_id == org_id,
            OrganizationUsageDaily.date == today_dt,
        )
    )
    usage = result.scalar_one_or_none()
    if usage:
        return usage
    usage = OrganizationUsageDaily(id=uuid.uuid4(), org_id=org_id, date=today_dt)
    db.add(usage)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        usage = (await db.execute(select(OrganizationUsageDaily).where(OrganizationUsageDaily.org_id == org_id, OrganizationUsageDaily.date == today_dt))).scalar_one()
    await db.refresh(usage)
    return usage


async def increment_usage(db: AsyncSession, org_id, field: str):
    """Generic non-quota-gated counter increment (e.g. api_calls, errors_count). NOT used for scans_count/eval_runs — those are atomically reserved below."""
    usage = await get_or_create_today_usage(db, org_id)
    setattr(usage, field, getattr(usage, field) + 1)
    await db.commit()


async def _check_org_active(db: AsyncSession, org_id):
    from models.sql_models import Organization
    result = await db.execute(select(Organization).where(Organization.id == org_id))
    org = result.scalar_one_or_none()
    if org is None or org.state != "active":
        raise HTTPException(status_code=403, detail="Tenant suspended, contact support.")


# ---------------------------------------------------------------------------
# Atomic reserve/release — closes TOCTOU race between check and increment.
# Single UPDATE does check + increment in one DB round trip; Postgres row
# lock serializes concurrent callers so two parallel requests can't both
# pass when only 1 slot is left.
# ---------------------------------------------------------------------------

async def _reserve_daily_usage(db: AsyncSession, org_id, field: str, limit_field: str) -> bool:
    today_dt = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    query = text(f"""
        UPDATE organization_usage_daily
        SET {field} = {field} + 1
        WHERE org_id = :org_id
          AND date = :today
          AND {field} < (
              SELECT {limit_field} FROM organization_quotas WHERE org_id = :org_id
          )
        RETURNING id
    """)
    result = await db.execute(query, {"org_id": org_id, "today": today_dt})
    row = result.first()
    await db.commit()
    return row is not None


async def _release_daily_usage(db: AsyncSession, org_id, field: str):
    """Called only when the scan/eval fails AFTER quota was reserved — gives the slot back."""
    today_dt = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    query = text(f"""
        UPDATE organization_usage_daily
        SET {field} = GREATEST({field} - 1, 0)
        WHERE org_id = :org_id AND date = :today
    """)
    await db.execute(query, {"org_id": org_id, "today": today_dt})
    await db.commit()


async def release_scan_usage(db: AsyncSession, org_id):
    await _release_daily_usage(db, org_id, "scans_count")


async def release_eval_usage(db: AsyncSession, org_id):
    await _release_daily_usage(db, org_id, "eval_runs")


class WorkLease:
    def __init__(self, db, reservation):
        self.db = db
        self.reservation = SimpleNamespace(id=reservation.id, org_id=reservation.org_id, field=reservation.field, date=reservation.date)
        self.completed = False

    def complete(self):
        self.completed = True

    async def close(self):
        row = self.reservation
        removed = (await self.db.execute(delete(WorkReservation).where(WorkReservation.id == row.id).returning(WorkReservation.id))).first()
        if removed and not self.completed:
            column = getattr(OrganizationUsageDaily, row.field)
            await self.db.execute(update(OrganizationUsageDaily).where(OrganizationUsageDaily.org_id == row.org_id, OrganizationUsageDaily.date == row.date, column > 0).values({row.field: column - 1}))
        await self.db.commit()


async def _reserve_work(db, org_id, field, limit_field):
    await _check_org_active(db, org_id)
    await get_or_create_org_quota(db, org_id)
    await get_or_create_today_usage(db, org_id)
    # All reservations for an organisation serialize on its quota row in PostgreSQL.
    quota = (await db.execute(select(OrganizationQuota).where(OrganizationQuota.org_id == org_id).with_for_update())).scalar_one()
    now = datetime.utcnow()
    active = (await db.execute(select(func.count()).select_from(WorkReservation).where(WorkReservation.org_id == org_id, WorkReservation.expires_at > now))).scalar_one()
    if active >= quota.max_concurrent_scans:
        await db.rollback()
        raise HTTPException(429, "Concurrent work quota exceeded")
    day = datetime.combine(now.date(), datetime.min.time())
    column = getattr(OrganizationUsageDaily, field)
    reserved = (await db.execute(update(OrganizationUsageDaily).where(OrganizationUsageDaily.org_id == org_id, OrganizationUsageDaily.date == day, column < getattr(quota, limit_field)).values({field: column + 1}).returning(OrganizationUsageDaily.id))).first()
    if not reserved:
        await db.rollback()
        raise HTTPException(429, "Daily work quota exceeded")
    row = WorkReservation(id=uuid.uuid4(), org_id=org_id, field=field, date=day, expires_at=now + timedelta(seconds=900))
    db.add(row)
    await db.commit()
    return WorkLease(db, row)


async def check_scan_quota(current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    lease = await _reserve_work(pg_db, current_user.org_id, "scans_count", "max_scans_per_day")
    try:
        yield lease
    finally:
        await lease.close()


async def check_eval_quota(current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    lease = await _reserve_work(pg_db, current_user.org_id, "eval_runs", "max_evals_per_day")
    try:
        yield lease
    finally:
        await lease.close()


# ---------------------------------------------------------------------------
# Plan seeding — called once at app startup (main.py lifespan)
# ---------------------------------------------------------------------------

async def seed_plans(db: AsyncSession):
    for name, tier in [("free", PlanTierEnum.free), ("pro", PlanTierEnum.pro), ("enterprise", PlanTierEnum.enterprise)]:
        result = await db.execute(select(Plan).where(Plan.name == name))
        if not result.scalar_one_or_none():
            db.add(Plan(id=uuid.uuid4(), name=name, tier=tier, monthly_price=None, description=f"{name} tier"))
    await db.commit()