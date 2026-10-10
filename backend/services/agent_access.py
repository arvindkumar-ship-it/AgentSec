from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.sql_models import AgentOwnership, ScanOwnership


async def ensure_agent_access(pg_db, mongo_db, agent_id, user, *, create=False):
    if not agent_id or len(agent_id) > 200:
        raise HTTPException(422, "Agent ID must contain 1–200 characters")
    owner = await pg_db.get(AgentOwnership, agent_id)
    if owner is None:
        # Never let a caller claim legacy data belonging to another tenant.
        legacy = await mongo_db.scan_reports.find({"agent_id": agent_id}, {"scan_id": 1}).to_list(length=None)
        ids = {doc.get("scan_id") for doc in legacy}
        links = (await pg_db.execute(select(ScanOwnership).where(ScanOwnership.mongo_scan_id.in_(ids)))).scalars().all() if ids else []
        if legacy and (None in ids or {link.mongo_scan_id for link in links} != ids or any(link.org_id != user.org_id for link in links)):
            raise HTTPException(409, "Legacy agent ownership requires administrator migration")
        for collection in (mongo_db.shield_logs, mongo_db.checkpoints, mongo_db.eval_results):
            if await collection.find_one({"agent_id": agent_id, "org_id": {"$ne": str(user.org_id)}}):
                raise HTTPException(409, "Legacy agent ownership requires administrator migration")
        if not create and not legacy:
            raise HTTPException(404, "Register this agent first")
        owner = AgentOwnership(agent_id=agent_id, org_id=user.org_id, user_id=user.id)
        pg_db.add(owner)
        try:
            await pg_db.commit()
        except IntegrityError:
            await pg_db.rollback()
            owner = await pg_db.get(AgentOwnership, agent_id)
    if owner is None or owner.org_id != user.org_id:
        raise HTTPException(403, "Access denied to this agent")
    return owner
