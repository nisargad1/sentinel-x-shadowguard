import logging
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.auth import get_current_workspace
from app.schemas.smartguard import ActionProposeRequest, ActionEvaluationOutput
from app.services.action_value_engine import action_value_engine
from app.models.smartguard import ActionEvaluation

logger = logging.getLogger("sentinel.gateway")
router = APIRouter(prefix="/api/v1/actions", tags=["SmartGuard Runtime Gateway"])

@router.post("/propose", response_model=ActionEvaluationOutput)
def propose_and_evaluate_action(
    req: ActionProposeRequest,
    x_api_key: Optional[str] = Header(None, description="Optional Workspace API Key"),
    db: Session = Depends(get_db)
):
    """
    Evaluates an autonomous AI agent's proposed tool action against 5 dimensions:
      1. Intent alignment
      2. Authorization
      3. Risk
      4. Cost
      5. Efficiency
      
    Returns exactly one primary decision: ALLOW, OPTIMIZE, ASK, or BLOCK.
    """
    # Enforce API key authentication and workspace binding
    ws_id = get_current_workspace(x_api_key=x_api_key, workspace_id=req.workspace_id, db=db)
    req.workspace_id = ws_id

    try:
        result = action_value_engine.evaluate_and_execute(db, req)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Internal evaluation error: {str(e)}", exc_info=True)
        # Fail-closed and do not expose internal stack or DB traces
        raise HTTPException(
            status_code=500,
            detail="Action Value Engine encountered an internal error. Request aborted fail-closed for safety."
        )

@router.get("/{evaluation_id}")
def get_action_evaluation(
    evaluation_id: str,
    x_api_key: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Retrieves an action evaluation record and its execution evidence with workspace tenant isolation."""
    ev = db.query(ActionEvaluation).filter(ActionEvaluation.id == evaluation_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Action evaluation not found")
    
    # Enforce workspace check
    ws_id = get_current_workspace(x_api_key=x_api_key, workspace_id=ev.workspace_id, db=db)
    if ev.workspace_id != ws_id:
        raise HTTPException(status_code=403, detail="Forbidden: Cannot access evaluations from another workspace.")

    return {
        "id": ev.id,
        "workspace_id": ev.workspace_id,
        "agent_id": ev.agent_id,
        "correlation_id": ev.correlation_id,
        "user_intent": ev.user_intent,
        "tool_name": ev.tool_name,
        "action_name": ev.action_name,
        "decision": ev.decision,
        "reason_code": ev.reason_code,
        "explanation": ev.explanation,
        "risk_level": ev.risk_level,
        "risk_score": ev.risk_score,
        "cost_estimate_cents": ev.cost_estimate_cents,
        "cost_actual_cents": ev.cost_actual_cents,
        "savings_cents": ev.savings_cents,
        "execution_status": ev.execution_status,
        "execution_result": ev.execution_result_json,
        "duration_ms": ev.duration_ms,
        "timestamp": ev.timestamp.isoformat()
    }
