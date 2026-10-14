from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class MCPToolCallRequest(BaseModel):
    tool_name: str = Field(..., description="Target MCP tool name")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")
    user_goal: str = Field(..., description="Original user prompt or task goal")
    request_id: Optional[str] = None
    caller_id: Optional[str] = "agent_executor"
    timestamp: Optional[int] = None
    hmac_signature: Optional[str] = None

class MCPToolCallResponse(BaseModel):
    request_id: str
    decision: str  # ALLOW, DENY, QUARANTINE, DECEPTION_REDIRECT
    execution_success: bool
    tool_name: str
    result: Any
    quarantined: bool = False
    deception_redirect: bool = False
    risk_score: int
    intent_match_score: float
    explanation: str
    timestamp: str
