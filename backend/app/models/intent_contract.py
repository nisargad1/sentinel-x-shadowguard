import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from app.core.database import Base

class IntentContractRecord(Base):
    __tablename__ = "intent_contracts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_goal = Column(Text, nullable=False)
    permitted_resources = Column(Text, nullable=False) # JSON array string
    permitted_actions = Column(Text, nullable=False) # JSON array string
    prohibited_actions = Column(Text, nullable=False) # JSON array string
    risk_constraints = Column(Text, nullable=False) # JSON object string
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
