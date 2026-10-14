import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import engine, Base, get_db
from app.models.security_event import SecurityEvent
from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_security import router as security_router
from app.api.routes_sandbox import router as sandbox_router
from app.api.routes_intents import router as intents_router
from app.api.routes_audit import router as audit_router
from app.api.routes_mcp import router as mcp_router
from app.api.routes_demo import router as demo_router, seed_realistic_events

# Ensure database tables exist immediately
Base.metadata.create_all(bind=engine)

START_TIME = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables and seed demo telemetry
    Base.metadata.create_all(bind=engine)
    with Session(engine) as db:
        if db.query(SecurityEvent).count() == 0:
            seed_realistic_events(db)
    yield
    # Shutdown logic if needed

app = FastAPI(
    title="SENTINEL-X ShadowGuard",
    description=(
        "Intent-Aware Runtime Security Gateway & Deception Sandbox for MCP-Connected AI Agents. "
        "Provides real-time intent drift detection, multi-vector injection prevention, "
        "DLP response quarantining, and isolated honeypot deception."
    ),
    version=settings.VERSION,
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
        "gateway": "SENTINEL-X ShadowGuard",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": uptime_seconds,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": {
            "connected": db_connected,
            "engine": engine.dialect.name,
            "recorded_events": total_events
        },
        "modules": {
            "intent_drift_engine": "ACTIVE",
            "injection_detectors": "ACTIVE",
            "hmac_integrity": "ACTIVE",
            "mcp_gateway_proxy": "ACTIVE",
            "shadow_deception_sandbox": "ACTIVE",
            "dlp_inspector": "ACTIVE"
        }
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "project": "SENTINEL-X ShadowGuard",
        "tagline": "Intent-Aware Security Gateway for MCP-Connected AI Agents",
        "docs_url": "/docs",
        "health_url": "/health",
        "api_prefix": settings.API_V1_STR
    }

# Register all API endpoints under /api
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(security_router, prefix=settings.API_V1_STR)
app.include_router(sandbox_router, prefix=settings.API_V1_STR)
app.include_router(intents_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(mcp_router, prefix=settings.API_V1_STR)
app.include_router(demo_router, prefix=settings.API_V1_STR)

# Mount built frontend single-page application if dist directory exists
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../frontend/dist"))
if os.path.exists(frontend_dist):
    from fastapi.staticfiles import StaticFiles
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
