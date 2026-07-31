# from fastapi import APIRouter, HTTPException
# from models.schemas import ScanRequest
# from layers.scan import run_full_scan
# from core.db import get_db

# router = APIRouter(prefix="/scan", tags=["Agent Scan"])


# @router.post("/run")
# async def trigger_scan(request: ScanRequest):
#     """
#     Run a full security scan on your agent.
#     If endpoint_url provided: static analysis + dynamic attack testing.
#     If no endpoint_url: static analysis only.
#     """
#     try:
#         report = await run_full_scan(
#             agent_id=request.agent_id,
#             scan_config=request.model_dump()
#         )
#         return {"status": "completed", "report": report}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/reports/{agent_id}")
# async def get_scan_reports(agent_id: str, limit: int = 10):
#     """Get all scan reports for an agent."""
#     db = get_db()
#     cursor = db.scan_reports.find(
#         {"agent_id": agent_id},
#         {"raw_results": 0}  # Exclude large field
#     ).sort("generated_at", -1).limit(limit)

#     reports = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])
#         reports.append(doc)
#     return {"agent_id": agent_id, "reports": reports}


# @router.get("/reports/{agent_id}/{scan_id}")
# async def get_single_report(agent_id: str, scan_id: str):
#     """Get a specific scan report."""
#     db = get_db()
#     doc = await db.scan_reports.find_one({"agent_id": agent_id, "scan_id": scan_id})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Report not found")
#     doc["_id"] = str(doc["_id"])
#     return doc


#---------------------------------------------------------------------------------







# from fastapi import APIRouter, HTTPException
# from models.schemas import ScanRequest
# from layers.scan import run_full_scan
# from core.db import get_db

# router = APIRouter(prefix="/scan", tags=["Agent Scan"])


# @router.post("/run")
# async def trigger_scan(request: ScanRequest):
#     """
#     Run a full security scan on your agent.
#     Includes: static analysis, single-shot attacks, multi-turn chains,
#     document/indirect injection tests.
#     If endpoint_url is empty: static analysis only.
#     """
#     try:
#         config = request.model_dump()
#         report = await run_full_scan(
#             agent_id=request.agent_id,
#             scan_config=config,
#         )
#         return {"status": "completed", "report": report}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/reports/{agent_id}")
# async def get_scan_reports(agent_id: str, limit: int = 10):
#     """Get all scan reports for an agent."""
#     db = get_db()
#     cursor = db.scan_reports.find(
#         {"agent_id": agent_id},
#         {"raw_results": 0, "multiturn_attacks.results.transcript": 0}
#     ).sort("generated_at", -1).limit(limit)

#     reports = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])
#         reports.append(doc)
#     return {"agent_id": agent_id, "reports": reports}


# @router.get("/reports/{agent_id}/{scan_id}")
# async def get_single_report(agent_id: str, scan_id: str):
#     """Get a specific scan report including full transcript."""
#     db = get_db()
#     doc = await db.scan_reports.find_one({"agent_id": agent_id, "scan_id": scan_id})
#     if not doc:
#         raise HTTPException(status_code=404, detail="Report not found")
#     doc["_id"] = str(doc["_id"])
#     return doc



# from fastapi import APIRouter

# # separate router, NO prefix — so paths stay exactly /agentsec/scans
# agentsec_scan_router = APIRouter()

# @agentsec_scan_router.get("/agentsec/scans")
# async def list_scans_for_agent(agent_id: str):
#     db = get_db()
#     cursor = db.scan_reports.find({"agent_id": agent_id}).sort("generated_at", -1)
#     docs = await cursor.to_list(length=100)

#     return [
#         {
#             "id": d.get("scan_id"),
#             "agent_id": d.get("agent_id"),
#             "agent_name": d.get("agent_name"),
#             "generated_at": d.get("generated_at"),
#             "risk_level": d.get("risk_level"),
#             "security_score": d.get("security_score"),
#             "dynamic_testing_performed": d.get("dynamic_testing_performed", False),
#             "status": d.get("status", "completed"),
#         }
#         for d in docs
#     ]


