from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import csv, io

from auth import get_current_user
from models.sql_models import User
from models.audit_models import AuditLog
from database import get_db as get_pg_db

router = APIRouter(prefix="/audit-logs", tags=["Audit"])


@router.get("")
async def list_audit_logs(action: str | None = None, user_id: str | None = None, start_date: str | None = None,
                           end_date: str | None = None, limit: int = 100,
                           current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    query = select(AuditLog).where(AuditLog.org_id == current_user.org_id)
    if action: query = query.where(AuditLog.action == action)
    if user_id: query = query.where(AuditLog.user_id == user_id)
    if start_date: query = query.where(AuditLog.created_at >= datetime.fromisoformat(start_date))
    if end_date: query = query.where(AuditLog.created_at <= datetime.fromisoformat(end_date))
    result = await pg_db.execute(query.order_by(AuditLog.created_at.desc()).limit(limit))
    logs = result.scalars().all()
    return [{"id": str(l.id), "user_id": str(l.user_id) if l.user_id else None, "action": l.action,
             "target_id": l.target_id, "metadata": l.audit_metadata, "created_at": l.created_at.isoformat()} for l in logs]


@router.get("/export")
async def export_audit_logs(current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await pg_db.execute(select(AuditLog).where(AuditLog.org_id == current_user.org_id).order_by(AuditLog.created_at.desc()))
    logs = result.scalars().all()
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["timestamp", "user_id", "action", "target_id", "metadata"])
    for l in logs:
        writer.writerow([l.created_at.isoformat(), l.user_id, l.action, l.target_id, l.audit_metadata])
    return Response(content=buffer.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=audit_logs.csv"})