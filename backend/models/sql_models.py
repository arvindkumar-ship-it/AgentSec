from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum

from database import Base


class RoleEnum(str, enum.Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    state = Column(String, default="active", nullable=False)
    org_plans = relationship("OrganizationPlan", back_populates="organization")
    quota = relationship("OrganizationQuota", back_populates="organization", uselist=False)
    usage_daily = relationship("OrganizationUsageDaily", back_populates="organization")
    usage_events = relationship("UsageEvent", back_populates="organization")

    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.member, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    organization = relationship("Organization", back_populates="users")
    usage_events = relationship("UsageEvent", back_populates="user")


class ScanOwnership(Base):
    __tablename__ = "scan_ownership"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mongo_scan_id = Column(String, nullable=False, index=True)

    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)