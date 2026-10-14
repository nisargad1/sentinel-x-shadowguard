import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import engine, Base, SessionLocal
from app.api.routes_demo import seed_realistic_events
from app.models.security_event import SecurityEvent

Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    if db.query(SecurityEvent).count() == 0:
        seed_realistic_events(db)

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "SmartGuard" in data["gateway"]
    assert data["modules"]["intent_drift_engine"] == "ACTIVE"

def test_dashboard_summary_endpoint():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_inspected" in data
    assert "system_health" in data
    assert isinstance(data["risk_trend"], list)

def test_demo_scenario_a_legitimate():
    res = client.post("/api/demo/run-scenario", json={"scenario_id": "DEMO_A"})
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "ALLOW"
    assert data["execution_success"] is True
    assert data["result"]["status"] == "SUCCESS"
    assert "QUARTERLY SECURITY AUDIT REPORT" in data["result"]["content"]

def test_demo_scenario_b_intent_drift():
    res = client.post("/api/demo/run-scenario", json={"scenario_id": "DEMO_B"})
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "DENY"
    assert data["execution_success"] is False
    assert data["risk_score"] >= 70
    assert "Intent Drift Detected" in data["explanation"]

def test_demo_scenario_c_path_traversal_deception():
    res = client.post("/api/demo/run-scenario", json={"scenario_id": "DEMO_C"})
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "DECEPTION_REDIRECT"
    assert data["deception_redirect"] is True
    assert data["result"]["is_simulated"] is True
    assert "CANARY-SENTINEL-X-TRAP-VERIFIED" in data["result"]["canary_signature"]

def test_demo_scenario_d_dlp_quarantine():
    res = client.post("/api/demo/run-scenario", json={"scenario_id": "DEMO_D"})
    assert res.status_code == 200
    data = res.json()
    assert data["decision"] == "QUARANTINE"
    assert data["quarantined"] is True
    assert "[REDACTED_AWS_ACCESS_KEY]" in str(data["result"])
    assert "[REDACTED_PASSWORD_FIELD]" in str(data["result"])

def test_audit_logs_and_export():
    res = client.get("/api/audit-logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0

    res_exp = client.get("/api/audit-logs/export?format=json")
    assert res_exp.status_code == 200
    data = res_exp.json()
    assert "audit_report" in data
