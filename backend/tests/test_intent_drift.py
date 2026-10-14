import pytest
from app.services.intent_engine import IntentContractEngine

def test_legitimate_intent_contract_match():
    user_goal = "Summarize report.pdf for the quarterly meeting."
    tool_name = "read_demo_file"
    tool_args = {"filename": "report.pdf"}

    result = IntentContractEngine.evaluate_intent(user_goal, tool_name, tool_args)
    assert result.decision == "ALLOW"
    assert result.intent_match_score >= 0.85
    assert result.risk_score <= 20
    assert "report.pdf" in result.contract.permitted_resources

def test_intent_drift_unauthorized_resource():
    user_goal = "Summarize report.pdf for the quarterly meeting."
    tool_name = "read_demo_file"
    tool_args = {"filename": "passwords.txt"}

    result = IntentContractEngine.evaluate_intent(user_goal, tool_name, tool_args)
    assert result.decision == "DENY"
    assert result.intent_match_score < 0.65
    assert result.risk_score >= 70
    assert "Intent Drift Detected" in result.explanation

def test_prohibited_action_override():
    user_goal = "Check report.pdf"
    tool_name = "delete_file"
    tool_args = {"filename": "report.pdf"}

    result = IntentContractEngine.evaluate_intent(user_goal, tool_name, tool_args)
    assert result.decision == "DENY"
    assert "prohibited action" in result.explanation.lower()
