# from fastapi import APIRouter, HTTPException
# from models.schemas import EvalRequest
# from layers.eval_layer import run_eval, get_eval_trend, detect_regression
# from core.db import get_db

# router = APIRouter(prefix="/eval", tags=["Agent Eval"])


# @router.post("/run")
# async def trigger_eval(request: EvalRequest):
#     """Run continuous adversarial evaluation against live agent."""
#     try:
#         result = await run_eval(
#             agent_id=request.agent_id,
#             eval_config=request.model_dump()
#         )
#         return {"status": "completed", "result": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/trend/{agent_id}")
# async def get_trend(agent_id: str, days: int = 30):
#     """Get pass rate trend over time. Used for dashboard chart."""
#     trend = await get_eval_trend(agent_id=agent_id, days=days)
#     return {"agent_id": agent_id, "trend": trend, "days": days}


# @router.get("/regression/{agent_id}")
# async def check_regression(agent_id: str):
#     """Check if latest eval is worse than previous one."""
#     result = await detect_regression(agent_id=agent_id)
#     return result


# @router.get("/history/{agent_id}")
# async def get_eval_history(agent_id: str, limit: int = 20):
#     """Get past eval runs for an agent."""
#     db = get_db()
#     cursor = db.eval_results.find(
#         {"agent_id": agent_id},
#         {"failed_attacks": 0}  # Exclude large field
#     ).sort("run_at", -1).limit(limit)

#     history = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])
#         history.append(doc)

#     return {"agent_id": agent_id, "history": history}
# from fastapi import APIRouter

# agentsec_eval_router = APIRouter()

# @agentsec_eval_router.get("/agentsec/evals")
# async def list_evals_for_agent(agent_id: str, scan_id: str | None = None):
#     db = get_db()
#     query = {"agent_id": agent_id}
#     if scan_id:
#         query["scan_id"] = scan_id

#     cursor = db.eval_results.find(query).sort("run_at", -1)
#     docs = await cursor.to_list(length=100)

#     for d in docs:
#         d.pop("_id", None)

#     return docs


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import EvalRequest
from layers.eval_layer import run_eval, get_eval_trend, detect_regression
from core.db import get_db
from fastapi import Request
from core.limiter import limiter
from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from services.ownership_service import create_ownership, get_org_scan_ids, get_org_agent_ids
from services.quota_service import check_eval_quota, release_eval_usage

router = APIRouter(prefix="/eval", tags=["Agent Eval"])


@router.post("/run")
@limiter.limit("5/minute")
async def trigger_eval(
    request: Request,
    eval_request: EvalRequest,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
    _: None = Depends(check_eval_quota),
):
    try:
        result = await run_eval(agent_id=eval_request.agent_id, eval_config=eval_request.model_dump())

        scan_id = result.get("eval_run_id")
        if scan_id:
            await create_ownership(
                db=pg_db, mongo_scan_id=scan_id,
                org_id=current_user.org_id, user_id=current_user.id,
            )
            

        return {"status": "completed", "result": result}
    except Exception as e:
        await release_eval_usage(db=pg_db, org_id=current_user.org_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend/{agent_id}")
async def get_trend(
    agent_id: str, days: int = 30,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_agent_ids = await get_org_agent_ids(pg_db, db, current_user.org_id)
    if agent_id not in org_agent_ids:
        raise HTTPException(status_code=403, detail="Access denied to this agent")
    trend = await get_eval_trend(agent_id=agent_id, days=days)
    return {"agent_id": agent_id, "trend": trend, "days": days}


@router.get("/regression/{agent_id}")
async def check_regression(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_agent_ids = await get_org_agent_ids(pg_db, db, current_user.org_id)
    if agent_id not in org_agent_ids:
        raise HTTPException(status_code=403, detail="Access denied to this agent")
    result = await detect_regression(agent_id=agent_id)
    return result


@router.get("/history/{agent_id}")
async def get_eval_history(
    agent_id: str, limit: int = 20,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_scan_ids = await get_org_scan_ids(pg_db, current_user.org_id)
    cursor = db.eval_results.find(
        {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}},
        {"failed_attacks": 0}
    ).sort("run_at", -1).limit(limit)
    history = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)
    return {"agent_id": agent_id, "history": history}


agentsec_eval_router = APIRouter()

@agentsec_eval_router.get("/agentsec/evals")
async def list_evals_for_agent(
    agent_id: str, scan_id: str | None = None,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_scan_ids = await get_org_scan_ids(pg_db, current_user.org_id)
    query = {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}}
    if scan_id:
        query["scan_id"] = scan_id if scan_id in org_scan_ids else "__none__"
    cursor = db.eval_results.find(query).sort("run_at", -1)
    docs = await cursor.to_list(length=100)
    for d in docs:
        d.pop("_id", None)
    return docs