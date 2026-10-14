import json
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.events import AuditLogSchema

router = APIRouter(prefix="/audit-logs", tags=["Audit & Compliance"])

@router.get("", response_model=List[AuditLogSchema])
def list_audit_logs(
    search: Optional[str] = None,
    outcome: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Searchable audit history with cryptographic verification status and sanitized summaries.
    """
    query = db.query(AuditLog)
    if outcome:
        query = query.filter(AuditLog.outcome == outcome)
    if search:
        query = query.filter(
            (AuditLog.sanitized_summary.ilike(f"%{search}%")) |
            (AuditLog.action.ilike(f"%{search}%")) |
            (AuditLog.request_id.ilike(f"%{search}%"))
        )

    logs = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(limit).all()
    results = []
    for log in logs:
        meta_dict = None
        if log.metadata_json:
            try:
                meta_dict = json.loads(log.metadata_json)
            except Exception:
                pass
        results.append(AuditLogSchema(
            id=log.id,
            request_id=log.request_id,
            timestamp=log.timestamp.isoformat() if log.timestamp else datetime.now(timezone.utc).isoformat(),
            caller_ip=log.caller_ip or "127.0.0.1",
            action=log.action,
            outcome=log.outcome,
            hmac_verified=log.hmac_verified,
            sanitized_summary=log.sanitized_summary,
            metadata=meta_dict
        ))
    return results

@router.get("/export")
def export_audit_logs(format: str = "json", db: Session = Depends(get_db)):
    """
    Exports sanitized audit report for compliance inspections.
    """
    logs = db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(500).all()
    export_data = []
    for log in logs:
        export_data.append({
            "id": log.id,
            "request_id": log.request_id,
            "timestamp": log.timestamp.isoformat() if log.timestamp else "",
            "caller_ip": log.caller_ip,
            "action": log.action,
            "outcome": log.outcome,
            "hmac_verified": log.hmac_verified,
            "sanitized_summary": log.sanitized_summary
        })

    if format.lower() == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["id", "request_id", "timestamp", "caller_ip", "action", "outcome", "hmac_verified", "sanitized_summary"])
        writer.writeheader()
        writer.writerows(export_data)
        return Response(content=output.getvalue(), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=sentinel-x-audit-report.csv"})

    return Response(
        content=json.dumps({"audit_report": export_data, "exported_at": datetime.now(timezone.utc).isoformat()}, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=sentinel-x-audit-report.json"}
    )
