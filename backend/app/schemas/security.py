from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SecurityEvaluateRequest(BaseModel):
    user_goal: str = Field(..., description="The original intent / user request")
    tool_name: str = Field(..., description="Proposed MCP tool name")
    tool_arguments: Dict[str, Any] = Field(default_factory=dict, description="Proposed tool arguments")
    caller_id: Optional[str] = "ai_agent_client"
    request_id: Optional[str] = None
    timestamp: Optional[int] = None
    hmac_signature: Optional[str] = None

class SecurityEvaluateResponse(BaseModel):
    request_id: str
    decision: str  # ALLOW, DENY, QUARANTINE, DECEPTION_REDIRECT, REQUIRE_APPROVAL
    risk_score: int  # 0 to 100
    intent_match_score: float  # 0.0 to 1.0
    matched_rules: List[str]
    explanation: str
    deception_active: bool = False
    deception_payload: Optional[Dict[str, Any]] = None
    timestamp: str

class ResponseInspectRequest(BaseModel):
    tool_name: str
    tool_output: Any
    request_id: Optional[str] = None
    redact_sensitive: bool = True

class ResponseInspectResponse(BaseModel):
    request_id: str
    contains_leak: bool
    quarantined: bool
    detected_categories: List[str]
    safe_output: Any
    risk_score: int
    remediation: str

class HMACVerifyRequest(BaseModel):
    payload: Dict[str, Any]
    timestamp: int
    nonce: str
    signature: str

class HMACVerifyResponse(BaseModel):
    valid: bool
    error_reason: Optional[str] = None
    timestamp: int
