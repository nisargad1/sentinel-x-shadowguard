import asyncio
import json
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.models.security_event import SecurityEvent
from app.schemas.events import DashboardSummary, SecurityEventSchema, RiskTrendPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Telemetry"])

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns live aggregated security metrics, risk trend, and recent events.
    """
    total = db.query(SecurityEvent).count()
    allowed = db.query(SecurityEvent).filter(SecurityEvent.decision == "ALLOW").count()
    blocked = db.query(SecurityEvent).filter(SecurityEvent.decision.in_(["DENY", "REQUIRE_APPROVAL"])).count()
    
    # Attacks detected: all events where event_type is not AUTHORIZED_ACCESS
    attacks = db.query(SecurityEvent).filter(SecurityEvent.event_type != "AUTHORIZED_ACCESS").count()
    
    dlp_prevented = db.query(SecurityEvent).filter(SecurityEvent.event_type == "DLP_LEAK_PREVENTED").count()
    sandbox_act = db.query(SecurityEvent).filter(SecurityEvent.decision == "DECEPTION_REDIRECT").count()

    avg_risk = db.query(func.avg(SecurityEvent.risk_score)).scalar() or 0.0

    # System Health logic based on recent risk and blocked attacks
    if avg_risk > 70 or blocked > 20:
        health = "CRITICAL"
    elif avg_risk > 35 or blocked > 5:
        health = "ELEVATED_THREAT"
    else:
        health = "OPERATIONAL"

    # Compute Risk Trend for past 6 hourly windows
    now = datetime.now(timezone.utc)
    risk_trend: List[RiskTrendPoint] = []
    for i in range(5, -1, -1):
        window_start = now - timedelta(hours=i + 1)
        window_end = now - timedelta(hours=i)
        events_in_win = db.query(SecurityEvent).filter(
            SecurityEvent.timestamp >= window_start,
            SecurityEvent.timestamp <= window_end
        ).all()

        win_risk = (
            sum(e.risk_score for e in events_in_win) / len(events_in_win)
            if events_in_win else (15.0 if i > 2 else (25.0 if i == 2 else avg_risk))
        )
        win_blocked = sum(1 for e in events_in_win if e.decision in ["DENY", "DECEPTION_REDIRECT"])
        win_allowed = sum(1 for e in events_in_win if e.decision == "ALLOW")

        time_label = window_end.strftime("%H:%M")
        risk_trend.append(RiskTrendPoint(
            time=time_label,
            avg_risk=round(win_risk, 1),
            blocked_count=win_blocked,
            allowed_count=win_allowed
        ))

    recent_models = db.query(SecurityEvent).order_by(desc(SecurityEvent.timestamp)).limit(10).all()
    recent_events = []
    for r in recent_models:
        details_obj = None
        if r.details_json:
            try:
                details_obj = json.loads(r.details_json)
            except Exception:
                pass
        recent_events.append(SecurityEventSchema(
            id=r.id,
            timestamp=r.timestamp.isoformat() if r.timestamp else now.isoformat(),
            event_type=r.event_type,
            severity=r.severity,
            decision=r.decision,
            source=r.source or "mcp_gateway",
            user_goal=r.user_goal,
            proposed_action=r.proposed_action,
            tool_name=r.tool_name,
            risk_score=r.risk_score or 0,
            intent_score=r.intent_score or 1.0,
            payload_preview=r.payload_preview,
            detection_rule=r.detection_rule,
            remediation=r.remediation,
            details=details_obj
        ))

    return DashboardSummary(
        total_inspected=total,
        allowed_count=allowed,
        blocked_count=blocked,
        attacks_detected=attacks,
        dlp_leaks_prevented=dlp_prevented,
        sandbox_activations=sandbox_act,
        system_health=health,
        average_risk_score=round(avg_risk, 1),
        risk_trend=risk_trend,
        recent_events=recent_events
    )

@router.get("/events", response_model=List[SecurityEventSchema])
def list_events(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    decision: Optional[str] = None,
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Searchable and filterable security event feed.
    """
    query = db.query(SecurityEvent)
    if event_type:
        query = query.filter(SecurityEvent.event_type == event_type)
    if severity:
        query = query.filter(SecurityEvent.severity == severity)
    if decision:
        query = query.filter(SecurityEvent.decision == decision)

    events = query.order_by(desc(SecurityEvent.timestamp)).offset(offset).limit(limit).all()
    results = []
    for r in events:
        details_obj = None
        if r.details_json:
            try:
                details_obj = json.loads(r.details_json)
            except Exception:
                pass
        results.append(SecurityEventSchema(
            id=r.id,
            timestamp=r.timestamp.isoformat() if r.timestamp else datetime.now(timezone.utc).isoformat(),
            event_type=r.event_type,
            severity=r.severity,
            decision=r.decision,
            source=r.source or "mcp_gateway",
            user_goal=r.user_goal,
            proposed_action=r.proposed_action,
            tool_name=r.tool_name,
            risk_score=r.risk_score or 0,
            intent_score=r.intent_score or 1.0,
            payload_preview=r.payload_preview,
            detection_rule=r.detection_rule,
            remediation=r.remediation,
            details=details_obj
        ))
    return results

@router.get("/events/{event_id}", response_model=SecurityEventSchema)
def get_event(event_id: str, db: Session = Depends(get_db)):
    event = db.query(SecurityEvent).filter(SecurityEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail=f"Security event '{event_id}' not found")
    details_obj = None
    if event.details_json:
        try:
            details_obj = json.loads(event.details_json)
        except Exception:
            pass
    return SecurityEventSchema(
        id=event.id,
        timestamp=event.timestamp.isoformat() if event.timestamp else datetime.now(timezone.utc).isoformat(),
        event_type=event.event_type,
        severity=event.severity,
        decision=event.decision,
        source=event.source or "mcp_gateway",
        user_goal=event.user_goal,
        proposed_action=event.proposed_action,
        tool_name=event.tool_name,
        risk_score=event.risk_score or 0,
        intent_score=event.intent_score or 1.0,
        payload_preview=event.payload_preview,
        detection_rule=event.detection_rule,
        remediation=event.remediation,
        details=details_obj
    )

@router.get("/stream")
async def stream_live_events(request: Request, db: Session = Depends(get_db)):
    """
    Server-Sent Events (SSE) live telemetry feed for real-time dashboard updates.
    """
    async def event_generator():
        last_checked = datetime.now(timezone.utc) - timedelta(seconds=1)
        while True:
            if await request.is_disconnected():
                break

            # Poll for new events since last_checked
            new_events = db.query(SecurityEvent).filter(SecurityEvent.timestamp > last_checked).all()
            if new_events:
                last_checked = datetime.now(timezone.utc)
                for ev in new_events:
                    payload = {
                        "id": ev.id,
                        "event_type": ev.event_type,
                        "severity": ev.severity,
                        "decision": ev.decision,
                        "risk_score": ev.risk_score,
                        "timestamp": ev.timestamp.isoformat() if ev.timestamp else datetime.now(timezone.utc).isoformat()
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
            else:
                # Keep-alive heartbeat
                yield f": heartbeat\n\n"

            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
