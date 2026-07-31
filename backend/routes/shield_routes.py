# from fastapi import APIRouter, HTTPException
# from models.schemas import ShieldRegisterRequest, ShieldLogQuery, RevertRequest, CheckOutboundRequest
# from layers.shield import AgentShield
# from core.db import get_db
# from datetime import datetime, timedelta

# router = APIRouter(prefix="/shield", tags=["Agent Shield"])

# # In-memory shield registry (in production: use Redis)
# _shields: dict[str, AgentShield] = {}


# @router.post("/register")
# async def register_shield(request: ShieldRegisterRequest):
#     """
#     Register an agent with Shield. Get back SDK usage instructions.
#     """
#     shield = AgentShield(agent_id=request.agent_id, policy=request.policy)
#     _shields[request.agent_id] = shield

#     return {
#         "status": "registered",
#         "agent_id": request.agent_id,
#         "sdk_usage": {
#             "python": f"""
# # Install: pip install agentsec-sdk
# from agentsec import AgentShield

# shield = AgentShield(
#     agent_id="{request.agent_id}",
#     api_url="http://localhost:8000"
# )

# # Wrap any tool:
# @shield.protect
# async def your_tool(input: str) -> str:
#     return "result"

# # Check outbound response:
# safe = await shield.check_outbound(agent_response)
# """
#         }
#     }


# @router.post("/check-outbound")
# async def check_outbound(request: CheckOutboundRequest):
#     """
#     Check if an agent's response is safe to send to user.
#     Called by your agent runtime before returning response.
#     """
#     if request.agent_id not in _shields:
#         shield = AgentShield(agent_id=request.agent_id)
#         _shields[request.agent_id] = shield

#     shield = _shields[request.agent_id]
#     result = await shield.check_outbound(request.response_text)
#     return result


# @router.post("/revert")
# async def revert_checkpoint(request: RevertRequest):
#     """Revert agent to a previous checkpoint."""
#     if request.agent_id not in _shields:
#         shield = AgentShield(agent_id=request.agent_id)
#         _shields[request.agent_id] = shield

#     shield = _shields[request.agent_id]
#     result = await shield.revert_to_checkpoint(request.checkpoint_id)
#     return result


# @router.get("/logs/{agent_id}")
# async def get_shield_logs(agent_id: str, hours: int = 24, limit: int = 100):
#     """Get shield audit logs for an agent."""
#     db = get_db()
#     since = datetime.utcnow() - timedelta(hours=hours)

#     cursor = db.shield_logs.find(
#         {"agent_id": agent_id, "timestamp": {"$gte": since}},
#     ).sort("timestamp", -1).limit(limit)

#     logs = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])
#         doc["timestamp"] = doc["timestamp"].isoformat()
#         logs.append(doc)

#     return {"agent_id": agent_id, "logs": logs, "count": len(logs)}


# @router.get("/stats/{agent_id}")
# async def get_shield_stats(agent_id: str, hours: int = 24):
#     """Get summary stats for agent shield activity."""
#     if agent_id not in _shields:
#         shield = AgentShield(agent_id=agent_id)
#         _shields[agent_id] = shield

#     stats = await _shields[agent_id].get_stats(hours=hours)
#     return stats


# @router.get("/checkpoints/{agent_id}")
# async def get_checkpoints(agent_id: str, limit: int = 20):
#     """Get list of checkpoints for undo functionality."""
#     db = get_db()
#     cursor = db.checkpoints.find(
#         {"agent_id": agent_id},
#         {"_id": 0}
#     ).sort("created_at", -1).limit(limit)

#     checkpoints = []
#     async for doc in cursor:
#         doc["created_at"] = doc["created_at"].isoformat()
#         checkpoints.append(doc)

#     return {"agent_id": agent_id, "checkpoints": checkpoints}
#-----------------------------------------------------------------------------------


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.schemas import ShieldRegisterRequest, ShieldLogQuery, RevertRequest, CheckOutboundRequest
from layers.shield import AgentShield
from core.db import get_db
from datetime import datetime, timedelta

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from services.ownership_service import get_org_agent_ids

router = APIRouter(prefix="/shield", tags=["Agent Shield"])

_shields: dict[str, AgentShield] = {}


async def _check_agent_access(agent_id: str, current_user: User, pg_db: AsyncSession):
    db = get_db()
    scan_doc = await db.scan_reports.find_one({"agent_id": agent_id}, {"scan_id": 1})
    if scan_doc is None:
        return
    org_agent_ids = await get_org_agent_ids(pg_db, db, current_user.org_id)
    if agent_id not in org_agent_ids:
        raise HTTPException(status_code=403, detail="Access denied to this agent")


@router.post("/register")
async def register_shield(request: ShieldRegisterRequest, current_user: User = Depends(get_current_user)):
    shield = AgentShield(agent_id=request.agent_id, policy=request.policy)
    _shields[request.agent_id] = shield
    return {
        "status": "registered",
        "agent_id": request.agent_id,
        "sdk_usage": {
            "python": f"""
# Install: pip install agentsec-sdk
from agentsec import AgentShield

shield = AgentShield(
    agent_id="{request.agent_id}",
    api_url="http://localhost:8000"
)

@shield.protect
async def your_tool(input: str) -> str:
    return "result"

safe = await shield.check_outbound(agent_response)
"""
        }
    }


@router.post("/check-outbound")
async def check_outbound(request: CheckOutboundRequest, current_user: User = Depends(get_current_user)):
    if request.agent_id not in _shields:
        shield = AgentShield(agent_id=request.agent_id)
        _shields[request.agent_id] = shield
    shield = _shields[request.agent_id]
    result = await shield.check_outbound(request.response_text)
    return result


@router.post("/revert")
async def revert_checkpoint(request: RevertRequest, current_user: User = Depends(get_current_user)):
    if request.agent_id not in _shields:
        shield = AgentShield(agent_id=request.agent_id)
        _shields[request.agent_id] = shield
    shield = _shields[request.agent_id]
    result = await shield.revert_to_checkpoint(request.checkpoint_id)
    return result


@router.get("/logs/{agent_id}")
async def get_shield_logs(
    agent_id: str, hours: int = 24, limit: int = 100,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_agent_access(agent_id, current_user, pg_db)
    db = get_db()
    since = datetime.utcnow() - timedelta(hours=hours)
    cursor = db.shield_logs.find(
        {"agent_id": agent_id, "timestamp": {"$gte": since}},
    ).sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["timestamp"] = doc["timestamp"].isoformat()
        logs.append(doc)
    return {"agent_id": agent_id, "logs": logs, "count": len(logs)}


@router.get("/stats/{agent_id}")
async def get_shield_stats(
    agent_id: str, hours: int = 24,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_agent_access(agent_id, current_user, pg_db)
    if agent_id not in _shields:
        shield = AgentShield(agent_id=agent_id)
        _shields[agent_id] = shield
    stats = await _shields[agent_id].get_stats(hours=hours)
    return stats


@router.get("/checkpoints/{agent_id}")
async def get_checkpoints(
    agent_id: str, limit: int = 20,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    await _check_agent_access(agent_id, current_user, pg_db)
    db = get_db()
    cursor = db.checkpoints.find(
        {"agent_id": agent_id}, {"_id": 0}
    ).sort("created_at", -1).limit(limit)
    checkpoints = []
    async for doc in cursor:
        doc["created_at"] = doc["created_at"].isoformat()
        checkpoints.append(doc)
    return {"agent_id": agent_id, "checkpoints": checkpoints}