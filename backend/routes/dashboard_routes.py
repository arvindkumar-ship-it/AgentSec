# from fastapi import APIRouter
# from core.db import get_db
# from datetime import datetime, timedelta

# router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# @router.get("/summary/{agent_id}")
# async def get_dashboard_summary(agent_id: str):
#     """
#     Single endpoint that returns everything the dashboard needs.
#     Latest scan score, shield activity, eval trend, regression alert.
#     """
#     db = get_db()

#     # Latest scan report
#     latest_scan = await db.scan_reports.find_one(
#     {"agent_id": agent_id},
#     {"scan_id": 1, "security_score": 1, "risk_level": 1, "generated_at": 1,
#      "statistics": 1, "executive_summary": 1, "_id": 0},
#     sort=[("generated_at", -1)]
#     )

#     # Shield stats (last 24h)
#     since = datetime.utcnow() - timedelta(hours=24)
#     shield_pipeline = [
#         {"$match": {"agent_id": agent_id, "timestamp": {"$gte": since}}},
#         {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
#     ]
#     shield_cursor = db.shield_logs.aggregate(shield_pipeline)
#     shield_stats = {}
#     async for doc in shield_cursor:
#         shield_stats[doc["_id"]] = doc["count"]

#     # Latest eval
#     latest_eval = await db.eval_results.find_one(
#         {"agent_id": agent_id},
#         {"pass_rate": 1, "consistency_score": 1, "run_at": 1,
#          "total_tests": 1, "successful_attacks": 1, "_id": 0},
#         sort=[("run_at", -1)]
#     )

#     # Eval trend (last 14 days)
#     trend_since = datetime.utcnow() - timedelta(days=14)
#     trend_cursor = db.eval_results.find(
#         {"agent_id": agent_id, "run_at": {"$gte": trend_since.isoformat()}},
#         {"run_at": 1, "pass_rate": 1, "_id": 0}
#     ).sort("run_at", 1)
#     trend = [doc async for doc in trend_cursor]

#     # Regression check
#     regression = {"regression_detected": False}
#     if db is not None:
#         from layers.eval_layer import detect_regression
#         regression = await detect_regression(agent_id)

#     return {
#         "agent_id": agent_id,
#         "latest_scan": latest_scan,
#         "shield": {
#             "last_24h": shield_stats,
#             "total_blocked": shield_stats.get("BLOCKED", 0) + shield_stats.get("POLICY_VIOLATION", 0),
#             "total_allowed": shield_stats.get("SUCCESS", 0),
#         },
#         "latest_eval": latest_eval,
#         "eval_trend": trend,
#         "regression": regression,
#     }


# @router.get("/agents")
# async def list_agents():
#     """List all agents that have been scanned."""
#     db = get_db()
#     pipeline = [
#         {"$group": {
#             "_id": "$agent_id",
#             "agent_name": {"$last": "$agent_name"},
#             "last_scan": {"$max": "$generated_at"},
#             "best_score": {"$max": "$security_score"},
#             "latest_score": {"$last": "$security_score"},
#         }},
#         {"$sort": {"last_scan": -1}}
#     ]
#     cursor = db.scan_reports.aggregate(pipeline)
#     agents = [doc async for doc in cursor]
#     for a in agents:
#         a["agent_id"] = a.pop("_id")
#     return {"agents": agents}










from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_db
from datetime import datetime, timedelta

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db
from services.ownership_service import get_org_scan_ids, get_org_agent_ids
from services.quota_service import get_or_create_org_quota, get_or_create_today_usage

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary/{agent_id}")
async def get_dashboard_summary(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_agent_ids = await get_org_agent_ids(pg_db, db, current_user.org_id)
    if agent_id not in org_agent_ids:
        raise HTTPException(status_code=403, detail="Access denied to this agent")

    org_scan_ids = await get_org_scan_ids(pg_db, current_user.org_id)

    latest_scan = await db.scan_reports.find_one(
        {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}},
        {"scan_id": 1, "security_score": 1, "risk_level": 1, "generated_at": 1,
         "statistics": 1, "executive_summary": 1, "_id": 0},
        sort=[("generated_at", -1)]
    )

    since = datetime.utcnow() - timedelta(hours=24)
    shield_pipeline = [
        {"$match": {"agent_id": agent_id, "timestamp": {"$gte": since}}},
        {"$group": {"_id": "$event_type", "count": {"$sum": 1}}}
    ]
    shield_cursor = db.shield_logs.aggregate(shield_pipeline)
    shield_stats = {}
    async for doc in shield_cursor:
        shield_stats[doc["_id"]] = doc["count"]

    latest_eval = await db.eval_results.find_one(
        {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}},
        {"pass_rate": 1, "consistency_score": 1, "run_at": 1,
         "total_tests": 1, "successful_attacks": 1, "_id": 0},
        sort=[("run_at", -1)]
    )

    trend_since = datetime.utcnow() - timedelta(days=14)
    trend_cursor = db.eval_results.find(
        {"agent_id": agent_id, "scan_id": {"$in": org_scan_ids}, "run_at": {"$gte": trend_since.isoformat()}},
        {"run_at": 1, "pass_rate": 1, "_id": 0}
    ).sort("run_at", 1)
    trend = [doc async for doc in trend_cursor]

    regression = {"regression_detected": False}
    if db is not None:
        from layers.eval_layer import detect_regression
        regression = await detect_regression(agent_id)

    return {
        "agent_id": agent_id,
        "latest_scan": latest_scan,
        "shield": {
            "last_24h": shield_stats,
            "total_blocked": shield_stats.get("BLOCKED", 0) + shield_stats.get("POLICY_VIOLATION", 0),
            "total_allowed": shield_stats.get("SUCCESS", 0),
        },
        "latest_eval": latest_eval,
        "eval_trend": trend,
        "regression": regression,
    }


@router.get("/agents")
async def list_agents(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    db = get_db()
    org_scan_ids = await get_org_scan_ids(pg_db, current_user.org_id)
    pipeline = [
        {"$match": {"scan_id": {"$in": org_scan_ids}}},
        {"$group": {
            "_id": "$agent_id",
            "agent_name": {"$last": "$agent_name"},
            "last_scan": {"$max": "$generated_at"},
            "best_score": {"$max": "$security_score"},
            "latest_score": {"$last": "$security_score"},
        }},
        {"$sort": {"last_scan": -1}}
    ]
    cursor = db.scan_reports.aggregate(pipeline)
    agents = [doc async for doc in cursor]
    for a in agents:
        a["agent_id"] = a.pop("_id")
    return {"agents": agents}


@router.get("/usage")
async def get_usage_summary(
    current_user: User = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_pg_db),
):
    quota = await get_or_create_org_quota(pg_db, current_user.org_id)
    usage = await get_or_create_today_usage(pg_db, current_user.org_id)
    return {
        "scans": {"used": usage.scans_count, "limit": quota.max_scans_per_day},
        "evals": {"used": usage.eval_runs, "limit": quota.max_evals_per_day},
        "storage_mb": {"used": usage.storage_used_mb, "limit": quota.max_storage_mb},
        "max_concurrent_scans": quota.max_concurrent_scans,
    }