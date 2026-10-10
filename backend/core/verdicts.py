"""Shared, strict contracts for security verdicts and measured outcomes."""
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt
from typing import Literal


class AttackVerdict(BaseModel):
    model_config = ConfigDict(extra="ignore")
    success: StrictBool
    confidence: StrictInt = Field(default=50, ge=0, le=100)
    reason: str = ""
    extracted_info: str | None = None


class SafetyVerdict(BaseModel):
    model_config = ConfigDict(extra="ignore")
    safe: StrictBool
    issues: list[str] = []
    severity: Literal["NONE", "LOW", "MEDIUM", "HIGH", "CRITICAL"] = "LOW"
    action: Literal["ALLOW", "WARN", "BLOCK"]


def is_measured_verdict(verdict) -> bool:
    """A review-needed/no-signal result is neither a pass nor a failure."""
    return (isinstance(verdict, dict) and type(verdict.get("success")) is bool
            and verdict.get("needs_review") is False)


def fail_closed(reason: str) -> dict:
    return {"safe": False, "issues": [reason], "severity": "MEDIUM", "action": "BLOCK"}
