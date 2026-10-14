import uuid
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.smartguard import Agent, Workspace, ActionEvaluation, ApprovalRequest
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog
from app.schemas.smartguard import ScenarioRunRequest, ScenarioRunOutput, ActionProposeRequest
from app.services.action_value_engine import action_value_engine

router = APIRouter(prefix="/api/v1/scenarios", tags=["SmartGuard 6 Demo Scenarios"])

SCENARIOS_META = {
    "scenario_1": {
        "id": "scenario_1",
        "title": "Legitimate Document Summary",
        "expected_decision": "ALLOW",
        "agent_id": "finance-analyst-agent",
        "user_intent": "Summarize Q3 earnings report for executive briefing",
        "tool_name": "read_demo_file",
        "action_name": "read",
        "parameters": {"filename": "report.pdf"},
        "description": "Authorized agent requests permitted document. Gateway verifies intent alignment & permissions, executes tool, and logs execution."
    },
    "scenario_2": {
        "id": "scenario_2",
        "title": "Restricted Payroll Access",
        "expected_decision": "BLOCK",
        "agent_id": "finance-analyst-agent",
        "user_intent": "Summarize Q3 earnings report for executive briefing",
        "tool_name": "read_demo_file",
        "action_name": "read",
        "parameters": {"filename": "payroll_salaries.csv"},
        "description": "Agent attempts to read restricted payroll CSV outside its permitted scope. Protected tool is never invoked; structured block recorded."
    },
    "scenario_3": {
        "id": "scenario_3",
        "title": "Redundant Search Optimization",
        "expected_decision": "OPTIMIZE",
        "agent_id": "market-research-agent",
        "user_intent": "Research competitor enterprise tier pricing",
        "tool_name": "search_demo_documents",
        "action_name": "query",
        "parameters": {"query": "enterprise tier pricing"},
        "description": "Agent repeats an identical search query within a 60-second window. Gateway detects duplication, serves from safe cache, and records net cost savings."
    },
    "scenario_4": {
        "id": "scenario_4",
        "title": "Sensitive Action Requiring Approval",
        "expected_decision": "ASK",
        "agent_id": "crm-automation-agent",
        "user_intent": "Deactivate churned customer account CUST-9842",
        "tool_name": "update_customer_status",
        "action_name": "update",
        "parameters": {"customer_id": "CUST-9842", "new_status": "DEACTIVATED"},
        "description": "Agent attempts a sensitive write operation. Action is halted pre-execution, generating a cryptographic approval token in the Human Approval Inbox."
    },
    "scenario_5": {
        "id": "scenario_5",
        "title": "Budget Limit Exceeded",
        "expected_decision": "BLOCK",
        "agent_id": "translation-agent",
        "user_intent": "Batch translate high-volume document",
        "tool_name": "translate_document",
        "action_name": "translate",
        "parameters": {"doc_id": "doc_large.pdf", "estimated_cost": 50},
        "description": "Agent attempts a high-cost translation (50¢) that exceeds its remaining budget cap (only 5¢ left of 100¢). Gateway halts execution atomically."
    },
    "scenario_6": {
        "id": "scenario_6",
        "title": "Prompt Injection in Synthetic Content",
        "expected_decision": "BLOCK",
        "agent_id": "support-agent",
        "user_intent": "Review support ticket with hidden prompt injection",
        "tool_name": "dump_database_credentials",
        "action_name": "execute",
        "parameters": {"extract": "admin_keys", "override": "SYSTEM_OVERRIDE_ACTIVE"},
        "description": "Untrusted ticket content instructs agent to dump database credentials. Gateway's deterministic allowlist and prompt injection filters block the tool."
    }
}

@router.get("", response_model=List[Dict[str, Any]])
def list_scenarios():
    """Lists metadata for all six reproducible demo scenarios."""
    return list(SCENARIOS_META.values())

@router.post("/run", response_model=ScenarioRunOutput)
def run_scenario(req: ScenarioRunRequest, db: Session = Depends(get_db)):
    """
    Executes a reproducible demo scenario against real backend policy logic.
    Returns the real evaluation result, execution evidence, and audit verification.
    """
    scenario = SCENARIOS_META.get(req.scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{req.scenario_id}' not found. Use scenario_1 through scenario_6.")

    # Special handling for Scenario 3: To guarantee OPTIMIZE cache hit, ensure first run has populated cache
    if req.scenario_id == "scenario_3":
        # Prime the cache with the initial run
        prime_req = ActionProposeRequest(
            workspace_id="ws-default",
            agent_id=scenario["agent_id"],
            user_intent=scenario["user_intent"],
            tool_name=scenario["tool_name"],
            action_name=scenario["action_name"],
            parameters=scenario["parameters"],
            correlation_id=str(uuid.uuid4())
        )
        action_value_engine.evaluate_and_execute(db, prime_req)

    # Now execute the evaluated scenario action
    action_req = ActionProposeRequest(
        workspace_id="ws-default",
        agent_id=scenario["agent_id"],
        user_intent=scenario["user_intent"],
        tool_name=scenario["tool_name"],
        action_name=scenario["action_name"],
        parameters=scenario["parameters"],
        correlation_id=str(uuid.uuid4())
    )

    eval_output = action_value_engine.evaluate_and_execute(db, action_req)

    # Verify expected decision matches actual
    verified = (eval_output.decision == scenario["expected_decision"])

    execution_evidence = {
        "execution_status": eval_output.execution_status,
        "protected_tool_invoked": eval_output.execution_status == "EXECUTED",
        "savings_measured_cents": eval_output.savings_cents,
        "cost_incurred_cents": eval_output.cost_actual_cents,
        "result_payload": eval_output.execution_result
    }

    return ScenarioRunOutput(
        scenario_id=req.scenario_id,
        title=scenario["title"],
        expected_decision=scenario["expected_decision"],
        actual_decision=eval_output.decision,
        evaluation=eval_output,
        execution_evidence=execution_evidence,
        audit_event_id=eval_output.correlation_id,
        verified=verified
    )

@router.post("/reset")
def reset_demo_data(db: Session = Depends(get_db)):
    """
    Resets demo agent budgets, spend, and in-memory caches to guarantee 100% repeatability.
    """
    # Clear in-memory duplicate cache
    action_value_engine._execution_cache.clear()

    # Reset translation agent budget spend to 95¢ so Scenario 5 always hits budget limit
    trans_agent = db.query(Agent).filter(Agent.id == "translation-agent").first()
    if trans_agent:
        trans_agent.current_spend_cents = 95
        trans_agent.budget_limit_cents = 100
        trans_agent.trust_score = 90

    # Reset finance analyst agent
    fin_agent = db.query(Agent).filter(Agent.id == "finance-analyst-agent").first()
    if fin_agent:
        fin_agent.current_spend_cents = 120
        fin_agent.trust_score = 98

    # Reset workspace spend
    ws = db.query(Workspace).filter(Workspace.id == "ws-default").first()
    if ws:
        ws.current_spend_cents = 450

    db.commit()

    return {
        "status": "RESET_SUCCESSFUL",
        "message": "Demo data, agent budgets, and duplicate execution caches have been reset."
    }
