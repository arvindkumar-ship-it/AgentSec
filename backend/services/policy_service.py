from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from models.policy_models import OrgPolicyOverride

POLICY_DEFAULTS = {
    "prompt_injection_strictness": "medium",
    "risk_thresholds": {"critical": 90, "high": 70, "medium": 40, "low": 0},
    "allowed_models": ["groq", "gemini"],
}


async def get_effective_policies(db: AsyncSession, org_id) -> dict:
    result = await db.execute(select(OrgPolicyOverride).where(OrgPolicyOverride.org_id == org_id))
    overrides = {row.key: row.value for row in result.scalars().all()}

    effective = {}
    for key, default_val in POLICY_DEFAULTS.items():
        effective[key] = {
            "value": overrides.get(key, default_val),
            "is_override": key in overrides,
        }
    return effective


async def get_policy_value(db: AsyncSession, org_id, key: str):
    if key not in POLICY_DEFAULTS:
        raise ValueError(f"Unknown policy key: {key}")
    result = await db.execute(select(OrgPolicyOverride).where(OrgPolicyOverride.org_id == org_id, OrgPolicyOverride.key == key))
    row = result.scalar_one_or_none()
    return row.value if row else POLICY_DEFAULTS[key]


async def set_tenant_policy(db: AsyncSession, org_id, key: str, value, updated_by):
    if key not in POLICY_DEFAULTS:
        raise ValueError(f"Unknown policy key: {key}")
    result = await db.execute(select(OrgPolicyOverride).where(OrgPolicyOverride.org_id == org_id, OrgPolicyOverride.key == key))
    row = result.scalar_one_or_none()
    if row:
        row.value = value
        row.updated_by = updated_by
    else:
        db.add(OrgPolicyOverride(id=uuid.uuid4(), org_id=org_id, key=key, value=value, updated_by=updated_by))
    await db.commit()
# async def seed_plans(db: AsyncSession):
#     for name, tier in [("free", PlanTierEnum.free), ("pro", PlanTierEnum.pro), ("enterprise", PlanTierEnum.enterprise)]:
#         result = await db.execute(select(Plan).where(Plan.name == name))
#         if not result.scalar_one_or_none():
#             db.add(Plan(id=uuid.uuid4(), name=name, tier=tier, monthly_price=None, description=f"{name} tier"))
#     await db.commit()