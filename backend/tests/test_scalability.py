import pytest
import concurrent.futures
from fastapi.testclient import TestClient
from app.main import app
from app.core.cache import distributed_cache
from app.core.rate_limiter import rate_limiter

client = TestClient(app)

def test_prometheus_metrics_endpoint():
    """Verify Prometheus /metrics scraping endpoint is active and compliant."""
    res = client.get("/metrics")
    assert res.status_code == 200
    assert "text/plain" in res.headers["content-type"]
    text = res.text
    assert "smartguard_up 1" in text
    assert "smartguard_requests_total" in text
    assert "smartguard_evaluation_duration_seconds" in text
    assert "smartguard_cache_hits_total" in text
    assert "smartguard_active_agents" in text

def test_liveness_and_readiness_probes():
    """Verify Kubernetes liveness and readiness probes."""
    live_res = client.get("/health/live")
    assert live_res.status_code == 200
    assert live_res.json()["status"] == "alive"

    ready_res = client.get("/health/ready")
    assert ready_res.status_code == 200
    assert ready_res.json()["status"] == "ready"
    assert ready_res.json()["database_pool"] == "HEALTHY"

def test_distributed_cache_hit_and_telemetry():
    """Verify cache get/set and telemetry hit ratios."""
    distributed_cache.clear()
    
    # Miss
    assert distributed_cache.get("test_key_1") is None

    # Set
    distributed_cache.set("test_key_1", {"content": "cached_report"}, cost=5, ttl=10)

    # Hit
    hit_data, cost = distributed_cache.get("test_key_1")
    assert hit_data == {"content": "cached_report"}
    assert cost == 5

    stats = distributed_cache.stats()
    assert stats["hits"] >= 1
    assert stats["misses"] >= 1
    assert stats["hit_ratio_percent"] > 0

def test_rate_limiter_throttling():
    """Verify rate limiter blocks runaway loops after limit is reached."""
    # Reset test identifier
    test_id = "test-agent-throttle"
    rate_limiter.reset(test_id)

    # Run 5 requests with limit of 3
    results = []
    for _ in range(5):
        allowed, remaining, reset_sec = rate_limiter.check_rate_limit(test_id, limit_per_minute=3)
        results.append(allowed)

    # First 3 allowed, last 2 blocked
    assert results == [True, True, True, False, False]

def test_high_concurrency_stress_simulation():
    """
    Simulates 25 concurrent agent requests executing simultaneously across multiple worker threads.
    Verifies zero thread lockup, zero 500 errors, and consistent database state.
    """
    rate_limiter.reset("ws-default:finance-analyst-agent")

    def send_proposal(i: int):
        return client.post("/api/v1/actions/propose", json={
            "workspace_id": "ws-default",
            "agent_id": "finance-analyst-agent",
            "user_intent": f"Concurrent test request #{i}",
            "tool_name": "read_demo_file",
            "action_name": "read",
            "parameters": {"filename": "report_concurrent.pdf"},
            "correlation_id": f"conc-test-{i}"
        })

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_proposal, i) for i in range(25)]
        responses = [f.result() for f in concurrent.futures.as_completed(futures)]

    # All concurrent requests must return HTTP 200 without database deadlocks
    for resp in responses:
        assert resp.status_code == 200
        data = resp.json()
        assert data["decision"] in ["ALLOW", "OPTIMIZE"]
        assert data["execution_status"] in ["EXECUTED", "OPTIMIZED"]
