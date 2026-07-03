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







from fastapi import APIRouter, HTTPException
from models.schemas import ScanRequest
from layers.scan import run_full_scan
from core.db import get_db

router = APIRouter(prefix="/scan", tags=["Agent Scan"])


@router.post("/run")
async def trigger_scan(request: ScanRequest):
    """
    Run a full security scan on your agent.
    Includes: static analysis, single-shot attacks, multi-turn chains,
    document/indirect injection tests.
    If endpoint_url is empty: static analysis only.
    """
    try:
        config = request.model_dump()
        report = await run_full_scan(
            agent_id=request.agent_id,
            scan_config=config,
        )
        return {"status": "completed", "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reports/{agent_id}")
async def get_scan_reports(agent_id: str, limit: int = 10):
    """Get all scan reports for an agent."""
    db = get_db()
    cursor = db.scan_reports.find(
        {"agent_id": agent_id},
        {"raw_results": 0, "multiturn_attacks.results.transcript": 0}
    ).sort("generated_at", -1).limit(limit)

    reports = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        reports.append(doc)
    return {"agent_id": agent_id, "reports": reports}


@router.get("/reports/{agent_id}/{scan_id}")
async def get_single_report(agent_id: str, scan_id: str):
    """Get a specific scan report including full transcript."""
    db = get_db()
    doc = await db.scan_reports.find_one({"agent_id": agent_id, "scan_id": scan_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Report not found")
    doc["_id"] = str(doc["_id"])
    return doc
