from sqlalchemy import Column, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import datetime

from database import Base


class OrgPolicyOverride(Base):
    """Org-specific override for a policy key. Row na ho to POLICY_DEFAULTS ka default apply hota hai."""
    __tablename__ = "org_policy_overrides"
    __table_args__ = (UniqueConstraint("org_id", "key", name="uq_org_policy_key"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)
    key = Column(String, nullable=False)            # e.g. "prompt_injection_strictness"
    value = Column(JSONB, nullable=False)            # e.g. "high" or {"critical": 90, ...}
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)