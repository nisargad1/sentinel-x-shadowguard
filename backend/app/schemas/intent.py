from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IntentContract(BaseModel):
    contract_id: str
    user_goal: str
    permitted_resources: List[str]
    permitted_actions: List[str]
    prohibited_actions: List[str]
    risk_constraints: Dict[str, Any]

class IntentEvaluateRequest(BaseModel):
    user_goal: str
    tool_name: str
    tool_arguments: Dict[str, Any] = Field(default_factory=dict)

class IntentEvaluateResponse(BaseModel):
    contract: IntentContract
    decision: str  # ALLOW, DENY, REQUIRE_APPROVAL
    intent_match_score: float  # 0.0 to 1.0
    risk_score: int  # 0 to 100
    explanation: str
    matched_rules: List[str]
