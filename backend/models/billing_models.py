from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid, datetime
from database import Base


class SSOConfig(Base):
    __tablename__ = "sso_configs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, unique=True)
    provider = Column(String, nullable=False)
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)
    redirect_uri = Column(String, nullable=False)
    issuer = Column(String, nullable=True)
    sso_only = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)