import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.schemas.mcp import MCPToolCallRequest, MCPToolCallResponse
from app.schemas.security import SecurityEvaluateRequest
from app.security.policy_evaluator import SecurityPolicyEvaluator
from app.security.detectors.dlp_inspector import DLPInspector
from app.models.security_event import SecurityEvent
from app.models.audit_log import AuditLog
from mcp_server.server import DemoMCPServer

class MCPGatewayProxy:
    """
    Sits directly between the AI Agent / Client and MCP Tools.
    Guarantees every request is inspected before execution and every response is inspected before returning.
    """

    @classmethod
    def execute_tool_call(
        cls,
        call_req: MCPToolCallRequest,
        db: Optional[Session] = None,
        caller_ip: str = "127.0.0.1"
    ) -> MCPToolCallResponse:
        req_id = call_req.request_id or f"mcp-{uuid.uuid4().hex[:12]}"
        now_iso = datetime.now(timezone.utc).isoformat()

        # Step 1: Pre-Execution Security Evaluation
        eval_req = SecurityEvaluateRequest(
            user_goal=call_req.user_goal,
            tool_name=call_req.tool_name,
            tool_arguments=call_req.arguments,
            caller_id=call_req.caller_id,
            request_id=req_id,
            timestamp=call_req.timestamp,
            hmac_signature=call_req.hmac_signature
        )

        eval_res = SecurityPolicyEvaluator.evaluate(eval_req, db=db, caller_ip=caller_ip)

        # Handle Deception Redirect (Honeypot Sandbox)
        if eval_res.decision == "DECEPTION_REDIRECT":
            return MCPToolCallResponse(
                request_id=req_id,
                decision="DECEPTION_REDIRECT",
                execution_success=True,
                tool_name=call_req.tool_name,
                result=eval_res.deception_payload,
                quarantined=False,
                deception_redirect=True,
                risk_score=eval_res.risk_score,
                intent_match_score=eval_res.intent_match_score,
                explanation=eval_res.explanation,
                timestamp=now_iso
            )

        # Handle Blocked Execution (Intent Drift or Injections)
        if eval_res.decision in ["DENY", "REQUIRE_APPROVAL"]:
            return MCPToolCallResponse(
                request_id=req_id,
                decision=eval_res.decision,
                execution_success=False,
                tool_name=call_req.tool_name,
                result={"error": "Tool execution blocked by SENTINEL-X Gateway Policy", "details": eval_res.explanation},
                quarantined=False,
                deception_redirect=False,
                risk_score=eval_res.risk_score,
                intent_match_score=eval_res.intent_match_score,
                explanation=eval_res.explanation,
                timestamp=now_iso
            )

        # Step 2: Execute MCP Tool (Only reached if verified ALLOW)
        tool_res = cls._dispatch_tool(call_req.tool_name, call_req.arguments)

        # Step 3: Post-Execution DLP Response Inspection
        contains_leak, categories, safe_output, dlp_risk = DLPInspector.inspect(tool_res)

        quarantined = False
        final_result = tool_res
        if contains_leak:
            quarantined = True
            final_result = safe_output
            dlp_explanation = f"DLP Quarantine Triggered: Sensitive tokens detected ({', '.join(categories)}). Unredacted output quarantined; safe sanitized payload delivered."
            
            # Log DLP Security Event
            if db:
                dlp_event = SecurityEvent(
                    id=f"dlp-{uuid.uuid4().hex[:12]}",
                    timestamp=datetime.now(timezone.utc),
                    event_type="DLP_LEAK_PREVENTED",
                    severity="HIGH",
                    decision="QUARANTINE",
                    source="dlp_inspector",
                    user_goal=call_req.user_goal,
                    proposed_action=f"{call_req.tool_name} response output",
                    tool_name=call_req.tool_name,
                    risk_score=dlp_risk,
                    intent_score=eval_res.intent_match_score,
                    payload_preview=DLPInspector.sanitize_for_logging(tool_res),
                    detection_rule=f"DLP_MATCH_{categories[0]}",
                    remediation="Tool returned synthetic credentials or secrets. Output quarantined and redacted.",
                    details_json=json.dumps({"detected_categories": categories, "quarantined": True})
                )
                db.add(dlp_event)

                audit_log = AuditLog(
                    request_id=req_id,
                    timestamp=datetime.now(timezone.utc),
                    caller_ip=caller_ip,
                    action=f"DLP_INSPECT:{call_req.tool_name}",
                    outcome="QUARANTINED",
                    hmac_verified=True,
                    sanitized_summary=f"Sensitive tokens redacted from {call_req.tool_name} response.",
                    metadata_json=json.dumps({"categories": categories})
                )
                db.add(audit_log)
                db.commit()

            return MCPToolCallResponse(
                request_id=req_id,
                decision="QUARANTINE",
                execution_success=True,
                tool_name=call_req.tool_name,
                result=final_result,
                quarantined=True,
                deception_redirect=False,
                risk_score=dlp_risk,
                intent_match_score=eval_res.intent_match_score,
                explanation=dlp_explanation,
                timestamp=now_iso
            )

        # Normal Clean Tool Execution
        return MCPToolCallResponse(
            request_id=req_id,
            decision="ALLOW",
            execution_success=True,
            tool_name=call_req.tool_name,
            result=final_result,
            quarantined=False,
            deception_redirect=False,
            risk_score=eval_res.risk_score,
            intent_match_score=eval_res.intent_match_score,
            explanation=eval_res.explanation,
            timestamp=now_iso
        )

    @classmethod
    def _dispatch_tool(cls, tool_name: str, args: Dict[str, Any]) -> Any:
        name = tool_name.strip()
        if name == "read_demo_file":
            filename = args.get("filename", "report.pdf")
            return DemoMCPServer.read_demo_file(filename)
        elif name == "search_demo_documents":
            query = args.get("query", "")
            return DemoMCPServer.search_demo_documents(query)
        elif name == "get_demo_calendar":
            day = args.get("day", "today")
            inject_leak = bool(args.get("inject_leak", False))
            return DemoMCPServer.get_demo_calendar(day=day, inject_leak=inject_leak)
        elif name == "get_demo_database_record":
            record_id = args.get("record_id", "rec-101")
            return DemoMCPServer.get_demo_database_record(record_id)
        else:
            return {"error": f"Tool '{tool_name}' not implemented in MCP demo server.", "status": "UNKNOWN_TOOL"}
