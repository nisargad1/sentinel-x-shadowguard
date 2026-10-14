# SENTINEL-X SHADOWGUARD
### Intent-Aware Runtime Security Gateway & Deception Sandbox for MCP AI Agents

[![Tests](https://img.shields.io/badge/Tests-22%20Passed-brightgreen?style=flat-square)](backend/tests)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?style=flat-square)](backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)](frontend)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square)](frontend)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE)

---

## 🚀 Live Public Deployment & Demo

- **Live Frontend Dashboard:** [https://carrier-advancement-lenses-fda.trycloudflare.com/](https://carrier-advancement-lenses-fda.trycloudflare.com/)
- **Interactive Swagger API Documentation:** [https://carrier-advancement-lenses-fda.trycloudflare.com/docs](https://carrier-advancement-lenses-fda.trycloudflare.com/docs)
- **Backend Health Endpoint:** [https://carrier-advancement-lenses-fda.trycloudflare.com/health](https://carrier-advancement-lenses-fda.trycloudflare.com/health)

---

## 1. Project Overview

**SENTINEL-X ShadowGuard** is an intent-aware runtime security gateway designed specifically for Model Context Protocol (MCP) connected autonomous AI agents.

As AI agents gain access to tools and execute actions autonomously, traditional perimeter defenses fail to prevent semantic threats:
- **Intent Drift:** An agent directed to summarize a public document is tricked into accessing password vaults or database dumps.
- **Perimeter Breakout:** Malicious arguments execute directory traversals (`../../etc/passwd`) against host infrastructure.
- **Data Leakage in Tool Responses:** Database tools return raw tokens or internal API keys back into the LLM context.

**SENTINEL-X ShadowGuard** interposes directly between the AI agent and MCP tools. It enforces dynamic Intent Contracts, prevents multi-vector injections, isolates attacks in an in-memory virtual deception sandbox, and inspects tool outputs via automated Data Loss Prevention (DLP) quarantining.

---

## 2. Architecture Diagram

```text
User / AI Agent
       |
       v
SENTINEL-X Security Gateway
       |
       +--> Intent Contract & Drift Detection
       |
       +--> Request Validation (Path Traversal, Cmd, SQL, Prompt Injection)
       |
       +--> HMAC Integrity Verification (HMAC-SHA256 & Nonce Store)
       |
       +--> MCP Tool Execution (Safe Demo Server Proxy)
       |
       +--> Response Inspection & DLP (Auto-Quarantine & Masking)
       |
       +--> Shadow Deception Simulator (Virtual In-Memory Honeypot)
       |
       v
Audit Database (SQLite / Postgres) & Live React Security Dashboard
```

---

## 3. Key Features

- **Dynamic Intent Contracts:** Parses natural language user goals at ingestion and generates deterministic allowlists for resources and actions.
- **Intent Drift Interception:** Quantifies action alignment on a 0.0 to 1.0 scale and blocks unauthorized tool usage.
- **In-Memory Shadow Deception Sandbox:** Traps directory traversals inside an isolated virtual filesystem containing synthetic honeypots (`/etc/passwd`, `/fake_credentials.txt`) with canary token tracing (`CANARY-X9821-EXFIL-TRAP`).
- **Multi-Vector Injection Defenses:** Independent detectors for Command Injection, SQL Injection, Path Traversal, and Prompt Injection / Jailbreaks.
- **Response DLP Quarantine:** Audits tool outputs before LLM ingestion. Automatically quarantines and redacts API keys, passwords, and private key headers.
- **Cryptographic Request Integrity:** Verifies payloads using HMAC-SHA256 with constant-time equality checks, clock drift bounds, and replay attack rejection.
- **Full-Stack Hackathon Dashboard:** Built with React, Vite, Tailwind CSS, and Recharts, featuring dark-theme telemetry, real-time event feeds, and an interactive 4-scenario Demo Deck.

---

## 4. Required End-to-End Demo Scenarios

SENTINEL-X ShadowGuard features a built-in interactive **Demo Control Panel** with four repeatable test scenarios executing against live backend endpoints:

| Scenario | Input Goal & Proposed Action | Gateway Decision | Key Outcome |
| :--- | :--- | :--- | :--- |
| **DEMO A: Legitimate Request** | Goal: *"Summarize report.pdf"*<br>Tool: `read_demo_file({"filename": "report.pdf"})` | `ALLOW` | Document is read from synthetic storage. Intent match verified (100%). Audit event logged. |
| **DEMO B: Intent Drift** | Goal: *"Summarize report.pdf"*<br>Tool: `read_demo_file({"filename": "passwords.txt"})` | `DENY` | Intent drift intercepted. Unauthorized resource access blocked. Zero credentials returned. |
| **DEMO C: Path Traversal** | Goal: *"Analyze report"*<br>Tool: `read_demo_file({"filename": "../../../etc/passwd"})` | `DECEPTION_REDIRECT` | Real host disk protected. Redirected to in-memory honeypot. Synthetic canary returned. |
| **DEMO D: Response DLP** | Goal: *"Check calendar"*<br>Tool: `get_demo_calendar` (returns synthetic AWS key) | `QUARANTINE` | Output scanner flags sensitive key and password. Payload quarantined and redacted. |

---

## 5. Technology Stack

- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide Icons
- **Backend:** Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn
- **Storage:** SQLite (local development) / PostgreSQL-compatible configuration
- **Security Engine:** Deterministic rule engine, HMAC-SHA256 integrity, in-memory honeypot filesystem
- **Testing:** Pytest, FastAPI TestClient (22 automated test suites)
- **Deployment:** Multi-stage Docker container, unified single-port SPA serving or decoupled microservices

---

## 6. Local Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Clone & Setup Repository
```bash
git clone https://github.com/nisargad1/sentinel-x-shadowguard.git
cd sentinel-x-shadowguard
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python run.py
```
*Backend runs on `http://localhost:8000` with Swagger documentation at `http://localhost:8000/docs`.*

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
*Frontend runs on `http://localhost:5173`.*

### 4. Running via Docker
```bash
docker-compose up --build
```
*Full application (both UI and API) available at `http://localhost:8000`.*

---

## 7. Automated Test Suite

Run the full backend test suite covering multi-vector detectors, intent drift, HMAC tampering, sandbox containment, and API routes:

```bash
cd backend
pytest tests -v
```

**Results:**
```text
tests/test_api_endpoints.py::test_health_check_endpoint PASSED           [  4%]
tests/test_api_endpoints.py::test_dashboard_summary_endpoint PASSED      [  9%]
tests/test_api_endpoints.py::test_demo_scenario_a_legitimate PASSED      [ 13%]
tests/test_api_endpoints.py::test_demo_scenario_b_intent_drift PASSED    [ 18%]
tests/test_api_endpoints.py::test_demo_scenario_c_path_traversal_deception PASSED [ 22%]
tests/test_api_endpoints.py::test_demo_scenario_d_dlp_quarantine PASSED  [ 27%]
tests/test_api_endpoints.py::test_audit_logs_and_export PASSED           [ 31%]
tests/test_detectors.py::test_path_traversal_detection PASSED            [ 36%]
tests/test_detectors.py::test_command_injection_detection PASSED         [ 40%]
tests/test_detectors.py::test_sql_injection_detection PASSED             [ 45%]
tests/test_detectors.py::test_prompt_injection_detection PASSED          [ 50%]
tests/test_dlp_response.py::test_dlp_detects_and_redacts_api_key PASSED  [ 54%]
tests/test_dlp_response.py::test_dlp_detects_password_fields PASSED      [ 59%]
tests/test_dlp_response.py::test_dlp_clean_output_passes_unmodified PASSED [ 63%]
tests/test_hmac_integrity.py::test_valid_hmac_signature PASSED           [ 68%]
tests/test_hmac_integrity.py::test_tampered_payload_rejected PASSED      [ 72%]
tests/test_hmac_integrity.py::test_expired_timestamp_rejected PASSED     [ 77%]
tests/test_hmac_integrity.py::test_replay_attack_rejected PASSED         [ 81%]
tests/test_intent_drift.py::test_legitimate_intent_contract_match PASSED [ 86%]
tests/test_intent_drift.py::test_intent_drift_unauthorized_resource PASSED [ 90%]
tests/test_intent_drift.py::test_prohibited_action_override PASSED       [ 95%]
tests/test_sandbox_deception.py::test_deception_sandbox_files PASSED     [100%]

============================= 22 passed in 1.14s ==============================
```

---

## 8. API Endpoint Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Production health check (database, modules, uptime) |
| `GET` | `/api/dashboard/summary` | Live telemetry metrics, risk trends, recent incidents |
| `GET` | `/api/dashboard/events` | Searchable & filterable security event feed |
| `GET` | `/api/dashboard/stream` | Server-Sent Events (SSE) live telemetry stream |
| `POST` | `/api/security/evaluate` | Intent and injection evaluation for agent tool calls |
| `POST` | `/api/security/inspect-response` | Post-execution DLP scanner and redactor |
| `POST` | `/api/security/verify-signature` | HMAC-SHA256 integrity and replay verification |
| `POST` | `/api/sandbox/simulate` | Virtual honeypot path containment simulator |
| `GET` | `/api/sandbox/status` | Deception filesystem state and synthetic file catalog |
| `POST` | `/api/intents/contract` | Structured Intent Contract generator |
| `POST` | `/api/intents/evaluate` | Real-time intent drift evaluation |
| `POST` | `/api/mcp/call-tool` | Mediated MCP Tool Gateway proxy |
| `POST` | `/api/demo/run-scenario` | Automated execution of the 4 hackathon demo scenarios |
| `POST` | `/api/demo/reset` | Resets and seeds baseline demonstration telemetry |
| `GET` | `/api/audit-logs` | Searchable audit trail with HMAC verification |
| `GET` | `/api/audit-logs/export` | Compliance audit report exporter (JSON / CSV) |

---

## 9. MCP Integration Guide

To route an external Model Context Protocol (MCP) server through SENTINEL-X ShadowGuard:

1. Configure your AI agent client to point tool execution requests to the gateway endpoint: `POST /api/mcp/call-tool`.
2. Include the original user goal in the request payload:
   ```json
   {
     "user_goal": "Summarize release notes",
     "tool_name": "read_demo_file",
     "arguments": {"filename": "release_notes.md"}
   }
   ```
3. The gateway inspects intent drift, ensures path traversal isolation, verifies command safety, proxies the execution to the MCP tool, and inspects the output for DLP leaks before returning to the agent.

---

## 10. Security Limitations & Threat Boundaries

- **In-Memory Deception Honeypot:** The deception filesystem is entirely virtualized in memory. It holds zero real credentials or host disk inodes.
- **Fail-Closed Architecture:** Unsigned or tampered requests are rejected prior to policy evaluation.
- **HMAC Scope:** HMAC verification guarantees request payload integrity and prevents replay attacks. It does not replace user identity authentication.

---

## 11. License

This project is licensed under the MIT License.
