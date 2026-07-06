from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ToolSchema(BaseModel):
    name: str
    description: str = ""
    parameters: Dict[str, Any] = {}


class ScanRequest(BaseModel):
    agent_id: str = Field(..., description="Unique identifier for your agent")
    agent_name: str
    system_prompt: str = ""
    endpoint_url: str = Field("", description="Your agent's HTTP endpoint (POST)")
    auth_header: str = Field("", description="e.g. 'Bearer your-token'")
    tools: List[ToolSchema] = []
    source_code: str = Field("", description="Optional: paste agent Python source code")
    rag_enabled: bool = False
    categories: List[str] = Field([], description="Filter single-shot attack categories. Empty = all.")
    request_format: Optional[Dict[str, Any]] = None
    use_form_data: bool = Field(False, description="Send attacks as form-urlencoded instead of JSON (e.g. for Gandalf-style APIs)")
    form_extra_fields: Optional[Dict[str, Any]] = Field(None, description="Extra static fields to include in the form body, e.g. {'defender': 'baseline'}")
    run_multiturn: bool = Field(True, description="Run multi-turn manipulation chains (requires endpoint_url)")
    run_document_injection: bool = Field(True, description="Run indirect/document injection tests (requires endpoint_url)")
    run_blackbox_probes: bool = Field(True, description="Run black-box behavioral probes without source code")

class EvalRequest(BaseModel):
    agent_id: str
    agent_name: str
    endpoint_url: str
    auth_header: str = ""
    categories: List[str] = []
    consistency_checks: int = Field(3, ge=1, le=5)


class ShieldRegisterRequest(BaseModel):
    agent_id: str
    agent_name: str
    policy: Dict[str, Any] = {}


class ShieldLogQuery(BaseModel):
    agent_id: str
    hours: int = 24
    event_type: Optional[str] = None


class RevertRequest(BaseModel):
    agent_id: str
    checkpoint_id: str


class CheckOutboundRequest(BaseModel):
    agent_id: str
    response_text: str
