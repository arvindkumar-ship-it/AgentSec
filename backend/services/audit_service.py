import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from models.audit_models import AuditLog


async def write_audit(db: AsyncSession, org_id, user_id, action: str, target_id: str = None, metadata: dict = None):
    db.add(AuditLog(id=uuid.uuid4(), org_id=org_id, user_id=user_id, action=action, target_id=target_id, audit_metadata=metadata))
    await db.commit()