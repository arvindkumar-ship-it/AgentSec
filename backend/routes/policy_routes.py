from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Any

from auth import get_current_user
from models.sql_models import User
from database import get_db as get_pg_db

from services.policy_service import get_effective_policies

router = APIRouter(prefix="/policies", tags=["Policy Engine"])


class PolicyUpdateRequest(BaseModel):
    value: Any


@router.get("")
async def list_effective_policies(current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    return await get_effective_policies(pg_db, current_user.org_id)


@router.put("/{key}")
async def update_tenant_policy(key: str, payload: PolicyUpdateRequest, current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    raise HTTPException(409, "Tenant policy overrides are not wired to runtime enforcement yet")
