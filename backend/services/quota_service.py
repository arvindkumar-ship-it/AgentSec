import uuid
from datetime import datetime
from fastapi import HTTPException, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from models.quota_models import Plan, PlanTierEnum, OrganizationPlan, OrganizationQuota, OrganizationUsageDaily

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
    await db.commit()
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
    await db.commit()
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
    await db.commit()
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
    if org and org.state == "suspended":
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


async def check_scan_quota(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_org_active(pg_db, current_user.org_id)
    await get_or_create_org_quota(pg_db, current_user.org_id)
    await get_or_create_today_usage(pg_db, current_user.org_id)

    reserved = await _reserve_daily_usage(pg_db, current_user.org_id, "scans_count", "max_scans_per_day")
    if not reserved:
        raise HTTPException(status_code=429, detail="Daily scan quota exceeded")


async def check_eval_quota(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_org_active(pg_db, current_user.org_id)
    await get_or_create_org_quota(pg_db, current_user.org_id)
    await get_or_create_today_usage(pg_db, current_user.org_id)

    reserved = await _reserve_daily_usage(pg_db, current_user.org_id, "eval_runs", "max_evals_per_day")
    if not reserved:
        raise HTTPException(status_code=429, detail="Daily eval quota exceeded")


# ---------------------------------------------------------------------------
# Plan seeding — called once at app startup (main.py lifespan)
# ---------------------------------------------------------------------------

async def seed_plans(db: AsyncSession):
    for name, tier in [("free", PlanTierEnum.free), ("pro", PlanTierEnum.pro), ("enterprise", PlanTierEnum.enterprise)]:
        result = await db.execute(select(Plan).where(Plan.name == name))
        if not result.scalar_one_or_none():
            db.add(Plan(id=uuid.uuid4(), name=name, tier=tier, monthly_price=None, description=f"{name} tier"))
    await db.commit()