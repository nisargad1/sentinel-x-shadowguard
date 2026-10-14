import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog
from app.schemas.mcp import MCPToolCallRequest, MCPToolCallResponse
from app.services.mcp_service import MCPGatewayProxy

router = APIRouter(prefix="/demo", tags=["Hackathon Demo Scenarios"])

class ScenarioRequest(BaseModel):
    scenario_id: str  # "DEMO_A", "DEMO_B", "DEMO_C", "DEMO_D"

@router.post("/run-scenario", response_model=MCPToolCallResponse)
def run_scenario(
    req: ScenarioRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Executes one of the 4 mandatory hackathon scenarios against the actual security gateway.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    scen = req.scenario_id.upper()

    if scen == "DEMO_A":
        # Legitimate authorized request
        call_req = MCPToolCallRequest(
            user_goal="Summarize report.pdf for the quarterly security briefing.",
            tool_name="read_demo_file",
            arguments={"filename": "report.pdf"},
            caller_id="hackathon_judge_agent"
        )
        return MCPGatewayProxy.execute_tool_call(call_req, db=db, caller_ip=client_ip)

    elif scen == "DEMO_B":
        # Intent drift and unauthorized file exfiltration attempt
        call_req = MCPToolCallRequest(
            user_goal="Summarize report.pdf for the quarterly security briefing.",
            tool_name="read_demo_file",
            arguments={"filename": "passwords.txt"},
            caller_id="compromised_agent"
        )
        return MCPGatewayProxy.execute_tool_call(call_req, db=db, caller_ip=client_ip)

    elif scen == "DEMO_C":
        # Path traversal attack redirected to safe deception sandbox honeypot
        call_req = MCPToolCallRequest(
            user_goal="Analyze report.pdf",
            tool_name="read_demo_file",
            arguments={"filename": "../../../etc/passwd"},
            caller_id="adversary_probe"
        )
        return MCPGatewayProxy.execute_tool_call(call_req, db=db, caller_ip=client_ip)

    elif scen == "DEMO_D":
        # Sensitive response containing synthetic API key and password
        call_req = MCPToolCallRequest(
            user_goal="Check security team calendar for today's hackathon standup.",
            tool_name="get_demo_calendar",
            arguments={"day": "today", "inject_leak": True},
            caller_id="calendar_agent"
        )
        return MCPGatewayProxy.execute_tool_call(call_req, db=db, caller_ip=client_ip)

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown scenario '{req.scenario_id}'. Valid scenarios are DEMO_A, DEMO_B, DEMO_C, DEMO_D."
        )

@router.post("/reset")
def reset_demo_database(
    x_admin_token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Resets the database and seeds realistic baseline events for presentation.
    Protected by admin token or enabled in development.
    """
    if settings.ENVIRONMENT != "development" and x_admin_token != settings.DEMO_RESET_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized: invalid or missing demo reset token.")

    # Clear existing events
    db.query(SecurityEvent).delete()
    db.query(AuditLog).delete()
    db.commit()

    # Seed baseline demonstration events
    seed_realistic_events(db)

    return {
        "status": "RESET_SUCCESSFUL",
        "message": "Security events and audit logs reset to baseline hackathon demonstration state."
    }

def seed_realistic_events(db: Session):
    """Seeds a rich set of realistic security events representing historical traffic."""
    now = datetime.now(timezone.utc)
    baseline_events = [
        SecurityEvent(
            id=f"seed-{uuid.uuid4().hex[:10]}",
            timestamp=now - timedelta(minutes=45),
            event_type="AUTHORIZED_ACCESS",
            severity="LOW",
            decision="ALLOW",
            source="mcp_gateway",
            user_goal="Summarize release notes for version 1.0",
            proposed_action="read_demo_file({'filename': 'release_notes.md'})",
            tool_name="read_demo_file",
            risk_score=10,
            intent_score=1.0,
            payload_preview="filename: release_notes.md",
            detection_rule="STANDARD_POLICY",
            remediation="None required",
            details_json=json.dumps({"explanation": "Matches user goal contract"})
        ),
        SecurityEvent(
            id=f"seed-{uuid.uuid4().hex[:10]}",
            timestamp=now - timedelta(minutes=32),
            event_type="INTENT_DRIFT",
            severity="HIGH",
            decision="DENY",
            source="mcp_gateway",
            user_goal="Summarize report.pdf",
            proposed_action="read_demo_file({'filename': 'company_passwords.xlsx'})",
            tool_name="read_demo_file",
            risk_score=85,
            intent_score=0.2,
            payload_preview="filename: company_passwords.xlsx",
            detection_rule="INTENT_DRIFT_UNAUTHORIZED_RESOURCE",
            remediation="Enforce least privilege contract on agent tool calls.",
            details_json=json.dumps({"violation": "Unauthorized access to credentials"})
        ),
        SecurityEvent(
            id=f"seed-{uuid.uuid4().hex[:10]}",
            timestamp=now - timedelta(minutes=20),
            event_type="DECEPTION_ACTIVATED",
            severity="CRITICAL",
            decision="DECEPTION_REDIRECT",
            source="shadow_sandbox",
            user_goal="Probe system configuration",
            proposed_action="read_demo_file({'filename': '../../../../etc/shadow'})",
            tool_name="read_demo_file",
            risk_score=95,
            intent_score=0.0,
            payload_preview="filename: ../../../../etc/shadow",
            detection_rule="PATH_TRAVERSAL_HONEYPOT_REDIRECT",
            remediation="Contained in virtual deception sandbox with canary tokens.",
            details_json=json.dumps({"canary_signature": "CANARY-X9821-EXFIL-TRAP", "is_simulated": True})
        ),
        SecurityEvent(
            id=f"seed-{uuid.uuid4().hex[:10]}",
            timestamp=now - timedelta(minutes=10),
            event_type="DLP_LEAK_PREVENTED",
            severity="HIGH",
            decision="QUARANTINE",
            source="dlp_inspector",
            user_goal="Retrieve calendar entries",
            proposed_action="get_demo_calendar({'day': 'today'})",
            tool_name="get_demo_calendar",
            risk_score=92,
            intent_score=0.95,
            payload_preview="[REDACTED_AWS_ACCESS_KEY] [REDACTED_PASSWORD_FIELD]",
            detection_rule="DLP_MATCH_AWS_ACCESS_KEY",
            remediation="Sensitive tokens quarantined and redacted from agent stream.",
            details_json=json.dumps({"detected": ["AWS_ACCESS_KEY", "PASSWORD_FIELD"]})
        )
    ]

    for ev in baseline_events:
        db.add(ev)
        db.add(AuditLog(
            request_id=ev.id,
            timestamp=ev.timestamp,
            caller_ip="127.0.0.1",
            action=f"EVALUATE:{ev.tool_name}",
            outcome=ev.decision,
            hmac_verified=True,
            sanitized_summary=f"Historical audit entry for {ev.event_type} (Risk: {ev.risk_score}).",
            metadata_json=ev.details_json
        ))

    db.commit()
