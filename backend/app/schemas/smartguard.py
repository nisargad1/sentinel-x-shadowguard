from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class ActionProposeRequest(BaseModel):
    workspace_id: str = Field(default="ws-default", description="Tenant workspace ID")
    agent_id: str = Field(..., description="ID of the proposing autonomous agent")
    user_intent: str = Field(..., description="Original user prompt or authorized objective")
    tool_name: str = Field(..., description="Proposed tool identifier")
    action_name: str = Field(default="execute", description="Action verb e.g. read, write, query, delete")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Proposed tool parameters")
    resource_id: Optional[str] = Field(default=None, description="Target resource if applicable (e.g. file, table)")
    estimated_cost_cents: Optional[int] = Field(default=0, description="Estimated execution cost in cents")
    correlation_id: Optional[str] = Field(default=None, description="Distributed correlation ID")

class ActionEvaluationOutput(BaseModel):
    correlation_id: str
    evaluation_id: str
    decision: str  # ALLOW, OPTIMIZE, ASK, BLOCK
    reason_code: str  # AUTHZ_PERMITTED, DUPLICATE_OPTIMIZED_CACHE_HIT, SENSITIVE_WRITE_REQUIRES_APPROVAL, etc.
    explanation: str
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    risk_score: float  # 0.0 to 1.0
    intent_alignment_score: float  # 0.0 to 1.0
    
    # Financial & Efficiency Evidence
    cost_estimate_cents: int
    cost_actual_cents: int
    savings_cents: int
    optimization_applied: Optional[str] = None
    
    # Execution status & evidence
    execution_status: str  # EXECUTED, BLOCKED, OPTIMIZED, PENDING_APPROVAL, REJECTED
    execution_result: Optional[Any] = None
    approval_token: Optional[str] = None
    approval_id: Optional[str] = None
    duration_ms: float
    timestamp: str

class ApprovalActionRequest(BaseModel):
    action: str = Field(..., description="APPROVE or REJECT")
    approved_by: Optional[str] = Field(default="secops-operator@enterprise.com", description="Approving identity")
    reason: Optional[str] = Field(default="Human operator validated write operation", description="Decision rationale")

class ApprovalItem(BaseModel):
    id: str
    workspace_id: str
    agent_id: str
    evaluation_id: str
    status: str  # PENDING, APPROVED, REJECTED, EXPIRED
    expires_at: str
    created_at: str
    approved_by: Optional[str] = None
    tool_name: str
    action_name: str
    parameters: Dict[str, Any]
    user_intent: str
    cost_estimate_cents: int
    risk_level: str

class AgentProfileOutput(BaseModel):
    id: str
    workspace_id: str
    name: str
    role: str
    status: str
    permitted_tools: List[str]
    permitted_resources: List[str]
    budget_limit_cents: int
    current_spend_cents: int
    trust_score: int
    total_actions: int = 0
    allowed_count: int = 0
    blocked_count: int = 0
    ask_count: int = 0
    optimized_count: int = 0
    recent_evaluations: List[Dict[str, Any]] = []

class ProofOfValueMetrics(BaseModel):
    total_proposed_actions: int
    total_executed_actions: int
    total_prevented_actions: int
    total_approval_actions: int
    total_optimized_actions: int
    
    baseline_cost_cents: int
    enforced_cost_cents: int
    gateway_overhead_cents: int
    net_savings_cents: int
    
    average_policy_latency_ms: float
    duplicate_calls_avoided: int
    currency: str = "USD"
    measurement_mode: str = "measured_runtime_telemetry"

class ScenarioRunRequest(BaseModel):
    scenario_id: str = Field(..., description="scenario_1, scenario_2, scenario_3, scenario_4, scenario_5, scenario_6")

class ScenarioRunOutput(BaseModel):
    scenario_id: str
    title: str
    expected_decision: str
    actual_decision: str
    evaluation: ActionEvaluationOutput
    execution_evidence: Dict[str, Any]
    audit_event_id: str
    verified: bool
