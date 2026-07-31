import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.sql_models import ScanOwnership


async def create_ownership(db: AsyncSession, mongo_scan_id: str, org_id, user_id):
    record = ScanOwnership(
        id=uuid.uuid4(),
        mongo_scan_id=mongo_scan_id,
        org_id=org_id,
        user_id=user_id,
    )
    db.add(record)
    await db.commit()
    return record


async def get_org_scan_ids(db: AsyncSession, org_id) -> list[str]:
    result = await db.execute(
        select(ScanOwnership.mongo_scan_id).where(ScanOwnership.org_id == org_id)
    )
    return [row[0] for row in result.all()]


async def user_owns_scan(db: AsyncSession, mongo_scan_id: str, org_id) -> bool:
    result = await db.execute(
        select(ScanOwnership).where(
            ScanOwnership.mongo_scan_id == mongo_scan_id,
            ScanOwnership.org_id == org_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def get_org_agent_ids(db: AsyncSession, mongo_db, org_id) -> set[str]:
    scan_ids = await get_org_scan_ids(db, org_id)
    if not scan_ids:
        return set()
    cursor = mongo_db.scan_reports.find(
        {"scan_id": {"$in": scan_ids}}, {"agent_id": 1, "_id": 0}
    )
    agent_ids = set()
    async for doc in cursor:
        if doc.get("agent_id"):
            agent_ids.add(doc["agent_id"])
    return agent_ids