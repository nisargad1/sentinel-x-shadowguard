import time
import uuid
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.security import (
    SecurityEvaluateRequest,
    SecurityEvaluateResponse,
    ResponseInspectRequest,
    ResponseInspectResponse,
    HMACVerifyRequest,
    HMACVerifyResponse
)
from app.security.policy_evaluator import SecurityPolicyEvaluator
from app.security.detectors.dlp_inspector import DLPInspector
from app.services.hmac_service import HMACIntegrityService

router = APIRouter(prefix="/security", tags=["Security Gateway Evaluation"])

@router.post("/evaluate", response_model=SecurityEvaluateResponse)
def evaluate_request(
    eval_req: SecurityEvaluateRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Evaluates an agent's proposed tool action against intent contracts,
    path traversal, command injection, SQL injection, and HMAC integrity.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    response = SecurityPolicyEvaluator.evaluate(eval_req, db=db, caller_ip=client_ip)
    return response

@router.post("/inspect-response", response_model=ResponseInspectResponse)
def inspect_tool_response(req: ResponseInspectRequest):
    """
    Inspects tool responses before returning to the AI agent.
    Detects API keys, passwords, and sensitive tokens. Returns sanitized/redacted payload.
    """
    req_id = req.request_id or f"dlp-{uuid.uuid4().hex[:12]}"
    contains_leak, categories, safe_output, risk = DLPInspector.inspect(req.tool_output)

    remediation = (
        "Response contained sensitive secrets. Payload has been quarantined and masked before agent ingestion."
        if contains_leak else "No sensitive patterns identified in response payload."
    )

    return ResponseInspectResponse(
        request_id=req_id,
        contains_leak=contains_leak,
        quarantined=contains_leak,
        detected_categories=categories,
        safe_output=safe_output if req.redact_sensitive else req.tool_output,
        risk_score=risk,
        remediation=remediation
    )

@router.post("/verify-signature", response_model=HMACVerifyResponse)
def verify_hmac_signature(req: HMACVerifyRequest):
    """
    Verifies HMAC-SHA256 signature for canonical request, checking timestamp expiration and replay.
    """
    valid, reason = HMACIntegrityService.verify_request(
        payload=req.payload,
        timestamp=req.timestamp,
        nonce=req.nonce,
        provided_signature=req.signature
    )
    return HMACVerifyResponse(
        valid=valid,
        error_reason=reason,
        timestamp=int(time.time())
    )

@router.post("/generate-signature")
def generate_hmac_signature(payload: Dict[str, Any], nonce: Optional[str] = None):
    """
    Developer utility endpoint to generate valid HMAC signatures for testing and agent integrations.
    """
    ts = int(time.time())
    n = nonce or f"nonce-{uuid.uuid4().hex[:10]}"
    sig = HMACIntegrityService.generate_signature(payload, ts, n)
    return {
        "timestamp": ts,
        "nonce": n,
        "signature": sig,
        "secret_length": len(HMACIntegrityService.get_secret())
    }
