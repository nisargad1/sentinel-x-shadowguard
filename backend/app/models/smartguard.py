import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, DateTime
from app.core.database import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)
    monthly_budget_cents = Column(Integer, default=10000) # $100.00
    current_spend_cents = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(64), primary_key=True) # e.g. finance-analyst-agent
    workspace_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    status = Column(String(20), default="ACTIVE")
    permitted_tools = Column(Text, default="[]") # JSON list of strings
    permitted_resources = Column(Text, default="[]") # JSON list of strings/patterns
    budget_limit_cents = Column(Integer, default=2000) # $20.00
    current_spend_cents = Column(Integer, default=0)
    trust_score = Column(Integer, default=95) # 0 to 100
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Policy(Base):
    __tablename__ = "policies"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), default="v1.0")
    policy_type = Column(String(50), nullable=False) # AUTHORIZATION, COST_BUDGET, SENSITIVE_ACTION, INJECTION_PREVENTION, OPTIMIZATION
    rules_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    precedence = Column(Integer, default=10) # Lower number = higher priority
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ActionEvaluation(Base):
    __tablename__ = "action_evaluations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(64), nullable=False, index=True)
    correlation_id = Column(String(64), nullable=False, index=True)
    user_intent = Column(Text, nullable=True)
    tool_name = Column(String(100), nullable=False, index=True)
    action_name = Column(String(100), nullable=False)
    parameters_json = Column(Text, nullable=False)
    
    # 4 Primary Decisions: ALLOW, OPTIMIZE, ASK, BLOCK
    decision = Column(String(20), nullable=False, index=True)
    reason_code = Column(String(50), nullable=False, index=True)
    explanation = Column(Text, nullable=False)
    
    risk_score = Column(Float, default=0.0) # 0.0 to 1.0
    risk_level = Column(String(20), default="LOW") # LOW, MEDIUM, HIGH, CRITICAL
    
    cost_estimate_cents = Column(Integer, default=0)
    cost_actual_cents = Column(Integer, default=0)
    savings_cents = Column(Integer, default=0)
    optimization_applied = Column(String(100), nullable=True)
    
    execution_status = Column(String(30), default="NOT_EXECUTED") # EXECUTED, BLOCKED, OPTIMIZED, PENDING_APPROVAL, REJECTED
    execution_result_json = Column(Text, nullable=True)
    duration_ms = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    agent_id = Column(String(64), nullable=False, index=True)
    evaluation_id = Column(String(36), nullable=False, index=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(String(20), default="PENDING", index=True) # PENDING, APPROVED, REJECTED, EXPIRED
    expires_at = Column(DateTime, nullable=False, index=True)
    approved_by = Column(String(100), nullable=True)
    action_payload_json = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    key_prefix = Column(String(16), nullable=False, index=True)
    hashed_secret = Column(String(128), nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class BenchmarkRun(Base):
    __tablename__ = "benchmark_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(String(36), nullable=False, index=True)
    total_actions = Column(Integer, default=0)
    allowed_count = Column(Integer, default=0)
    optimized_count = Column(Integer, default=0)
    blocked_count = Column(Integer, default=0)
    ask_count = Column(Integer, default=0)
    baseline_cost_cents = Column(Integer, default=0)
    enforced_cost_cents = Column(Integer, default=0)
    net_savings_cents = Column(Integer, default=0)
    avg_latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
