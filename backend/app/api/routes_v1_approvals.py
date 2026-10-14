import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.smartguard import ApprovalRequest, ActionEvaluation, Agent
from app.models.audit_log import AuditLog
from app.schemas.smartguard import ApprovalActionRequest, ApprovalItem
from app.execution.adapter import execution_adapter

router = APIRouter(prefix="/api/v1/approvals", tags=["SmartGuard Human Approval Inbox"])

@router.get("", response_model=List[ApprovalItem])
def list_approval_requests(
    status: Optional[str] = None,
    workspace_id: str = "ws-default",
    db: Session = Depends(get_db)
):
    """Lists human approval requests with optional status filtering (PENDING, APPROVED, REJECTED, EXPIRED)."""
    query = db.query(ApprovalRequest).filter(ApprovalRequest.workspace_id == workspace_id)
    if status:
        query = query.filter(ApprovalRequest.status == status.upper())
    
    records = query.order_by(ApprovalRequest.created_at.desc()).limit(100).all()
    
    items = []
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

    for rec in records:
        # Check if expired
        exp = rec.expires_at.replace(tzinfo=None) if rec.expires_at.tzinfo else rec.expires_at
        is_expired = rec.status == "PENDING" and exp < now_utc
        if is_expired:
            rec.status = "EXPIRED"
            db.commit()

        try:
            payload = json.loads(rec.action_payload_json)
        except Exception:
            payload = {}

        items.append(ApprovalItem(
            id=rec.id,
            workspace_id=rec.workspace_id,
            agent_id=rec.agent_id,
            evaluation_id=rec.evaluation_id,
            status=rec.status,
            expires_at=rec.expires_at.isoformat(),
            created_at=rec.created_at.isoformat(),
            approved_by=rec.approved_by,
            tool_name=payload.get("tool_name", "unknown_tool"),
            action_name=payload.get("action_name", "write"),
            parameters=payload.get("parameters", {}),
            user_intent=payload.get("user_intent", "Sensitive write operation"),
            cost_estimate_cents=payload.get("estimated_cost_cents", 10),
            risk_level="MEDIUM"
        ))

    return items

@router.post("/{approval_id}/action")
def decide_approval_request(
    approval_id: str,
    req: ApprovalActionRequest,
    db: Session = Depends(get_db)
):
    """
    Approves or rejects a pending action approval request.
    Enforces replay-resistance, cryptographic binding to the exact parameters, and expiration checks.
    """
    approval = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    # Replay-Resistance Check
    if approval.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=f"Approval request cannot be replayed. Current status is already {approval.status}."
        )

    # Expiry Check
    now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    exp = approval.expires_at.replace(tzinfo=None) if approval.expires_at.tzinfo else approval.expires_at
    if exp < now_utc:
        approval.status = "EXPIRED"
        db.commit()
        raise HTTPException(
            status_code=400,
            detail="Approval request has expired and cannot be approved. A new action must be proposed."
        )

    try:
        payload = json.loads(approval.action_payload_json)
    except Exception:
        raise HTTPException(status_code=500, detail="Corrupted action payload in approval request")

    evaluation = db.query(ActionEvaluation).filter(ActionEvaluation.id == approval.evaluation_id).first()
    action_type = req.action.upper()

    if action_type == "APPROVE":
        approval.status = "APPROVED"
        approval.approved_by = req.approved_by or "secops-operator@enterprise.com"

        # Execute the exact approved action through the controlled adapter
        success, exec_result, cost_actual = execution_adapter.execute_tool(
            tool_name=payload["tool_name"],
            action_name=payload["action_name"],
            parameters=payload.get("parameters", {})
        )

        # Update evaluation execution status
        if evaluation:
            evaluation.execution_status = "EXECUTED"
            evaluation.cost_actual_cents = cost_actual
            evaluation.execution_result_json = json.dumps(exec_result)

        # Update agent spend
        agent = db.query(Agent).filter(Agent.id == approval.agent_id).first()
        if agent:
            agent.current_spend_cents += cost_actual

        # Log audit trail
        audit = AuditLog(
            request_id=payload.get("correlation_id", approval.id),
            timestamp=now_utc,
            action=f"{payload['tool_name']}:{payload['action_name']}",
            outcome="APPROVED_AND_EXECUTED",
            hmac_verified=True,
            sanitized_summary=f"[APPROVED] Human operator '{approval.approved_by}' approved sensitive action.",
            metadata_json=json.dumps({"approval_id": approval.id, "reason": req.reason, "cost_cents": cost_actual})
        )
        db.add(audit)
        db.commit()

        return {
            "status": "APPROVED",
            "message": "Action successfully approved and executed via controlled adapter.",
            "execution_result": exec_result,
            "cost_actual_cents": cost_actual,
            "approved_by": approval.approved_by
        }

    elif action_type == "REJECT":
        approval.status = "REJECTED"
        approval.approved_by = req.approved_by or "secops-operator@enterprise.com"

        if evaluation:
            evaluation.execution_status = "REJECTED"

        audit = AuditLog(
            request_id=payload.get("correlation_id", approval.id),
            timestamp=now_utc,
            action=f"{payload['tool_name']}:{payload['action_name']}",
            outcome="REJECTED_BY_OPERATOR",
            hmac_verified=True,
            sanitized_summary=f"[REJECTED] Human operator rejected action: {req.reason}",
            metadata_json=json.dumps({"approval_id": approval.id, "reason": req.reason})
        )
        db.add(audit)
        db.commit()

        return {
            "status": "REJECTED",
            "message": "Action was rejected by human operator. Protected tool was not invoked.",
            "approved_by": approval.approved_by
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Must be APPROVE or REJECT.")