#-----------------------------------------------------------------------------

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import ScanRequest
from layers.scan import run_full_scan
from core.db import get_db
from fastapi import Request
from core.limiter import limiter
from services.quota_service import check_scan_quota, release_scan_usage

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from services.ownership_service import create_ownership, get_org_scan_ids, user_owns_scan, get_org_agent_ids

router = APIRouter(prefix="/scan", tags=["Agent Scan"])


@router.post("/run")
@limiter.limit("5/minute")
async def trigger_scan(
    request: Request,
    scan_request: ScanRequest,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
    _: None = Depends(check_scan_quota),
):
    """
    Run a full security scan on your agent.
    """
    # Idempotency: same user, same agent, last 30 seconds ke andar
    # duplicate scan request ko ignore karo
    from datetime import datetime, timedelta
    from sqlalchemy import select
    from models.sql_models import ScanOwnership

    recent_cutoff = datetime.utcnow() - timedelta(seconds=30)
    recent = await pg_db.execute(
        select(ScanOwnership).where(
            ScanOwnership.user_id == current_user.id,
            ScanOwnership.created_at >= recent_cutoff,
        ).order_by(ScanOwnership.created_at.desc()).limit(1)
    )
    recent_record = recent.scalar_one_or_none()
    if recent_record:
        db = get_db()
        existing_doc = await db.scan_reports.find_one(
            {"scan_id": recent_record.mongo_scan_id, "agent_id": scan_request.agent_id}
        )
        if existing_doc:
            existing_doc["_id"] = str(existing_doc["_id"])
            return {"status": "completed", "report": existing_doc, "note": "Duplicate request detected — returned existing scan."}

    try:
        config = scan_request.model_dump()
        report = await run_full_scan(
            agent_id=scan_request.agent_id,
            scan_config=config,
        )

        scan_id = report.get("scan_id")
        if scan_id:
            await create_ownership(
                db=pg_db,
                mongo_scan_id=scan_id,
                org_id=current_user.org_id,
                user_id=current_user.id,
            )
            # increment_usage call REMOVED — quota already reserved atomically in check_scan_quota

        return {"status": "completed", "report": report}
    except Exception as e:
        await release_scan_usage(db=pg_db, org_id=current_user.org_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{agent_id}")
async def get_scan_reports(
    agent_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    """Get all scan reports for an agent. Sirf apne org ke reports."""
    db = get_db()
    org_scan_ids = await get_org_scan_ids(pg_db, current_user.org_id)

    cursor = db.scan_reports.find(
        {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}},
        {"raw_results": 0, "multiturn_attacks.results.transcript": 0}
    ).sort("generated_at", -1).limit(limit)

    reports = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        reports.append(doc)
    return {"agent_id": agent_id, "reports": reports}


@router.get("/reports/{agent_id}/{scan_id}")
async def get_single_report(
    agent_id: str,
    scan_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    """Get a specific scan report including full transcript. Ownership check hota hai."""
    if not await user_owns_scan(pg_db, scan_id, current_user.org_id):
        raise HTTPException(status_code=403, detail="Access denied to this scan")

    db = get_db()
    doc = await db.scan_reports.find_one({"agent_id": agent_id, "scan_id": scan_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    doc["_id"] = str(doc["_id"])
    return doc


agentsec_scan_router = APIRouter()

@agentsec_scan_router.get("/agentsec/scans")
async def list_scans_for_agent(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_scan_ids = await get_org_scan_ids(pg_db, current_user.org_id)

    cursor = db.scan_reports.find(
        {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}}
    ).sort("generated_at", -1)
    docs = await cursor.to_list(length=100)

    return [
        {
            "id": d.get("scan_id"),
            "agent_id": d.get("agent_id"),
            "agent_name": d.get("agent_name"),
            "generated_at": d.get("generated_at"),
            "risk_level": d.get("risk_level"),
            "security_score": d.get("security_score"),
            "dynamic_testing_performed": d.get("dynamic_testing_performed", False),
            "status": d.get("status", "completed"),
        }
        for d in docs
    ]