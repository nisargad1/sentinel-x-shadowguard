import uuid
import re
from typing import Dict, Any, List, Tuple
from app.schemas.intent import IntentContract, IntentEvaluateResponse

class IntentContractEngine:
    """
    Generates structured Intent Contracts from original user goals and validates
    proposed AI agent tool actions against defined contracts and security policies.
    """

    # Prohibited action keywords that violate least privilege
    GLOBAL_PROHIBITED_ACTIONS = [
        "delete", "drop", "destroy", "execute_shell", "spawn_process",
        "dump_credentials", "exfiltrate", "modify_system", "bypass_guardrail"
    ]

    # Sensitive resource tokens that require explicit permission in user goal
    HIGH_RISK_RESOURCES = [
        "password", "credential", "secret", "token", "shadow", "private_key",
        "database_dump", "auth", "admin_config"
    ]

    @classmethod
    def generate_contract(cls, user_goal: str) -> IntentContract:
        """
        Parses the user goal to construct an immutable Intent Contract.
        """
        goal_lower = user_goal.lower()
        contract_id = f"cntr-{uuid.uuid4().hex[:12]}"

        # 1. Extract permitted resources from goal
        permitted_resources = []
        # Match filenames like report.pdf, data.csv, doc.md, calendar, etc.
        file_matches = re.findall(r"\b[\w\-.]+\.(?:pdf|csv|txt|docx|json|md|yaml)\b", goal_lower)
        permitted_resources.extend(file_matches)

        if "calendar" in goal_lower:
            permitted_resources.append("calendar")
        if "schedule" in goal_lower:
            permitted_resources.append("schedule")
        if "document" in goal_lower or "report" in goal_lower:
            if "report.pdf" not in permitted_resources:
                permitted_resources.append("report.pdf")
        if "database" in goal_lower or "client" in goal_lower:
            permitted_resources.append("client_records")

        # 2. Extract permitted actions
        permitted_actions = ["read", "get"]
        if any(w in goal_lower for w in ["search", "find", "query"]):
            permitted_actions.append("search")
        if any(w in goal_lower for w in ["summarize", "analyze", "explain"]):
            permitted_actions.append("summarize")
            permitted_actions.append("read")
        if any(w in goal_lower for w in ["schedule", "calendar"]):
            permitted_actions.extend(["calendar", "get_calendar"])

        # 3. Compile prohibited actions
        prohibited_actions = list(cls.GLOBAL_PROHIBITED_ACTIONS)
        # If user only asked to read/summarize, write/delete are prohibited
        if "delete" not in goal_lower and "remove" not in goal_lower:
            prohibited_actions.extend(["delete_file", "truncate_data"])
        if "write" not in goal_lower and "save" not in goal_lower:
            prohibited_actions.extend(["overwrite_file", "write_file"])

        risk_constraints = {
            "max_risk_tolerance": 40,
            "forbid_path_traversal": True,
            "forbid_credential_access": True,
            "require_resource_match": True
        }

        return IntentContract(
            contract_id=contract_id,
            user_goal=user_goal,
            permitted_resources=permitted_resources if permitted_resources else ["report.pdf", "documents"],
            permitted_actions=permitted_actions,
            prohibited_actions=prohibited_actions,
            risk_constraints=risk_constraints
        )

    @classmethod
    def evaluate_intent(
        cls,
        user_goal: str,
        tool_name: str,
        tool_arguments: Dict[str, Any]
    ) -> IntentEvaluateResponse:
        """
        Calculates intent match score (0.0 - 1.0) and evaluates drift against the contract.
        Explicit policy violations override any lexical similarity score.
        """
        contract = cls.generate_contract(user_goal)
        matched_rules: List[str] = []
        violations: List[str] = []
        risk_score = 0

        # Extract target resource from arguments
        target_resource = ""
        for k in ["filename", "path", "file", "query", "record_id", "resource"]:
            if k in tool_arguments and isinstance(tool_arguments[k], str):
                target_resource = tool_arguments[k].lower().strip()
                break

        # Check 1: Action alignment
        tool_lower = tool_name.lower()
        tool_clean = tool_lower.replace("_demo_", "_")
        action_allowed = False
        for act in contract.permitted_actions:
            if act in tool_lower or act in tool_clean or (act in ["read", "get"] and any(prefix in tool_lower for prefix in ["read", "get", "fetch", "check", "view"])):
                action_allowed = True
                matched_rules.append(f"Action '{act}' permitted by contract")
                break

        if not action_allowed:
            # Check if explicitly prohibited
            for prob in contract.prohibited_actions:
                if prob in tool_lower:
                    violations.append(f"Tool '{tool_name}' matches prohibited action '{prob}'")
                    risk_score += 45
                    break
            if not violations:
                violations.append(f"Tool action '{tool_name}' not in permitted action list: {contract.permitted_actions}")
                risk_score += 25

        # Check 2: Resource scope alignment
        resource_allowed = False
        if not target_resource:
            # Tool has no target file/resource, e.g. get_calendar
            if "calendar" in tool_lower and "calendar" in contract.permitted_resources:
                resource_allowed = True
                matched_rules.append("Calendar resource matches contract")
            elif "search" in tool_lower and "documents" in contract.permitted_resources:
                resource_allowed = True
                matched_rules.append("General search scope permitted")
        else:
            # Check high-risk resources (passwords, credentials, etc.)
            for hr in cls.HIGH_RISK_RESOURCES:
                if hr in target_resource and hr not in user_goal.lower():
                    violations.append(f"Unauthorized access to high-risk resource '{target_resource}'")
                    risk_score += 60
                    break

            # Check if resource matches permitted resources
            for allowed_res in contract.permitted_resources:
                if allowed_res in target_resource or target_resource in allowed_res:
                    resource_allowed = True
                    matched_rules.append(f"Resource '{target_resource}' matches permitted contract resource '{allowed_res}'")
                    break

            if not resource_allowed and not any(hr in target_resource for hr in cls.HIGH_RISK_RESOURCES):
                violations.append(f"Resource '{target_resource}' not found in user goal contract: {contract.permitted_resources}")
                risk_score += 35

        # Check 3: Calculate deterministic Intent Match Score
        # Formula: Base score 1.0 minus penalties for unpermitted actions and unpermitted resources
        match_score = 1.0
        if not action_allowed:
            match_score -= 0.45
        if not resource_allowed and target_resource:
            match_score -= 0.45
        match_score = max(0.0, min(1.0, round(match_score, 2)))

        # Determine Decision
        if violations:
            decision = "DENY"
            explanation = f"Intent Drift Detected: {'; '.join(violations)}."
            risk_score = min(100, max(risk_score, 75))
        elif match_score < 0.65:
            decision = "REQUIRE_APPROVAL"
            explanation = f"Ambiguous action alignment (score {match_score:.2f}). Security policy requires human authorization."
            risk_score = max(risk_score, 40)
        else:
            decision = "ALLOW"
            explanation = f"Action verified: Tool '{tool_name}' and target resource conform to User Intent Contract '{contract.contract_id}'."
            risk_score = min(risk_score, 15)

        return IntentEvaluateResponse(
            contract=contract,
            decision=decision,
            intent_match_score=match_score,
            risk_score=risk_score,
            explanation=explanation,
            matched_rules=matched_rules if not violations else violations
        )
