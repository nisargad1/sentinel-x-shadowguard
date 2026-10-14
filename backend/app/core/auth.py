import hashlib
from typing import Optional
from fastapi import Header, HTTPException, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.smartguard import ApiKey, Workspace

def hash_api_key(raw_key: str) -> str:
    """Computes SHA-256 hash of API key for secure storage."""
    return hashlib.sha256(raw_key.strip().encode()).hexdigest()

def ensure_seed_api_keys(db: Session):
    """Ensures standard testing and production seed API keys exist in the database."""
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

def get_current_workspace(
    x_api_key: Optional[str] = Header(None, description="Workspace API Key"),
    workspace_id: Optional[str] = Query(None, description="Target Workspace ID"),
    db: Session = Depends(get_db)
) -> str:
    """
    Authenticates API requests and enforces workspace isolation:
      - Validates active status of provided API keys.
      - Rejects revoked or invalid keys with 401 Unauthorized.
      - Enforces strict tenant boundaries: callers cannot access another workspace.
      - Permits 'ws-default' without key only for local demo console usage.
    """
    ensure_seed_api_keys(db)
    target_ws = workspace_id or "ws-default"

    if x_api_key:
        hashed = hash_api_key(x_api_key)
        key_record = db.query(ApiKey).filter(ApiKey.hashed_secret == hashed).first()
        
        if not key_record:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key provided."
            )
        
        if not key_record.is_active:
            raise HTTPException(
                status_code=401,
                detail="API key has been revoked. Access denied."
            )
        
        # Enforce that key can only access its own bound workspace
        if workspace_id and workspace_id != key_record.workspace_id:
            raise HTTPException(
                status_code=403,
                detail=f"Forbidden: API key is bound to workspace '{key_record.workspace_id}' and cannot access workspace '{workspace_id}'."
            )
        
        return key_record.workspace_id

    # If no API key provided:
    if target_ws != "ws-default":
        raise HTTPException(
            status_code=401,
            detail=f"Authentication required: API key must be provided to access workspace '{target_ws}'."
        )

    return "ws-default"
