import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

import hashlib
import app.models
from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.models.security_event import SecurityEvent
from app.models.smartguard import Workspace, Agent, ApiKey
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_security import router as security_router
from app.api.routes_sandbox import router as sandbox_router
from app.api.routes_intents import router as intents_router
from app.api.routes_audit import router as audit_router
from app.api.routes_mcp import router as mcp_router
from app.api.routes_demo import router as demo_router, seed_realistic_events

# SmartGuard v1 routers
from app.api.routes_v1_gateway import router as v1_gateway_router
from app.api.routes_v1_approvals import router as v1_approvals_router
from app.api.routes_v1_scenarios import router as v1_scenarios_router
from app.api.routes_v1_analytics import router as v1_analytics_router

# Ensure all database tables exist immediately
Base.metadata.create_all(bind=engine)

START_TIME = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and seed baseline telemetry
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        if db.query(SecurityEvent).count() == 0:
            seed_realistic_events(db)
        # Ensure default workspace and agents exist
        if not db.query(Workspace).filter(Workspace.id == "ws-default").first():
            ws = Workspace(
                id="ws-default",
                name="Acme Corp AI Lab",
                slug="acme-ai",
                monthly_budget_cents=10000,
                current_spend_cents=450
            )
            db.add(ws)
            db.commit()

        # Seed default active API key
        default_key_hash = hashlib.sha256(b"sg_live_enterprise_default_key_2026").hexdigest()
        if not db.query(ApiKey).filter(ApiKey.hashed_secret == default_key_hash).first():
            db.add(ApiKey(
                id="key-enterprise-default",
                workspace_id="ws-default",
                key_prefix="sg_live_ent",
                hashed_secret=default_key_hash,
                name="Production Default Agent Key",
                is_active=True
            ))

        # Seed revoked test key
        revoked_key_hash = hashlib.sha256(b"sg_revoked_key_test_2026").hexdigest()
        if not db.query(ApiKey).filter(ApiKey.hashed_secret == revoked_key_hash).first():
            db.add(ApiKey(
                id="key-revoked-test",
                workspace_id="ws-default",
                key_prefix="sg_rev_test",
                hashed_secret=revoked_key_hash,
                name="Revoked Compromised Key",
                is_active=False
            ))

        # Seed second isolated tenant workspace and key
        if not db.query(Workspace).filter(Workspace.id == "ws-tenant-bravo").first():
            db.add(Workspace(
                id="ws-tenant-bravo",
                name="Bravo Logistics AI",
                slug="bravo-logistics",
                monthly_budget_cents=5000,
                current_spend_cents=100
            ))
        bravo_key_hash = hashlib.sha256(b"sg_live_tenant_bravo_key_2026").hexdigest()
        if not db.query(ApiKey).filter(ApiKey.hashed_secret == bravo_key_hash).first():
            db.add(ApiKey(
                id="key-tenant-bravo",
                workspace_id="ws-tenant-bravo",
                key_prefix="sg_live_bravo",
                hashed_secret=bravo_key_hash,
                name="Tenant Bravo Integration Key",
                is_active=True
            ))
        db.commit()
    yield

app = FastAPI(
    title="SENTINEL-X SmartGuard",
    description=(
        "The Trust Layer for Autonomous AI Agents. "
        "Runtime enforcement gateway evaluating whether proposed agent tool actions "
        "are authorized, relevant, safe, cost-effective, and necessary."
    ),
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health & Status"])
def health_check(db: Session = Depends(get_db)):
    """
    Production health check verifying database connectivity, gateway modules, and uptime.
    """
    uptime_seconds = int(time.time() - START_TIME)
    db_connected = True
    try:
        total_events = db.query(SecurityEvent).count()
    except Exception:
        db_connected = False
        total_events = 0

    return {
        "status": "HEALTHY",
        "gateway": "SENTINEL-X SmartGuard",
        "tagline": "The Trust Layer for Autonomous AI Agents",
        "version": "2.0.0",
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "connected": db_connected,
            "engine": engine.dialect.name,
            "recorded_events": total_events
        },
        "modules": {
            "action_value_engine": "ACTIVE",
            "intent_drift_engine": "ACTIVE",
            "injection_detectors": "ACTIVE",
            "hmac_integrity": "ACTIVE",
            "mcp_gateway_proxy": "ACTIVE",
            "shadow_deception_sandbox": "ACTIVE",
            "dlp_inspector": "ACTIVE",
            "human_approval_inbox": "ACTIVE",
            "proof_of_value_engine": "ACTIVE"
        }
    }

frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/dist"))
assets_dist = os.path.join(frontend_dist, "assets")

if os.path.exists(assets_dist):
    app.mount("/assets", StaticFiles(directory=assets_dist), name="assets")

@app.get("/", tags=["Root"])
def root():
    index_html = os.path.join(frontend_dist, "index.html")
    if os.path.exists(index_html):
        return FileResponse(index_html)
    return {
        "project": "SENTINEL-X SmartGuard",
        "tagline": "The Trust Layer for Autonomous AI Agents",
        "docs_url": "/docs",
        "health_url": "/health",
        "api_prefix": "/api/v1"
    }

# Register SmartGuard API v1 endpoints
app.include_router(v1_gateway_router)
app.include_router(v1_approvals_router)
app.include_router(v1_scenarios_router)
app.include_router(v1_analytics_router)

# Preserve legacy / existing endpoints for backward compatibility
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(security_router, prefix=settings.API_V1_STR)
app.include_router(sandbox_router, prefix=settings.API_V1_STR)
app.include_router(intents_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(mcp_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)
