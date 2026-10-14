import time
from fastapi import APIRouter, Response, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db, check_db_health
from app.core.cache import distributed_cache
from app.models.smartguard import ActionEvaluation, Agent
from app.core.config import settings

router = APIRouter(tags=["Production Telemetry & Observability"])

@router.get("/metrics")
def get_prometheus_metrics(db: Session = Depends(get_db)):
    """
    Exposes Prometheus-formatted metrics for Kubernetes scraping, Grafana, and Datadog.
    """
    # 1. Decision counts
    decisions = db.query(ActionEvaluation.decision, func.count(ActionEvaluation.id)).group_by(ActionEvaluation.decision).all()
    decision_map = dict(decisions)
    allow_cnt = decision_map.get("ALLOW", 0)
    optimize_cnt = decision_map.get("OPTIMIZE", 0)
    ask_cnt = decision_map.get("ASK", 0)
    block_cnt = decision_map.get("BLOCK", 0)
    total_evals = allow_cnt + optimize_cnt + ask_cnt + block_cnt

    # 2. Latency
    avg_latency_ms = db.query(func.avg(ActionEvaluation.duration_ms)).scalar() or 1.5
    avg_latency_sec = round(float(avg_latency_ms) / 1000.0, 5)

    # 3. Active agents
    active_agents = db.query(Agent).count()

    # 4. Cache statistics
    cache_stats = distributed_cache.stats()
    hits = cache_stats.get("hits", 0)
    misses = cache_stats.get("misses", 0)

    # Build Prometheus text format output
    lines = [
        "# HELP smartguard_up Sentinel-X SmartGuard gateway operational status",
        "# TYPE smartguard_up gauge",
        "smartguard_up 1",
        "",
        "# HELP smartguard_requests_total Total evaluated autonomous AI agent tool actions",
        "# TYPE smartguard_requests_total counter",
        f'smartguard_requests_total{{decision="ALLOW"}} {allow_cnt}',
        f'smartguard_requests_total{{decision="OPTIMIZE"}} {optimize_cnt}',
        f'smartguard_requests_total{{decision="ASK"}} {ask_cnt}',
        f'smartguard_requests_total{{decision="BLOCK"}} {block_cnt}',
        f'smartguard_requests_total{{decision="ALL"}} {total_evals}',
        "",
        "# HELP smartguard_evaluation_duration_seconds Average runtime policy evaluation duration in seconds",
        "# TYPE smartguard_evaluation_duration_seconds gauge",
        f"smartguard_evaluation_duration_seconds {avg_latency_sec}",
        "",
        "# HELP smartguard_cache_hits_total High-throughput deduplication cache hit counter",
        "# TYPE smartguard_cache_hits_total counter",
        f"smartguard_cache_hits_total {hits}",
        f"smartguard_cache_misses_total {misses}",
        "",
        "# HELP smartguard_active_agents Registered autonomous agent fleet size",
        "# TYPE smartguard_active_agents gauge",
        f"smartguard_active_agents {active_agents}"
    ]

    return Response(content="\n".join(lines) + "\n", media_type="text/plain; version=0.0.4")

@router.get("/health/live")
def liveness_probe():
    """Kubernetes liveness probe: returns 200 if gateway process is responsive."""
    return {"status": "alive", "timestamp": time.time()}

@router.get("/health/ready")
def readiness_probe(db: Session = Depends(get_db)):
    """Kubernetes readiness probe: verifies database connection pool and internal subsystem readiness."""
    db_ok = check_db_health()
    if not db_ok:
        raise HTTPException(status_code=503, detail="Database pool not ready")
    return {
        "status": "ready",
        "database_pool": "HEALTHY",
        "cache_backend": distributed_cache.backend_type,
        "timestamp": time.time()
    }
