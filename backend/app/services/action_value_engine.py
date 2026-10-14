import uuid
import time
import json
import fnmatch
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session

from app.models.smartguard import (
    Workspace,
    Agent,
    Policy,
    ActionEvaluation,
    ApprovalRequest,
)
from app.models.audit_log import AuditLog
from app.models.security_event import SecurityEvent
from app.schemas.smartguard import ActionProposeRequest, ActionEvaluationOutput
from app.security.detectors.path_traversal import PathTraversalDetector
from app.security.detectors.command_injection import CommandInjectionDetector
from app.security.detectors.sql_injection import SQLInjectionDetector
from app.security.detectors.prompt_injection import PromptInjectionDetector
from app.execution.adapter import execution_adapter

class ActionValueEngine:
    """
    Action Value Engine — The Core Differentiator of SENTINEL-X SmartGuard.
    Evaluates 5 dimensions:
      1. Intent Alignment
      2. Authorization
      3. Risk
      4. Cost
      5. Efficiency
    
    Produces 1 primary decision: ALLOW, OPTIMIZE, ASK, or BLOCK.
    """

    def __init__(self):
        self.path_traversal = PathTraversalDetector()
        self.command_injection = CommandInjectionDetector()
        self.sql_injection = SQLInjectionDetector()
        self.prompt_injection = PromptInjectionDetector()
        
        # In-memory execution cache for duplicate/idempotent calls (Query -> (timestamp, result, cost))
        self._execution_cache: Dict[str, Tuple[float, Any, int]] = {}
        self.CACHE_TTL_SECONDS = 60.0

    def _ensure_seed_entities(self, db: Session, workspace_id: str = "ws-default", agent_id: str = "finance-analyst-agent") -> Tuple[Workspace, Agent]:
        """Ensures the workspace and agent exist in the database with defaults."""
        ws = db.query(Workspace).filter(Workspace.id == workspace_id).first()
        if not ws:
            ws = Workspace(
                id=workspace_id,
                name="Acme Corp AI Lab",
                slug="acme-ai",
                monthly_budget_cents=10000, # $100.00
                current_spend_cents=450,    # $4.50
            )
            db.add(ws)
            db.commit()

        agent = db.query(Agent).filter(Agent.id == agent_id).first()
        if not agent:
            # Create agent with tailored default permissions based on ID
            if "crm" in agent_id:
                agent = Agent(
                    id=agent_id,
                    workspace_id=workspace_id,
                    name="CRM Automation Agent",
                    role="Customer Operations",
                    permitted_tools=json.dumps(["update_customer_status", "search_demo_documents"]),
                    permitted_resources=json.dumps(["customer_*", "CUST-*"]),
                    budget_limit_cents=3000,
                    current_spend_cents=200,
                    trust_score=94
                )
            elif "market" in agent_id or "research" in agent_id:
                agent = Agent(
                    id=agent_id,
                    workspace_id=workspace_id,
                    name="Market Research Agent",
                    role="Competitive Intelligence",
                    permitted_tools=json.dumps(["search_demo_documents", "read_demo_file"]),
                    permitted_resources=json.dumps(["*.pdf", "market_*", "pricing_*"]),
                    budget_limit_cents=2500,
                    current_spend_cents=150,
                    trust_score=97
                )
            elif "translation" in agent_id:
                agent = Agent(
                    id=agent_id,
                    workspace_id=workspace_id,
                    name="Document Translation Agent",
                    role="Localization",
                    permitted_tools=json.dumps(["translate_document", "read_demo_file"]),
                    permitted_resources=json.dumps(["doc_*", "*.txt"]),
                    budget_limit_cents=100, # $1.00 strict budget cap
                    current_spend_cents=95,  # $0.95 already spent (only $0.05 remaining!)
                    trust_score=90
                )
            elif "support" in agent_id:
                agent = Agent(
                    id=agent_id,
                    workspace_id=workspace_id,
                    name="Support Ticket Agent",
                    role="Customer Support",
                    permitted_tools=json.dumps(["read_demo_file"]),
                    permitted_resources=json.dumps(["ticket_*", "support_*", "doc_*"]),
                    budget_limit_cents=1500,
                    current_spend_cents=50,
                    trust_score=96
                )
            else: # Default finance analyst
                agent = Agent(
                    id=agent_id,
                    workspace_id=workspace_id,
                    name="Financial Analyst Agent",
                    role="Portfolio & Filing Analysis",
                    permitted_tools=json.dumps(["read_demo_file", "search_demo_documents", "get_demo_calendar"]),
                    permitted_resources=json.dumps(["report.pdf", "q3_report.pdf", "quarterly_*", "*.pdf"]),
                    budget_limit_cents=2000,
                    current_spend_cents=120,
                    trust_score=98
                )
            db.add(agent)
            db.commit()

        return ws, agent

    def evaluate_and_execute(self, db: Session, req: ActionProposeRequest) -> ActionEvaluationOutput:
        """
        Executes the 5-dimension Action Value Engine pipeline.
        Decides: ALLOW, OPTIMIZE, ASK, or BLOCK.
        """
        start_time = time.time()
        correlation_id = req.correlation_id or str(uuid.uuid4())
        evaluation_id = str(uuid.uuid4())
        
        ws, agent = self._ensure_seed_entities(db, req.workspace_id, req.agent_id)
        
        # Parse agent permissions
        try:
            permitted_tools = json.loads(agent.permitted_tools)
        except Exception:
            permitted_tools = []
        try:
            permitted_resources = json.loads(agent.permitted_resources)
        except Exception:
            permitted_resources = []

        params_str = json.dumps(req.parameters)
        target_resource = req.resource_id or req.parameters.get("filename") or req.parameters.get("table") or req.parameters.get("query") or ""

        # =====================================================================
        # 1. RISK & INJECTION SCANNING (Highest Precedence)
        # =====================================================================
        
        # Path Traversal Check
        is_traversal, details, risk_score, should_deceive, virtual_target = self.path_traversal.inspect(str(target_resource))
        if not is_traversal:
            for k, v in req.parameters.items():
                if isinstance(v, str):
                    t, _, _, _, _ = self.path_traversal.inspect(v)
                    if t:
                        is_traversal = True
                        break

        if is_traversal:
            # Trapped in In-Memory Deception Sandbox
            duration_ms = round((time.time() - start_time) * 1000, 2)
            success, result_data, cost_actual = execution_adapter.execute_tool(
                req.tool_name, req.action_name, req.parameters, is_sandbox=True
            )
            return self._record_evaluation(
                db=db,
                ws=ws,
                agent=agent,
                correlation_id=correlation_id,
                evaluation_id=evaluation_id,
                req=req,
                decision="OPTIMIZE",  # Deception containment redirect
                reason_code="PATH_TRAVERSAL_DECEPTION_CONTAINED",
                explanation=f"Directory traversal '{target_resource}' detected. Contained in isolated in-memory deception honeypot with zero host disk access.",
                risk_level="HIGH",
                risk_score=0.85,
                intent_score=0.10,
                cost_estimate=req.estimated_cost_cents or 2,
                cost_actual=0,
                savings=req.estimated_cost_cents or 2,
                optimization="IN_MEMORY_DECEPTION_HONEYPOT",
                execution_status="OPTIMIZED",
                execution_result=result_data,
                duration_ms=duration_ms
            )

        # Command Injection Check
        is_cmd, cmd_detail, cmd_risk = self.command_injection.inspect(params_str)
        if is_cmd:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return self._record_evaluation(
                db=db,
                ws=ws,
                agent=agent,
                correlation_id=correlation_id,
                evaluation_id=evaluation_id,
                req=req,
                decision="BLOCK",
                reason_code="COMMAND_INJECTION_DETECTED",
                explanation=f"Dangerous command injection signature detected: {cmd_detail}. Tool execution aborted.",
                risk_level="CRITICAL",
                risk_score=0.98,
                intent_score=0.0,
                cost_estimate=req.estimated_cost_cents or 10,
                cost_actual=0,
                savings=0,
                execution_status="BLOCKED",
                duration_ms=duration_ms
            )

        # SQL Injection Check
        is_sql, sql_detail, sql_risk = self.sql_injection.inspect(params_str)
        if is_sql:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return self._record_evaluation(
                db=db,
                ws=ws,
                agent=agent,
                correlation_id=correlation_id,
                evaluation_id=evaluation_id,
                req=req,
                decision="BLOCK",
                reason_code="SQL_INJECTION_DETECTED",
                explanation=f"SQL injection syntax detected: {sql_detail}. Tool execution aborted.",
                risk_level="CRITICAL",
                risk_score=0.95,
                intent_score=0.0,
                cost_estimate=req.estimated_cost_cents or 10,
                cost_actual=0,
                savings=0,
                execution_status="BLOCKED",
                duration_ms=duration_ms
            )

        # Prompt Injection in parameters or synthetic override attempts
        is_prompt_inj, p_details, p_risk = self.prompt_injection.inspect(params_str + " " + req.user_intent)
        if "dump_database" in req.tool_name or "override" in params_str.lower() or "credentials" in params_str.lower() or is_prompt_inj:
            if "password" in params_str.lower() or "dump" in req.tool_name or is_prompt_inj:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return self._record_evaluation(
                    db=db,
                    ws=ws,
                    agent=agent,
                    correlation_id=correlation_id,
                    evaluation_id=evaluation_id,
                    req=req,
                    decision="BLOCK",
                    reason_code="PROMPT_INJECTION_DETECTED",
                    explanation=f"Prompt injection or unauthorized credential exfiltration attempt blocked: {p_details}. Gateway enforce fail-closed boundary.",
                    risk_level="HIGH",
                    risk_score=0.92,
                    intent_score=0.05,
                    cost_estimate=req.estimated_cost_cents or 5,
                    cost_actual=0,
                    savings=0,
                    execution_status="BLOCKED",
                    duration_ms=duration_ms
                )

        # =====================================================================
        # 2. AUTHORIZATION & RESOURCE BOUNDARIES
        # =====================================================================
        
        # Check tool permission
        if req.tool_name not in permitted_tools:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return self._record_evaluation(
                db=db,
                ws=ws,
                agent=agent,
                correlation_id=correlation_id,
                evaluation_id=evaluation_id,
                req=req,
                decision="BLOCK",
                reason_code="AUTHZ_TOOL_FORBIDDEN",
                explanation=f"Agent '{agent.name}' is not authorized to invoke tool '{req.tool_name}'. Permitted tools: {permitted_tools}",
                risk_level="HIGH",
                risk_score=0.80,
                intent_score=0.10,
                cost_estimate=req.estimated_cost_cents or 5,
                cost_actual=0,
                savings=0,
                execution_status="BLOCKED",
                duration_ms=duration_ms
            )

        # Check resource permission (e.g. payroll_salaries.csv vs report.pdf)
        is_file_tool = req.tool_name in ["read_demo_file", "document_reader", "write_file"]
        is_restricted_keyword = any(forbidden in str(target_resource).lower() for forbidden in ["payroll", "salary", "salaries", "passwords", "creds", "/etc"])

        if target_resource:
            if is_restricted_keyword:
                resource_authorized = False
            elif not is_file_tool:
                # For search, calendar, or translation tools, general queries are permitted
                resource_authorized = True
            else:
                resource_authorized = False
                for pattern in permitted_resources:
                    if fnmatch.fnmatch(str(target_resource).lower(), pattern.lower()) or pattern in str(target_resource).lower():
                        resource_authorized = True
                        break

            if not resource_authorized:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return self._record_evaluation(
                    db=db,
                    ws=ws,
                    agent=agent,
                    correlation_id=correlation_id,
                    evaluation_id=evaluation_id,
                    req=req,
                    decision="BLOCK",
                    reason_code="AUTHZ_RESOURCE_FORBIDDEN",
                    explanation=f"Resource '{target_resource}' is strictly outside agent '{agent.name}' authorized permissions. Protected tool was not invoked.",
                    risk_level="HIGH",
                    risk_score=0.75,
                    intent_score=0.15,
                    cost_estimate=req.estimated_cost_cents or 2,
                    cost_actual=0,
                    savings=0,
                    execution_status="BLOCKED",
                    duration_ms=duration_ms
                )

        # =====================================================================
        # 3. SENSITIVE WRITE ACTION -> HUMAN APPROVAL (ASK)
        # =====================================================================
        is_sensitive_write = (
            req.action_name in ["write", "update", "delete", "deactivate", "modify", "drop"]
            or "update_" in req.tool_name
            or "delete_" in req.tool_name
            or req.parameters.get("new_status") == "DEACTIVATED"
        )

        if is_sensitive_write:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            # Create cryptographic approval token
            nonce = str(uuid.uuid4())
            token_raw = f"{correlation_id}:{req.tool_name}:{params_str}:{nonce}"
            token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
            
            approval = ApprovalRequest(
                id=str(uuid.uuid4()),
                workspace_id=ws.id,
                agent_id=agent.id,
                evaluation_id=evaluation_id,
                token_hash=token_hash,
                status="PENDING",
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=15),
                action_payload_json=json.dumps({
                    "tool_name": req.tool_name,
                    "action_name": req.action_name,
                    "parameters": req.parameters,
                    "user_intent": req.user_intent,
                    "estimated_cost_cents": req.estimated_cost_cents or 10,
                    "correlation_id": correlation_id
                })
            )
            db.add(approval)
            db.commit()

            return self._record_evaluation(
                db=db,
                ws=ws,
                agent=agent,
                correlation_id=correlation_id,
                evaluation_id=evaluation_id,
                req=req,
                decision="ASK",
                reason_code="SENSITIVE_WRITE_REQUIRES_APPROVAL",
                explanation=f"Action '{req.tool_name}:{req.action_name}' modifies sensitive customer/system state. Execution paused pending human operator review.",
                risk_level="MEDIUM",
                risk_score=0.55,
                intent_score=0.85,
                cost_estimate=req.estimated_cost_cents or 10,
                cost_actual=0,
                savings=0,
                execution_status="PENDING_APPROVAL",
                approval_token=token_hash,
                approval_id=approval.id,
                duration_ms=duration_ms
            )

        # =====================================================================
        # 4. COST & BUDGET CONSTRAINTS
        # =====================================================================
        estimated_cost = req.estimated_cost_cents or 2
        # Default translation tool has higher cost
        if "translate" in req.tool_name:
            estimated_cost = 50

        if (agent.current_spend_cents + estimated_cost) > agent.budget_limit_cents:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            return self._record_evaluation(
                db=db,
                ws=ws,
                agent=agent,
                correlation_id=correlation_id,
                evaluation_id=evaluation_id,
                req=req,
                decision="BLOCK",
                reason_code="BUDGET_EXCEEDED",
                explanation=f"Action cost ({estimated_cost}¢) exceeds remaining agent budget limit ({agent.budget_limit_cents - agent.current_spend_cents}¢ remaining of {agent.budget_limit_cents}¢).",
                risk_level="MEDIUM",
                risk_score=0.50,
                intent_score=0.90,
                cost_estimate=estimated_cost,
                cost_actual=0,
                savings=0,
                execution_status="BLOCKED",
                duration_ms=duration_ms
            )

        # =====================================================================
        # 5. EFFICIENCY & DUPLICATE OPTIMIZATION
        # =====================================================================
        cache_key = f"{agent.id}:{req.tool_name}:{params_str}"
        now_ts = time.time()
        
        if cache_key in self._execution_cache:
            prev_ts, cached_result, original_cost = self._execution_cache[cache_key]
            if (now_ts - prev_ts) < self.CACHE_TTL_SECONDS:
                duration_ms = round((time.time() - start_time) * 1000, 2)
                return self._record_evaluation(
                    db=db,
                    ws=ws,
                    agent=agent,
                    correlation_id=correlation_id,
                    evaluation_id=evaluation_id,
                    req=req,
                    decision="OPTIMIZE",
                    reason_code="DUPLICATE_OPTIMIZED_CACHE_HIT",
                    explanation=f"Redundant identical query detected within {int(now_ts - prev_ts)}s. Served from verified safe cache, avoiding external tool invocation.",
                    risk_level="LOW",
                    risk_score=0.02,
                    intent_score=1.0,
                    cost_estimate=original_cost,
                    cost_actual=0,
                    savings=original_cost,
                    optimization="IDEMPOTENT_CACHE_REUSE",
                    execution_status="OPTIMIZED",
                    execution_result=cached_result,
                    duration_ms=duration_ms
                )

        # =====================================================================
        # 6. ALLOW — ALL CONSTRAINTS SATISFIED
        # =====================================================================
        success, result_data, cost_actual = execution_adapter.execute_tool(
            req.tool_name, req.action_name, req.parameters
        )
        duration_ms = round((time.time() - start_time) * 1000, 2)
        
        # Cache safe read/search results for optimization
        if req.action_name in ["read", "execute", "query"] and success:
            self._execution_cache[cache_key] = (now_ts, result_data, cost_actual)

        # Deduct budget atomically
        agent.current_spend_cents += cost_actual
        ws.current_spend_cents += cost_actual
        db.commit()

        return self._record_evaluation(
            db=db,
            ws=ws,
            agent=agent,
            correlation_id=correlation_id,
            evaluation_id=evaluation_id,
            req=req,
            decision="ALLOW",
            reason_code="AUTHZ_PERMITTED",
            explanation=f"Action satisfies all applicable policies, resource allowlists, and budget constraints. Successfully executed through controlled adapter.",
            risk_level="LOW",
            risk_score=0.05,
            intent_score=1.0,
            cost_estimate=estimated_cost,
            cost_actual=cost_actual,
            savings=0,
            execution_status="EXECUTED",
            execution_result=result_data,
            duration_ms=duration_ms
        )

    def _record_evaluation(
        self,
        db: Session,
        ws: Workspace,
        agent: Agent,
        correlation_id: str,
        evaluation_id: str,
        req: ActionProposeRequest,
        decision: str,
        reason_code: str,
        explanation: str,
        risk_level: str,
        risk_score: float,
        intent_score: float,
        cost_estimate: int,
        cost_actual: int,
        savings: int,
        execution_status: str,
        duration_ms: float,
        optimization: Optional[str] = None,
        execution_result: Optional[Any] = None,
        approval_token: Optional[str] = None,
        approval_id: Optional[str] = None
    ) -> ActionEvaluationOutput:
        """Persists evaluation, audit log, security event, and updates trust scores."""
        ts_now = datetime.now(timezone.utc)
        
        # 1. ActionEvaluation record
        eval_record = ActionEvaluation(
            id=evaluation_id,
            workspace_id=ws.id,
            agent_id=agent.id,
            correlation_id=correlation_id,
            user_intent=req.user_intent,
            tool_name=req.tool_name,
            action_name=req.action_name,
            parameters_json=json.dumps(req.parameters),
            decision=decision,
            reason_code=reason_code,
            explanation=explanation,
            risk_score=risk_score,
            risk_level=risk_level,
            cost_estimate_cents=cost_estimate,
            cost_actual_cents=cost_actual,
            savings_cents=savings,
            optimization_applied=optimization,
            execution_status=execution_status,
            execution_result_json=json.dumps(execution_result) if execution_result else None,
            duration_ms=duration_ms,
            timestamp=ts_now
        )
        db.add(eval_record)

        # 2. AuditLog record
        audit = AuditLog(
            id=str(uuid.uuid4()),
            request_id=correlation_id,
            timestamp=ts_now,
            action=f"{req.tool_name}:{req.action_name}",
            outcome=decision,
            hmac_verified=True,
            sanitized_summary=f"[{decision}] {reason_code} - {explanation[:120]}",
            metadata_json=json.dumps({
                "agent_id": agent.id,
                "workspace_id": ws.id,
                "cost_cents": cost_actual,
                "savings_cents": savings,
                "risk_score": risk_score
            })
        )
        db.add(audit)

        # 3. SecurityEvent if blocked or high risk
        if decision == "BLOCK" or risk_level in ["HIGH", "CRITICAL"]:
            sec_event = SecurityEvent(
                id=str(uuid.uuid4()),
                timestamp=ts_now,
                event_type=reason_code,
                severity=risk_level,
                decision=decision,
                source=f"smartguard_agent:{agent.id}",
                user_goal=req.user_intent,
                proposed_action=f"{req.tool_name}({json.dumps(req.parameters)})",
                tool_name=req.tool_name,
                risk_score=int(risk_score * 100),
                intent_score=intent_score,
                payload_preview=json.dumps(req.parameters)[:200],
                detection_rule=reason_code,
                remediation="Enforce strict least-privilege tool allowlists and verify prompt integrity.",
                details_json=json.dumps({"correlation_id": correlation_id, "explanation": explanation})
            )
            db.add(sec_event)

        # Update Agent Trust Score dynamically
        if decision == "ALLOW":
            agent.trust_score = min(100, agent.trust_score + 1)
        elif decision == "BLOCK":
            agent.trust_score = max(20, agent.trust_score - 10)
        elif decision == "OPTIMIZE":
            agent.trust_score = min(100, agent.trust_score + 1)

        db.commit()

        return ActionEvaluationOutput(
            correlation_id=correlation_id,
            evaluation_id=evaluation_id,
            decision=decision,
            reason_code=reason_code,
            explanation=explanation,
            risk_level=risk_level,
            risk_score=risk_score,
            intent_alignment_score=intent_score,
            cost_estimate_cents=cost_estimate,
            cost_actual_cents=cost_actual,
            savings_cents=savings,
            optimization_applied=optimization,
            execution_status=execution_status,
            execution_result=execution_result,
            approval_token=approval_token,
            approval_id=approval_id,
            duration_ms=duration_ms,
            timestamp=ts_now.isoformat()
        )

action_value_engine = ActionValueEngine()
