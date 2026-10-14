from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.mcp import MCPToolCallRequest, MCPToolCallResponse
from app.services.mcp_service import MCPGatewayProxy

router = APIRouter(prefix="/mcp", tags=["MCP Tool Execution Gateway"])

@router.post("/call-tool", response_model=MCPToolCallResponse)
def execute_mcp_tool(
    call_req: MCPToolCallRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Executes an MCP tool call through the SENTINEL-X Security Gateway.
    Pre-execution: Evaluates intent drift, path traversal, injection payloads.
    Post-execution: Inspects response output for DLP token leaks and redacts if necessary.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    response = MCPGatewayProxy.execute_tool_call(call_req, db=db, caller_ip=client_ip)
    return response

@router.get("/tools")
def list_available_mcp_tools():
    """
    Lists demo MCP tools monitored and mediated by the gateway.
    """
    return {
        "gateway_status": "ONLINE",
        "protocol": "Model Context Protocol (MCP) v1.0",
        "registered_tools": [
            {
                "name": "read_demo_file",
                "description": "Reads authorized documents (e.g. report.pdf, release_notes.md) from demo storage.",
                "parameters": {"filename": "string"}
            },
            {
                "name": "search_demo_documents",
                "description": "Searches authorized demo knowledge base for relevant cybersecurity snippets.",
                "parameters": {"query": "string"}
            },
            {
                "name": "get_demo_calendar",
                "description": "Retrieves authorized schedule and calendar entries.",
                "parameters": {"day": "string", "inject_leak": "boolean (optional for DLP testing)"}
            },
            {
                "name": "get_demo_database_record",
                "description": "Fetches authorized client record by ID.",
                "parameters": {"record_id": "string"}
            }
        ]
    }
