"""
AgentSec — MongoDB document models (Motor + Pydantic).
Collections: agents, scan_runs, eval_runs, reports
"""
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field
import uuid


def new_id() -> str:
    return str(uuid.uuid4())


class Agent(BaseModel):
    id: str = Field(default_factory=new_id, alias="_id")
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True


class ScanRun(BaseModel):
    id: str = Field(default_factory=new_id, alias="_id")       # scan_id
    agent_id: str
    status: str = "completed"                                   # queued|running|completed|failed
    security_score: int
    risk_level: str                                             # LOW|MEDIUM|HIGH|CRITICAL
    dynamic_testing_performed: bool
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    raw_report: dict[str, Any]                                  # full JSON exactly as produced by ScanRunner

    class Config:
        populate_by_name = True


class EvalRun(BaseModel):
    id: str = Field(default_factory=new_id, alias="_id")        # eval_run_id
    agent_id: str
    scan_id: Optional[str] = None
    run_at: datetime = Field(default_factory=datetime.utcnow)
    pass_rate: float
    consistency_score: Optional[float] = None
    total_tests: int
    successful_attacks: int
    execution_errors: int
    category_breakdown: dict[str, Any]
    failed_attacks: list[dict[str, Any]] = []
    note: str = ""
    raw_result: dict[str, Any]                                  # full JSON exactly as produced by EvalRunner

    class Config:
        populate_by_name = True


class ReportRecord(BaseModel):
    id: str = Field(default_factory=new_id, alias="_id")
    agent_id: str
    scan_id: str
    eval_run_id: Optional[str] = None
    type: str = "COMBINED"                                      # SCAN_REPORT|EVAL_REPORT|COMBINED
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    html_path: Optional[str] = None
    pdf_path: Optional[str] = None

    class Config:
        populate_by_name = True