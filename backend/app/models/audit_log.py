import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, Text, DateTime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=False, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    caller_ip = Column(String(45), default="127.0.0.1")
    action = Column(String(100), nullable=False)
    outcome = Column(String(50), nullable=False) # SUCCESS, BLOCKED, QUARANTINED, DECEPTION
    hmac_verified = Column(Boolean, default=True)
    sanitized_summary = Column(Text, nullable=False)
    metadata_json = Column(Text, nullable=True)
