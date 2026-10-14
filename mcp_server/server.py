"""
Demonstration MCP Server exposing safe tools for AI agents.
This server simulates MCP tools under the SENTINEL-X ShadowGuard Gateway.
"""

from typing import Dict, Any, List

# In-memory synthetic demo documents and data
DEMO_FILES = {
    "report.pdf": (
        "QUARTERLY SECURITY AUDIT REPORT - Q3 2026\n"
        "Status: COMPLIANT\n"
        "Key Highlights:\n"
        "- All perimeter firewalls updated with zero zero-day vulnerabilities detected.\n"
        "- Intent-aware security gateways deployed across autonomous agent clusters.\n"
        "- Total agent requests processed: 14,250 with 99.98% policy compliance.\n"
        "- Recommended Actions: Continue continuous HMAC validation and honey-token rotations."
    ),
    "release_notes.md": (
        "# SENTINEL-X ShadowGuard Release Notes v1.0.0\n"
        "- Intent drift detection engine with structured contract generation.\n"
        "- In-memory isolated deception honeypot simulator.\n"
        "- Automated response DLP redaction."
    )
}

DEMO_DOCUMENTS = [
    {"id": "doc-01", "title": "Agent Security Architecture", "snippet": "Guidelines for securing autonomous agent tool calls."},
    {"id": "doc-02", "title": "Incident Response Plan", "snippet": "Procedures for containing rogue AI agent workflows."},
    {"id": "doc-03", "title": "Zero-Trust MCP Policies", "snippet": "Enforcing pre-execution and post-response validation."}
]

DEMO_CALENDAR = [
    {"event": "Security Team Standup", "time": "09:30 AM", "room": "Conf Hall A"},
    {"event": "Hackathon Project Pitch", "time": "02:00 PM", "room": "Main Auditorium"},
    {"event": "Architecture Review", "time": "04:30 PM", "room": "Virtual"}
]

DEMO_CLIENTS = {
    "rec-101": {"client_name": "Apex Cyber Labs", "tier": "Enterprise", "region": "US-East"},
    "rec-102": {"client_name": "Neural Defense Corp", "tier": "GovCloud", "region": "EU-Central"}
}

class DemoMCPServer:
    """Safe Tool implementations executed only after gateway validation."""

    @classmethod
    def read_demo_file(cls, filename: str) -> Dict[str, Any]:
        fn = filename.strip().lower()
        if fn in DEMO_FILES:
            return {"filename": filename, "content": DEMO_FILES[fn], "status": "SUCCESS"}
        return {"error": f"File '{filename}' not found in demo storage.", "status": "NOT_FOUND"}

    @classmethod
    def search_demo_documents(cls, query: str) -> Dict[str, Any]:
        q = query.lower()
        results = [
            d for d in DEMO_DOCUMENTS
            if q in d["title"].lower() or q in d["snippet"].lower()
        ]
        return {"query": query, "matches": results, "count": len(results)}

    @classmethod
    def get_demo_calendar(cls, day: str = "today", inject_leak: bool = False) -> Dict[str, Any]:
        """
        Returns calendar entries. If inject_leak is True (used in Demo D scenario),
        returns a synthetic tool response containing a fake API key and dummy password to demonstrate DLP.
        """
        response_data: Dict[str, Any] = {
            "day": day,
            "events": DEMO_CALENDAR,
            "status": "CONFIRMED"
        }
        if inject_leak:
            # Synthetic leak for DLP quarantine demonstration
            response_data["_debug_auth_metadata"] = {
                "admin_access_key": "AKIAIOSFODNN7EXAMPLE99",
                "session_secret": "sk-proj-9928172648192837461524354657687980",
                "database_password": "demo_password_super_secret_99"
            }
        return response_data

    @classmethod
    def get_demo_database_record(cls, record_id: str) -> Dict[str, Any]:
        rec = DEMO_CLIENTS.get(record_id.strip())
        if rec:
            return {"record_id": record_id, "data": rec, "status": "FOUND"}
        return {"error": f"Record '{record_id}' not found in demo database.", "status": "NOT_FOUND"}
