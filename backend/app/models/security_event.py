import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from app.core.database import Base

class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    event_type = Column(String(50), nullable=False, index=True)
    # Types: INTENT_DRIFT, PATH_TRAVERSAL, COMMAND_INJECTION, SQL_INJECTION, PROMPT_INJECTION, DLP_LEAK_PREVENTED, DECEPTION_ACTIVATED, HMAC_TAMPER_DETECTED, AUTHORIZED_ACCESS
    
    severity = Column(String(20), nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    decision = Column(String(30), nullable=False) # ALLOW, DENY, QUARANTINE, DECEPTION_REDIRECT, REQUIRE_APPROVAL
    source = Column(String(50), default="mcp_gateway")
    
    user_goal = Column(Text, nullable=True)
    proposed_action = Column(Text, nullable=True)
    tool_name = Column(String(100), nullable=True)
    
    risk_score = Column(Integer, default=0) # 0 to 100
    intent_score = Column(Float, default=1.0) # 0.0 to 1.0
    
    payload_preview = Column(Text, nullable=True) # Sanitized representation
    detection_rule = Column(String(100), nullable=True)
    remediation = Column(Text, nullable=True)
    details_json = Column(Text, nullable=True) # Full structured metadata as JSON string
