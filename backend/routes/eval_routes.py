from fastapi import APIRouter, HTTPException
from models.schemas import EvalRequest
from layers.eval_layer import run_eval, get_eval_trend, detect_regression
from core.db import get_db

router = APIRouter(prefix="/eval", tags=["Agent Eval"])


@router.post("/run")
async def trigger_eval(request: EvalRequest):
    """Run continuous adversarial evaluation against live agent."""
    try:
        result = await run_eval(
            agent_id=request.agent_id,
            eval_config=request.model_dump()
        )
        return {"status": "completed", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trend/{agent_id}")
async def get_trend(agent_id: str, days: int = 30):
    """Get pass rate trend over time. Used for dashboard chart."""
    trend = await get_eval_trend(agent_id=agent_id, days=days)
    return {"agent_id": agent_id, "trend": trend, "days": days}


@router.get("/regression/{agent_id}")
async def check_regression(agent_id: str):
    """Check if latest eval is worse than previous one."""
    result = await detect_regression(agent_id=agent_id)
    return result


@router.get("/history/{agent_id}")
async def get_eval_history(agent_id: str, limit: int = 20):
    """Get past eval runs for an agent."""
    db = get_db()
    cursor = db.eval_results.find(
        {"agent_id": agent_id},
        {"failed_attacks": 0}  # Exclude large field
    ).sort("run_at", -1).limit(limit)

    history = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        history.append(doc)

    return {"agent_id": agent_id, "history": history}
from fastapi import APIRouter

agentsec_eval_router = APIRouter()

@agentsec_eval_router.get("/agentsec/evals")
async def list_evals_for_agent(agent_id: str, scan_id: str | None = None):
    db = get_db()
    query = {"agent_id": agent_id}
    if scan_id:
        query["scan_id"] = scan_id

    cursor = db.eval_results.find(query).sort("run_at", -1)
    docs = await cursor.to_list(length=100)

    for d in docs:
        d.pop("_id", None)

    return docs