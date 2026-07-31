from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Integer, JSON, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import datetime
import enum

from database import Base


class PlanTierEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"


class OrgPlanStatusEnum(str, enum.Enum):
    active = "active"
    cancelled = "cancelled"


class UsageEventTypeEnum(str, enum.Enum):
    scan_run = "scan_run"
    eval_run = "eval_run"
    config_change = "config_change"


class Plan(Base):
    __tablename__ = "plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    tier = Column(Enum(PlanTierEnum), nullable=False)
    monthly_price = Column(Integer, nullable=True)  # paise/cents, null for free — Phase F wires this to billing
    description = Column(String, nullable=True)

    org_plans = relationship("OrganizationPlan", back_populates="plan")
    quotas = relationship("OrganizationQuota", back_populates="plan")


class OrganizationPlan(Base):
    __tablename__ = "organization_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

    effective_from = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    effective_to = Column(DateTime, nullable=True)  # null = current plan
    status = Column(Enum(OrgPlanStatusEnum), default=OrgPlanStatusEnum.active, nullable=False)

    organization = relationship("Organization", back_populates="org_plans")
    plan = relationship("Plan", back_populates="org_plans")


class OrganizationQuota(Base):
    __tablename__ = "organization_quotas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("plans.id"), nullable=False)

    max_scans_per_day = Column(Integer, nullable=False)
    max_evals_per_day = Column(Integer, nullable=False, server_default="5")
    max_concurrent_scans = Column(Integer, nullable=False)
    max_storage_mb = Column(Integer, nullable=False)
    max_users = Column(Integer, nullable=False)
    max_targets = Column(Integer, nullable=False)

    organization = relationship("Organization", back_populates="quota")
    plan = relationship("Plan", back_populates="quotas")

    __table_args__ = (
        UniqueConstraint("org_id", name="uq_organization_quotas_org_id"),
    )


class OrganizationUsageDaily(Base):
    __tablename__ = "organization_usage_daily"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    date = Column(DateTime, nullable=False)  # stored as date-truncated DateTime, one row per org per day

    scans_count = Column(Integer, default=0, nullable=False)
    eval_runs = Column(Integer, default=0, nullable=False)
    storage_used_mb = Column(Integer, default=0, nullable=False)
    api_calls = Column(Integer, default=0, nullable=False)
    errors_count = Column(Integer, default=0, nullable=False)

    organization = relationship("Organization", back_populates="usage_daily")

    __table_args__ = (
        UniqueConstraint("org_id", "date", name="uq_organization_usage_daily_org_id_date"),
    )


class UsageEvent(Base):
    __tablename__ = "usage_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    event_type = Column(Enum(UsageEventTypeEnum), nullable=False)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    organization = relationship("Organization", back_populates="usage_events")
    user = relationship("User", back_populates="usage_events")