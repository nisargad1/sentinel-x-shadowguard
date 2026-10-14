from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class SecurityEventSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    timestamp: str
    event_type: str
    severity: str
    decision: str
    source: str
    user_goal: Optional[str] = None
    proposed_action: Optional[str] = None
    tool_name: Optional[str] = None
    risk_score: int
    intent_score: float
    payload_preview: Optional[str] = None
    detection_rule: Optional[str] = None
    remediation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class RiskTrendPoint(BaseModel):
    time: str
    avg_risk: float
    blocked_count: int
    allowed_count: int

class DashboardSummary(BaseModel):
    total_inspected: int
    allowed_count: int
    blocked_count: int
    attacks_detected: int
    dlp_leaks_prevented: int
    sandbox_activations: int
    system_health: str  # OPERATIONAL, ELEVATED_THREAT, CRITICAL
    average_risk_score: float
    risk_trend: List[RiskTrendPoint]
    recent_events: List[SecurityEventSchema]

class AuditLogSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    request_id: str
    timestamp: str
    caller_ip: str
    action: str
    outcome: str
    hmac_verified: bool
    sanitized_summary: str
    metadata: Optional[Dict[str, Any]] = None
