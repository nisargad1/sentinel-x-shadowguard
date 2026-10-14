import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from app.schemas.security import SecurityEvaluateRequest, SecurityEvaluateResponse
from app.services.intent_engine import IntentContractEngine
from app.services.hmac_service import HMACIntegrityService
from app.security.detectors.path_traversal import PathTraversalDetector
from app.security.detectors.command_injection import CommandInjectionDetector
from app.security.detectors.sql_injection import SQLInjectionDetector
from app.security.detectors.prompt_injection import PromptInjectionDetector
from app.sandbox.deception_fs import deception_fs
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog
from app.core.config import settings

class SecurityPolicyEvaluator:
    """
    Central Security Gateway orchestrator: evaluates intent, input attack vectors,
    integrity signatures, and deception routing.
    """

    @classmethod
    def evaluate(
        cls,
        request: SecurityEvaluateRequest,
        db: Optional[Session] = None,
        caller_ip: str = "127.0.0.1"
    ) -> SecurityEvaluateResponse:
        req_id = request.request_id or f"req-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()
        
        matched_rules = []
        highest_risk = 0
        decision = "ALLOW"
        explanation = "Request verified and approved by SENTINEL-X gateway."
        deception_active = False
        deception_payload = None
        event_type = "AUTHORIZED_ACCESS"
        severity = "LOW"

        # 1. HMAC Verification (if provided)
        hmac_status = True
        if request.hmac_signature and request.timestamp:
            payload_data = {"user_goal": request.user_goal, "tool_name": request.tool_name, "args": request.tool_arguments}
            valid, hmac_err = HMACIntegrityService.verify_request(
                payload_data,
                request.timestamp,
                req_id,
                request.hmac_signature
            )
            if not valid:
                hmac_status = False
                matched_rules.append(f"HMAC integrity failure: {hmac_err}")
                highest_risk = max(highest_risk, 90)
                decision = "DENY"
                event_type = "HMAC_TAMPER_DETECTED"
                severity = "HIGH"
                explanation = f"Security Gateway Blocked: {hmac_err}"

        # 2. Inspect all arguments for attack payloads
        arg_text_aggregate = ""
        for k, v in request.tool_arguments.items():
            arg_str = str(v)
            arg_text_aggregate += f" {arg_str}"

            # 2a. Path Traversal check
            pt_viol, pt_reason, pt_risk, should_deceive, virtual_tgt = PathTraversalDetector.inspect(arg_str)
            if pt_viol:
                matched_rules.append(pt_reason)
                highest_risk = max(highest_risk, pt_risk)
                event_type = "PATH_TRAVERSAL"
                severity = "HIGH"
                if should_deceive and settings.HONEYPOT_ENABLED:
                    deception_active = True
                    deception_payload = deception_fs.read_file(virtual_tgt)
                    decision = "DECEPTION_REDIRECT"
                    explanation = f"Host perimeter breach prevented. Intercepted path traversal and redirected to isolated Shadow Sandbox honeypot ({virtual_tgt})."
                else:
                    decision = "DENY"
                    explanation = f"Host perimeter protection: {pt_reason}"

            # 2b. Command Injection check
            ci_viol, ci_reason, ci_risk = CommandInjectionDetector.inspect(arg_str)
            if ci_viol:
                matched_rules.append(ci_reason)
                highest_risk = max(highest_risk, ci_risk)
                if decision != "DECEPTION_REDIRECT":
                    decision = "DENY"
                event_type = "COMMAND_INJECTION"
                severity = "CRITICAL"
                explanation = f"Command execution blocked: {ci_reason}"

            # 2c. SQL Injection check
            sqli_viol, sqli_reason, sqli_risk = SQLInjectionDetector.inspect(arg_str)
            if sqli_viol:
                matched_rules.append(sqli_reason)
                highest_risk = max(highest_risk, sqli_risk)
                if decision != "DECEPTION_REDIRECT":
                    decision = "DENY"
                event_type = "SQL_INJECTION"
                severity = "HIGH"
                explanation = f"Database injection blocked: {sqli_reason}"

        # 2d. Prompt Injection check on user goal and arguments
        pi_viol, pi_reason, pi_risk = PromptInjectionDetector.inspect(f"{request.user_goal} {arg_text_aggregate}")
        if pi_viol:
            matched_rules.append(pi_reason)
            highest_risk = max(highest_risk, pi_risk)
            if decision != "DECEPTION_REDIRECT":
                decision = "DENY"
            event_type = "PROMPT_INJECTION"
            severity = "HIGH"
            explanation = f"Prompt jailbreak / override blocked: {pi_reason}"

        # 3. Intent Drift Evaluation
        intent_res = IntentContractEngine.evaluate_intent(
            user_goal=request.user_goal,
            tool_name=request.tool_name,
            tool_arguments=request.tool_arguments
        )

        intent_match_score = intent_res.intent_match_score
        highest_risk = max(highest_risk, intent_res.risk_score)

        if intent_res.decision == "DENY" and decision not in ["DECEPTION_REDIRECT", "DENY"]:
            decision = "DENY"
            event_type = "INTENT_DRIFT"
            severity = "HIGH"
            explanation = intent_res.explanation
            matched_rules.extend(intent_res.matched_rules)
        elif intent_res.decision == "REQUIRE_APPROVAL" and decision == "ALLOW":
            decision = "REQUIRE_APPROVAL"
            event_type = "INTENT_DRIFT"
            severity = "MEDIUM"
            explanation = intent_res.explanation
            matched_rules.extend(intent_res.matched_rules)
        elif decision == "ALLOW":
            matched_rules.extend(intent_res.matched_rules)

        # Map final severity
        if highest_risk >= 85:
            severity = "CRITICAL"
        elif highest_risk >= 65:
            severity = "HIGH"
        elif highest_risk >= 35:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        # 4. Save Security Event & Audit Log to DB if session provided
        if db:
            sec_event = SecurityEvent(
                id=req_id,
                timestamp=datetime.now(timezone.utc),
                event_type=event_type,
                severity=severity,
                decision=decision,
                source="mcp_gateway",
                user_goal=request.user_goal,
                proposed_action=f"{request.tool_name}({json.dumps(request.tool_arguments)})",
                tool_name=request.tool_name,
                risk_score=highest_risk,
                intent_score=intent_match_score,
                payload_preview=str(request.tool_arguments)[:200],
                detection_rule=matched_rules[0] if matched_rules else "STANDARD_POLICY",
                remediation="Ensure tool requests conform to the User Goal Intent Contract and contain no path escape syntax." if decision != "ALLOW" else "None required",
                details_json=json.dumps({
                    "matched_rules": matched_rules,
                    "explanation": explanation,
                    "deception_active": deception_active
                })
            )
            db.add(sec_event)

            audit_log = AuditLog(
                request_id=req_id,
                timestamp=datetime.now(timezone.utc),
                caller_ip=caller_ip,
                action=f"TOOL_CALL:{request.tool_name}",
                outcome=decision,
                hmac_verified=hmac_status,
                sanitized_summary=f"Evaluated {request.tool_name} for goal '{request.user_goal[:50]}...'. Decision: {decision}.",
                metadata_json=json.dumps({"risk_score": highest_risk, "event_type": event_type})
            )
            db.add(audit_log)
            db.commit()

        return SecurityEvaluateResponse(
            request_id=req_id,
            decision=decision,
            risk_score=highest_risk,
            intent_match_score=intent_match_score,
            matched_rules=matched_rules,
            explanation=explanation,
            deception_active=deception_active,
            deception_payload=deception_payload,
            timestamp=now_iso
        )
