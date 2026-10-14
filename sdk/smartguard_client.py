"""
SENTINEL-X SmartGuard Python SDK
The Trust Layer for Autonomous AI Agents

Usage:
    from smartguard_client import SmartGuardClient

    client = SmartGuardClient(base_url="http://localhost:8000")
    
    # Propose an action before executing
    decision = client.propose_action(
        agent_id="finance-analyst-agent",
        user_intent="Summarize Q3 earnings report",
        tool_name="read_demo_file",
        parameters={"filename": "report.pdf"}
    )
    
    if decision["decision"] == "ALLOW":
        print("Action authorized and executed:", decision["execution_result"])
    elif decision["decision"] == "OPTIMIZE":
        print("Action optimized via safe cache:", decision["execution_result"])
    elif decision["decision"] == "ASK":
        print("Action requires human approval. Token:", decision["approval_token"])
    elif decision["decision"] == "BLOCK":
        print("Action blocked by gateway:", decision["explanation"])
"""

import urllib.request
import urllib.error
import json
from typing import Dict, Any, Optional

class SmartGuardClient:
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "SmartGuard-Python-SDK/2.0"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        data = json.dumps(payload).encode("utf-8") if payload else None
        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                res_body = resp.read().decode("utf-8")
                return json.loads(res_body)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            try:
                err_json = json.loads(error_body)
                raise RuntimeError(f"SmartGuard API error ({e.code}): {err_json.get('detail', error_body)}")
            except Exception:
                raise RuntimeError(f"SmartGuard API error ({e.code}): {error_body}")
        except Exception as e:
            raise RuntimeError(f"Failed to connect to SmartGuard Gateway at {self.base_url}: {str(e)}")

    def propose_action(
        self,
        agent_id: str,
        user_intent: str,
        tool_name: str,
        action_name: str = "execute",
        parameters: Optional[Dict[str, Any]] = None,
        workspace_id: str = "ws-default",
        estimated_cost_cents: int = 0
    ) -> Dict[str, Any]:
        """Submits a proposed tool action to the SmartGuard runtime gateway."""
        payload = {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "user_intent": user_intent,
            "tool_name": tool_name,
            "action_name": action_name,
            "parameters": parameters or {},
            "estimated_cost_cents": estimated_cost_cents
        }
        return self._request("POST", "/api/v1/actions/propose", payload)

    def get_pending_approvals(self, workspace_id: str = "ws-default") -> list:
        """Retrieves pending human approval items."""
        return self._request("GET", f"/api/v1/approvals?workspace_id={workspace_id}&status=PENDING")

    def decide_approval(self, approval_id: str, approve: bool, approved_by: str = "operator@corp.com", reason: str = "Approved") -> Dict[str, Any]:
        """Approves or rejects an approval request."""
        action_str = "APPROVE" if approve else "REJECT"
        return self._request("POST", f"/api/v1/approvals/{approval_id}/action", {
            "action": action_str,
            "approved_by": approved_by,
            "reason": reason
        })

    def get_proof_of_value_metrics(self, workspace_id: str = "ws-default") -> Dict[str, Any]:
        """Fetches measured Proof of Value savings and telemetry."""
        return self._request("GET", f"/api/v1/value-engine/metrics?workspace_id={workspace_id}")
