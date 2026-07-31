# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, func
# from datetime import datetime, timedelta
# from services.audit_service import write_audit
# from services.ownership_service import get_org_scan_ids
# from models.quota_models import OrganizationQuota, OrganizationUsageDaily

# from auth import get_current_user
# from models.sql_models import User, Organization, ScanOwnership
# from database import get_db as get_pg_db
# from core.db import get_db

# router = APIRouter(prefix="/admin", tags=["Admin"])


# @router.get("/stats")
# async def get_system_stats(
#     current_user: User = Depends(get_current_user),
#     pg_db: AsyncSession = Depends(get_pg_db),
# ):
#     """Internal system stats. Sirf admin role wale users access kar sakte hain."""
#     if current_user.role.value != "admin":
#         raise HTTPException(status_code=403, detail="Admin access required")

#     org_count = await pg_db.execute(select(func.count(Organization.id)))
#     user_count = await pg_db.execute(select(func.count(User.id)))
#     scan_ownership_count = await pg_db.execute(select(func.count(ScanOwnership.id)))

#     since_24h = datetime.utcnow() - timedelta(hours=24)
#     recent_scans = await pg_db.execute(
#         select(func.count(ScanOwnership.id)).where(ScanOwnership.created_at >= since_24h)
#     )

#     db = get_db()
#     total_mongo_scans = await db.scan_reports.count_documents({})
#     total_mongo_evals = await db.eval_results.count_documents({})

#     return {
#         "organizations": org_count.scalar(),
#         "users": user_count.scalar(),
#         "total_linked_scans": scan_ownership_count.scalar(),
#         "scans_last_24h": recent_scans.scalar(),
#         "total_scan_reports_mongo": total_mongo_scans,
#         "total_eval_results_mongo": total_mongo_evals,
#     }






















































from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta

from auth import get_current_user
from models.sql_models import User, Organization, ScanOwnership
from database import get_db as get_pg_db
from core.db import get_db

from services.audit_service import write_audit
from services.ownership_service import get_org_scan_ids
from models.quota_models import OrganizationQuota, OrganizationUsageDaily

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/stats")
async def get_system_stats(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    """Internal system stats. Sirf admin role wale users access kar sakte hain."""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    org_count = await pg_db.execute(select(func.count(Organization.id)))
    user_count = await pg_db.execute(select(func.count(User.id)))
    scan_ownership_count = await pg_db.execute(select(func.count(ScanOwnership.id)))

    since_24h = datetime.utcnow() - timedelta(hours=24)
    recent_scans = await pg_db.execute(
        select(func.count(ScanOwnership.id)).where(ScanOwnership.created_at >= since_24h)
    )

    db = get_db()
    total_mongo_scans = await db.scan_reports.count_documents({})
    total_mongo_evals = await db.eval_results.count_documents({})

    return {
        "organizations": org_count.scalar(),
        "users": user_count.scalar(),
        "total_linked_scans": scan_ownership_count.scalar(),
        "scans_last_24h": recent_scans.scalar(),
        "total_scan_reports_mongo": total_mongo_scans,
        "total_eval_results_mongo": total_mongo_evals,
    }


@router.get("/organizations")
async def list_organizations(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    orgs = (await pg_db.execute(select(Organization))).scalars().all()
    grid = []
    for org in orgs:
        quota = (await pg_db.execute(
            select(OrganizationQuota).where(OrganizationQuota.org_id == org.id)
        )).scalar_one_or_none()

        today_dt = datetime.combine(datetime.utcnow().date(), datetime.min.time())
        usage = (await pg_db.execute(
            select(OrganizationUsageDaily).where(
                OrganizationUsageDaily.org_id == org.id,
                OrganizationUsageDaily.date == today_dt,
            )
        )).scalar_one_or_none()

        grid.append({
            "org_id": str(org.id),
            "name": org.name,
            "state": org.state,
            "max_scans_per_day": quota.max_scans_per_day if quota else None,
            "scans_today": usage.scans_count if usage else 0,
            "evals_today": usage.eval_runs if usage else 0,
        })
    return {"organizations": grid}


@router.post("/organizations/{org_id}/suspend")
async def suspend_tenant(
    org_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    org = (await pg_db.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")

    org.state = "suspended"
    await pg_db.commit()
    await write_audit(pg_db, org_id=org.id, user_id=current_user.id, action="tenant_suspend")
    return {"status": "suspended", "org_id": org_id}


@router.post("/organizations/{org_id}/reactivate")
async def reactivate_tenant(
    org_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    org = (await pg_db.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")

    org.state = "active"
    await pg_db.commit()
    await write_audit(pg_db, org_id=org.id, user_id=current_user.id, action="tenant_reactivate")
    return {"status": "active", "org_id": org_id}


@router.post("/organizations/{org_id}/offboard")
async def offboard_tenant(
    org_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    org = (await pg_db.execute(select(Organization).where(Organization.id == org_id))).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Tenant not found")

    scan_ids = await get_org_scan_ids(pg_db, org_id)
    mongo_db = get_db()
    scan_reports = await mongo_db.scan_reports.find({"scan_id": {"$in": scan_ids}}).to_list(length=None)
    eval_results = await mongo_db.eval_results.find({"scan_id": {"$in": scan_ids}}).to_list(length=None)
    for doc in scan_reports + eval_results:
        doc["_id"] = str(doc["_id"])

    org.state = "deleted"
    await pg_db.commit()
    await write_audit(
        pg_db, org_id=org.id, user_id=current_user.id, action="tenant_offboard",
        metadata={"scan_reports_exported": len(scan_reports), "eval_results_exported": len(eval_results)}
    )
    return {
        "status": "offboarded",
        "org_id": org_id,
        "export": {"scan_reports": scan_reports, "eval_results": eval_results},
    }