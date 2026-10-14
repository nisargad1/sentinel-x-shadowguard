from app.api.routes_dashboard import router as dashboard_router
from app.api.routes_security import router as security_router
from app.api.routes_sandbox import router as sandbox_router
from app.api.routes_intents import router as intents_router
from app.api.routes_audit import router as audit_router
from app.api.routes_mcp import router as mcp_router
from app.api.routes_demo import router as demo_router

__all__ = [
    "dashboard_router",
    "security_router",
    "sandbox_router",
    "intents_router",
    "audit_router",
    "mcp_router",
    "demo_router"
]
