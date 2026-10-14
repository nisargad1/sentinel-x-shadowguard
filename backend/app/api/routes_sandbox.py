import uuid
import json
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.sandbox.deception_fs import deception_fs
from app.security.detectors.path_traversal import PathTraversalDetector
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/sandbox", tags=["Shadow Deception Sandbox"])

class SandboxSimulateRequest(BaseModel):
    requested_path: str
    attack_category: Optional[str] = "PATH_TRAVERSAL"
    caller_id: Optional[str] = "honeypot_probe"

@router.post("/simulate")
def simulate_deception(
    req: SandboxSimulateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Simulates path traversal containment. Safely intercepts path,
    prevents host access, and returns isolated synthetic decoy files.
    """
    req_id = f"trap-{uuid.uuid4().hex[:12]}"
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Inspect the requested path
    is_viol, reason, risk, should_deceive, virtual_tgt = PathTraversalDetector.inspect(req.requested_path)
    
    # Return synthetic decoy content
    target = virtual_tgt or req.requested_path
    trap_content = deception_fs.read_file(target)

    # Record Deception Security Event
    sec_event = SecurityEvent(
        id=req_id,
        timestamp=datetime.now(timezone.utc),
        event_type="DECEPTION_ACTIVATED",
        severity="HIGH",
        decision="DECEPTION_REDIRECT",
        source="shadow_sandbox",
        user_goal=f"Exfiltrate '{req.requested_path}'",
        proposed_action=f"read_file('{req.requested_path}')",
        tool_name="read_file",
        risk_score=risk or 90,
        intent_score=0.1,
        payload_preview=f"Trapped path: {req.requested_path}",
        detection_rule="SANDBOX_HONEYPOT_REDIRECT",
        remediation="Attacker contained in in-memory deception filesystem. Host access isolated.",
        details_json=json.dumps({
            "virtual_target": target,
            "canary_signature": trap_content.get("canary_signature"),
            "is_simulated": True
        })
    )
    db.add(sec_event)

    audit = AuditLog(
        request_id=req_id,
        timestamp=datetime.now(timezone.utc),
        caller_ip=client_ip,
        action="SANDBOX_CONTAINMENT",
        outcome="DECEPTION_REDIRECT",
        hmac_verified=True,
        sanitized_summary=f"Intercepted traversal '{req.requested_path}'. Redirected to honeypot {target}.",
        metadata_json=json.dumps({"synthetic_target": target})
    )
    db.add(audit)
    db.commit()

    return {
        "sandbox_status": "ACTIVE_CONTAINMENT",
        "isolated_environment": "In-Memory Virtual Deception Filesystem",
        "real_filesystem_accessed": False,
        "intercepted_path": req.requested_path,
        "served_virtual_target": target,
        "content": trap_content["content"],
        "is_simulated": True,
        "risk_score": risk or 90,
        "explanation": "Threat neutralized. Attacker exfiltrating synthetic decoy canaries."
    }

@router.get("/status")
def get_sandbox_status():
    """
    Returns telemetry on the in-memory deception simulator and synthetic file catalog.
    """
    return {
        "enabled": True,
        "sandbox_mode": "IN_MEMORY_VIRTUAL_FS",
        "honeypot_canary_id": "CANARY-X9821-EXFIL-TRAP",
        "synthetic_files": [
            {"path": "/etc/passwd", "type": "unix_passwd_decoy", "description": "Synthetic root & canary accounts"},
            {"path": "/etc/shadow", "type": "unix_shadow_decoy", "description": "Simulated salt hashes"},
            {"path": "/fake_credentials.txt", "type": "cloud_decoy_keys", "description": "Canary AWS keys and webhooks"},
            {"path": "/fake_users.txt", "type": "user_registry_decoy", "description": "Synthetic compliance user list"},
            {"path": "/var/log/audit.log", "type": "audit_log_decoy", "description": "Simulated honeypot audit logs"}
        ]
    }
