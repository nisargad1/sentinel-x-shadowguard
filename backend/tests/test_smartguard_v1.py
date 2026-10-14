import pytest
import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_scenario_1_legitimate_allow():
    res = client.post("/api/v1/scenarios/run", json={"scenario_id": "scenario_1"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "scenario_1"
    assert data["actual_decision"] == "ALLOW"
    assert data["verified"] is True
    assert data["execution_evidence"]["protected_tool_invoked"] is True
    assert data["evaluation"]["reason_code"] == "AUTHZ_PERMITTED"

def test_scenario_2_restricted_resource_block():
    res = client.post("/api/v1/scenarios/run", json={"scenario_id": "scenario_2"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "scenario_2"
    assert data["actual_decision"] == "BLOCK"
    assert data["verified"] is True
    # Crucial proof: The protected tool was NEVER invoked!
    assert data["execution_evidence"]["protected_tool_invoked"] is False
    assert data["evaluation"]["reason_code"] == "AUTHZ_RESOURCE_FORBIDDEN"

def test_scenario_3_redundant_search_optimize():
    # Scenario 3 tests duplicate detection and cost savings
    res = client.post("/api/v1/scenarios/run", json={"scenario_id": "scenario_3"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "scenario_3"
    assert data["actual_decision"] == "OPTIMIZE"
    assert data["verified"] is True
    assert data["evaluation"]["reason_code"] == "DUPLICATE_OPTIMIZED_CACHE_HIT"
    assert data["evaluation"]["cost_actual_cents"] == 0
    assert data["evaluation"]["savings_cents"] > 0

def test_scenario_4_sensitive_action_ask():
    res = client.post("/api/v1/scenarios/run", json={"scenario_id": "scenario_4"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "scenario_4"
    assert data["actual_decision"] == "ASK"
    assert data["verified"] is True
    assert data["evaluation"]["reason_code"] == "SENSITIVE_WRITE_REQUIRES_APPROVAL"
    # Action must NOT execute before approval!
    assert data["execution_evidence"]["protected_tool_invoked"] is False
    assert data["evaluation"]["approval_token"] is not None
    assert data["evaluation"]["approval_id"] is not None

def test_approval_workflow_execution_and_replay_resistance():
    # First trigger an ASK decision
    res = client.post("/api/v1/actions/propose", json={
        "workspace_id": "ws-default",
        "agent_id": "crm-automation-agent",
        "user_intent": "Update user account status",
        "tool_name": "update_customer_status",
        "action_name": "update",
        "parameters": {"customer_id": "CUST-TEST-01", "new_status": "DEACTIVATED"}
    })
    assert res.status_code == 200
    eval_data = res.json()
    assert eval_data["decision"] == "ASK"
    approval_id = eval_data["approval_id"]
    assert approval_id is not None

    # Step 2: Approve the action
    approve_res = client.post(f"/api/v1/approvals/{approval_id}/action", json={
        "action": "APPROVE",
        "approved_by": "secops-lead@enterprise.com",
        "reason": "Verified churn confirmation"
    })
    assert approve_res.status_code == 200
    approved_data = approve_res.json()
    assert approved_data["status"] == "APPROVED"
    assert approved_data["execution_result"] is not None
    assert approved_data["cost_actual_cents"] == 10

    # Step 3: Attempt REPLAY of the same approval request (Must FAIL!)
    replay_res = client.post(f"/api/v1/approvals/{approval_id}/action", json={
        "action": "APPROVE",
        "approved_by": "attacker@fake.com"
    })
    assert replay_res.status_code == 400
    assert "cannot be replayed" in replay_res.json()["detail"].lower()

def test_scenario_5_budget_exceeded_block():
    res = client.post("/api/v1/scenarios/run", json={"scenario_id": "scenario_5"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "scenario_5"
    assert data["actual_decision"] == "BLOCK"
    assert data["verified"] is True
    assert data["evaluation"]["reason_code"] == "BUDGET_EXCEEDED"
    assert data["execution_evidence"]["protected_tool_invoked"] is False

def test_scenario_6_prompt_injection_block():
    res = client.post("/api/v1/scenarios/run", json={"scenario_id": "scenario_6"})
    assert res.status_code == 200
    data = res.json()
    assert data["scenario_id"] == "scenario_6"
    assert data["actual_decision"] == "BLOCK"
    assert data["verified"] is True
    assert data["execution_evidence"]["protected_tool_invoked"] is False
    assert "PROMPT_INJECTION" in data["evaluation"]["reason_code"] or "AUTHZ" in data["evaluation"]["reason_code"]

def test_scenarios_reset():
    res = client.post("/api/v1/scenarios/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "RESET_SUCCESSFUL"

def test_proof_of_value_metrics():
    res = client.get("/api/v1/value-engine/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "total_proposed_actions" in data
    assert "net_savings_cents" in data
    assert "average_policy_latency_ms" in data
    assert data["currency"] == "USD"

def test_repeatable_benchmark():
    res = client.post("/api/v1/value-engine/benchmark")
    assert res.status_code == 200
    data = res.json()
    assert data["workload_actions"] == 20
    assert data["execution_mode"] == "empirical_measured_pipeline"
    assert data["baseline_unconstrained_cost_cents"] > data["enforced_smartguard_cost_cents"]
    assert data["net_measured_savings_cents"] > 0
    assert "savings_percentage" in data

def test_agent_trust_profiles():
    res = client.get("/api/v1/agents")
    assert res.status_code == 200
    agents = res.json()
    assert len(agents) > 0
    analyst = next((a for a in agents if "finance" in a["id"]), None)
    assert analyst is not None
    assert analyst["trust_score"] > 80
    assert "read_demo_file" in analyst["permitted_tools"]
