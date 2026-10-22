# SENTINEL-X SMARTGUARD
### The Trust Layer for Autonomous AI Agents

[![Tests](https://img.shields.io/badge/Tests-44%20Passed-brightgreen?style=flat-square)](backend/tests)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.14-blue?style=flat-square)](backend)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)](frontend)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat-square)](frontend)
[![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)](LICENSE)

---
> 🚧 **Project Status: Under Active Development**
> SENTINEL-X SmartGuard started at HackUrity 2026 and is still being improved. Some features are incomplete, and you may run into bugs. Live demo links have been taken down while I work on stability.

---


## 1. Executive Summary & Problem Statement

Autonomous AI agents powered by LLMs and protocols like Model Context Protocol (MCP) are rapidly taking over production operations—reading files, querying databases, executing APIs, and modifying CRM records.

**The Catastrophic Problem:**
Traditional network firewalls and API gateways operate at network layers (IP, port, HTTP method) and have **zero visibility into AI intent, agent trust, or cumulative action cost**. If an autonomous agent suffers an indirect prompt injection, tool hallucination, or runaway loop:
- It can read sensitive payroll databases while performing a harmless report summary (**Intent Drift & Unauthorized Access**).
- It can break out of application sandboxes using traversal attacks (**System Compromise**).
- It can waste thousands of dollars executing redundant identical queries in a loop (**Budget Bleed**).
- It can execute irreversible high-consequence writes without oversight (**Uncontrolled Autonomy**).

**SENTINEL-X SmartGuard** is the **Trust Layer for Autonomous AI Agents**: an intent-aware, pre-execution runtime gateway that evaluates every proposed tool call across **5 dimensions** and returns one of **4 deterministic decisions** before the tool is ever allowed to execute.

---

## 2. Core Architecture & The 5-Stage Action Value Engine

```text
               +-------------------------------------------------------------+
               |                  Autonomous AI Agent Client                 |
               |       (Python SDK, LangChain, LlamaIndex, MCP Client)       |
               +-------------------------------------------------------------+
                                              |
                                              | Propose Action (JSON / REST)
                                              v
+-------------------------------------------------------------------------------------------+
|                          SENTINEL-X SMARTGUARD RUNTIME GATEWAY                            |
+-------------------------------------------------------------------------------------------+
|  1. INTENT ALIGNMENT                                                                      |
|     Evaluates semantic and structural overlap with user objective (Goal-Action Alignment) |
|                                                                                           |
|  2. DETERMINISTIC AUTHORIZATION                                                           |
|     Enforces agent role boundaries, permitted tools, and resource pattern access policies|
|                                                                                           |
|  3. MULTI-VECTOR RISK SCANNING                                                             |
|     Inspects payloads for Path Traversal, Command Injection, SQLi & Prompt Injection     |
|                                                                                           |
|  4. BUDGET & COST ENFORCEMENT                                                             |
|     Enforces workspace & agent-level monetary caps atomically pre-execution               |
|                                                                                           |
|  5. EFFICIENCY & VALUE OPTIMIZATION                                                       |
|     Detects redundant/duplicate idempotent calls with 60s TTL; returns cached results     |
+-------------------------------------------------------------------------------------------+
        |                     |                       |                        |
        v                     v                       v                        v
    [ ALLOW ]            [ OPTIMIZE ]               [ ASK ]                [ BLOCK ]
Safe & authorized.     Redundant call safely    High-consequence write;   Unauthorized,
Direct execution       returned from cache;     requires human sign-off   risky, or over-budget.
logged to audit.       saves cost & compute.    in Approval Inbox.        Never executes.
        |                     |                       |                        |
        v                     v                       v                        v
+---------------+     +---------------+       +---------------+       +------------------+
| MCP Execution |     | Cached Result |       | Crypto Token  |       | Structured Audit |
|    Adapter    |     | Zero Tool Run |       | Human Inbox   |       | Incident Logged  |
+---------------+     +---------------+       +---------------+       +------------------+
```

### The 4 Gateway Decisions:

1. **ALLOW:** The proposed action is authorized, aligned with the user's intent, safe, and within budget limits. The gateway proceeds to execute the tool and records an audit log.
2. **OPTIMIZE:** A safe, identical, or more efficient execution path is available. The gateway satisfies the agent's request without re-executing costly compute or external API calls, measuring and recording net cost savings.
3. **ASK:** The action proposes a sensitive or irreversible change (e.g. deleting files, deactivating customer accounts, transferring funds). Execution is paused pre-execution, generating a cryptographic approval token in the **Human Approval Inbox**.
4. **BLOCK:** The proposed action violates authorization policies, exceeds budget caps, drifts from stated user intent, or contains malicious payloads. The protected tool is **never invoked**.

---

## 3. The 6 Reproducible Demo Scenarios

SENTINEL-X SmartGuard includes 6 reproducible end-to-end scenarios executing live through both API endpoints and the interactive frontend console:

| # | Scenario Name | Agent & Intent | Proposed Tool Action | Gateway Decision | Reason Code & Outcome |
| :---: | :--- | :--- | :--- | :---: | :--- |
| **1** | **Legitimate Document Summary** | `finance-analyst-agent`<br>Intent: *"Summarize Q3 report"* | `read_demo_file({"filename": "report.pdf"})` | **ALLOW** | `AUTHZ_PERMITTED`<br>Verified intent alignment (100%), permitted resource. Report safely read and returned. |
| **2** | **Restricted Resource Access** | `finance-analyst-agent`<br>Intent: *"Summarize Q3 report"* | `read_demo_file({"filename": "payroll_salaries.csv"})` | **BLOCK** | `AUTHZ_RESOURCE_FORBIDDEN`<br>Restricted payroll file is outside agent permissions. Tool is never invoked. |
| **3** | **Redundant Search Optimization** | `market-research-agent`<br>Intent: *"Research pricing"* | `search_demo_documents({"query": "enterprise tier pricing"})` | **OPTIMIZE** | `DUPLICATE_OPTIMIZED_CACHE_HIT`<br>Identical query repeated within 60s window. Served from cache; saved 5¢ compute. |
| **4** | **Sensitive Action Human Approval** | `crm-automation-agent`<br>Intent: *"Deactivate churned account"* | `update_customer_status({"customer_id": "CUST-9842", "new_status": "DEACTIVATED"})` | **ASK** | `POLICY_REQUIRES_HUMAN_APPROVAL`<br>Halted pre-execution. Generates crypto token in Human Approval Inbox for 1-click review. |
| **5** | **Budget Limit Exceeded** | `translation-agent`<br>Intent: *"Batch translate document"* | `translate_document({"doc_id": "doc_large.pdf", "estimated_cost": 50})` | **BLOCK** | `BUDGET_CAP_EXCEEDED`<br>Cost (50¢) exceeds agent remaining budget cap (5¢ left). Atomically halted. |
| **6** | **Prompt Injection in Synthetic Content** | `support-agent`<br>Intent: *"Review support ticket"* | `dump_database_credentials({"override": "SYSTEM_OVERRIDE_ACTIVE"})` | **BLOCK** | `INJECTION_ATTACK_DETECTED`<br>Untrusted ticket text attempts credential dump. Disallowed tool blocked immediately. |

---

## 4. Transparent Proof of Value (PoV) Engine

Rather than claiming vague efficiency gains, SENTINEL-X SmartGuard measures honest, observable financial and runtime value using the formula:

$$\text{Net Savings} = \text{Baseline Cost} - \text{Enforced Cost} - \text{Gateway Overhead}$$

- **Baseline Cost:** Total theoretical cost if all proposed actions ran unconstrained.
- **Enforced Cost:** Cost of actions actually executed and permitted through the gateway.
- **Gateway Overhead:** Evaluated computing overhead incurred by the gateway (~$0.0001 per evaluation).
- **Sub-5ms Evaluation Latency:** Pure deterministic policy engine runs with an average latency of ~3.4 milliseconds.
- **Reproducible Benchmark:** Click **"Run Reproducible Benchmark"** in the UI to evaluate 20 mixed actions and verify the savings calculation live.

---

## 5. Human-in-the-Loop Approval Workflow

High-stakes tool executions generate cryptographically signed approval records:
- **State Machine:** `PENDING` $\rightarrow$ `APPROVED` or `REJECTED`.
- **Replay Protection:** Approval tokens are single-use. Once an action is approved, replaying the same token fails with `409 Conflict`.
- **Pre-Execution Halt:** Sensitive tools are never executed until explicit human authorization is received.
- **Atomic Post-Approval Execution:** When authorized in the Inbox, the gateway executes the tool immediately on behalf of the agent, records the authorizer's identity, and updates agent telemetry.

---

## 6. Python SDK Quickstart

AI agents integrate with SENTINEL-X SmartGuard with just a few lines of Python:

```python
from smartguard_client import SmartGuardClient

# Initialize client pointing to local or remote gateway
client = SmartGuardClient(base_url="http://localhost:8000")

# Propose an action before executing
evaluation = client.propose_action(
    agent_id="finance-analyst-agent",
    user_intent="Summarize quarterly earnings report",
    tool_name="read_demo_file",
    action_name="read",
    parameters={"filename": "report.pdf"},
    estimated_cost_cents=2
)

print(f"Decision: {evaluation['decision']}")  # ALLOW
print(f"Execution Output: {evaluation['execution_result']}")

# If an action returns ASK:
if evaluation['decision'] == 'ASK':
    print(f"Human approval required: Token {evaluation['approval_token']}")
```

Run the complete demo workflow in your terminal:
```bash
python sdk/examples/agent_workflow.py
```

---

## 7. Technology Stack

- **Backend:** Python 3.11+, FastAPI 0.115, Pydantic v2, SQLAlchemy, Uvicorn
- **Frontend:** React 18, TypeScript 5, Vite, Tailwind CSS, Lucide Icons, Recharts
- **Storage:** SQLite with WAL mode (local) / PostgreSQL ready for production
- **Security:** HMAC-SHA256 request verification, in-memory virtual deception sandbox, response DLP quarantining, deterministic intent engine
- **Test Suite:** Pytest (33 automated test suites running in <2 seconds)

---

## 8. Local Setup & Quickstart

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
*Backend starts on `http://localhost:8000` with API docs at `http://localhost:8000/docs`.*

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run build   # Or 'npm run dev' for development server
```

### 4. Running via Docker
```bash
docker-compose up --build
```

---

## 9. Automated Test Suite (33/33 Tests Passing)

Execute the full suite of unit and integration tests:

```bash
pytest -v
```

```text
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1 -- 33 items

backend/tests/test_api_endpoints.py::test_health_check_endpoint PASSED   [  3%]
backend/tests/test_api_endpoints.py::test_dashboard_summary_endpoint PASSED [  6%]
backend/tests/test_api_endpoints.py::test_demo_scenario_a_legitimate PASSED [  9%]
backend/tests/test_api_endpoints.py::test_demo_scenario_b_intent_drift PASSED [ 12%]
backend/tests/test_api_endpoints.py::test_demo_scenario_c_path_traversal_deception PASSED [ 15%]
backend/tests/test_api_endpoints.py::test_demo_scenario_d_dlp_quarantine PASSED [ 18%]
backend/tests/test_api_endpoints.py::test_audit_logs_and_export PASSED   [ 21%]
backend/tests/test_detectors.py::test_path_traversal_detection PASSED    [ 24%]
backend/tests/test_detectors.py::test_command_injection_detection PASSED [ 27%]
backend/tests/test_detectors.py::test_sql_injection_detection PASSED     [ 30%]
backend/tests/test_detectors.py::test_prompt_injection_detection PASSED  [ 33%]
backend/tests/test_dlp_response.py::test_dlp_detects_and_redacts_api_key PASSED [ 36%]
backend/tests/test_dlp_response.py::test_dlp_detects_password_fields PASSED [ 39%]
backend/tests/test_dlp_response.py::test_dlp_clean_output_passes_unmodified PASSED [ 42%]
backend/tests/test_hmac_integrity.py::test_valid_hmac_signature PASSED   [ 45%]
backend/tests/test_hmac_integrity.py::test_tampered_payload_rejected PASSED [ 48%]
backend/tests/test_hmac_integrity.py::test_expired_timestamp_rejected PASSED [ 51%]
backend/tests/test_hmac_integrity.py::test_replay_attack_rejected PASSED [ 54%]
backend/tests/test_intent_drift.py::test_legitimate_intent_contract_match PASSED [ 57%]
backend/tests/test_intent_drift.py::test_intent_drift_unauthorized_resource PASSED [ 60%]
backend/tests/test_intent_drift.py::test_prohibited_action_override PASSED [ 63%]
backend/tests/test_sandbox_deception.py::test_deception_sandbox_files PASSED [ 66%]
backend/tests/test_smartguard_v1.py::test_scenario_1_legitimate_allow PASSED [ 69%]
backend/tests/test_smartguard_v1.py::test_scenario_2_restricted_resource_block PASSED [ 72%]
backend/tests/test_smartguard_v1.py::test_scenario_3_redundant_search_optimize PASSED [ 75%]
backend/tests/test_smartguard_v1.py::test_scenario_4_sensitive_action_ask PASSED [ 78%]
backend/tests/test_smartguard_v1.py::test_approval_workflow_execution_and_replay_resistance PASSED [ 81%]
backend/tests/test_smartguard_v1.py::test_scenario_5_budget_exceeded_block PASSED [ 84%]
backend/tests/test_smartguard_v1.py::test_scenario_6_prompt_injection_block PASSED [ 87%]
backend/tests/test_smartguard_v1.py::test_scenarios_reset PASSED         [ 90%]
backend/tests/test_smartguard_v1.py::test_proof_of_value_metrics PASSED  [ 93%]
backend/tests/test_smartguard_v1.py::test_repeatable_benchmark PASSED    [ 96%]
backend/tests/test_smartguard_v1.py::test_agent_trust_profiles PASSED    [100%]

============================= 33 passed in 1.62s ==============================
```

---

## 10. Complete API Reference

### SmartGuard Core Gateway (`/api/v1/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/actions/propose` | Evaluate proposed action across 5 dimensions (ALLOW, OPTIMIZE, ASK, BLOCK) |
| `GET` | `/api/v1/actions/{id}` | Retrieve evaluation record and audit log by evaluation ID |
| `GET` | `/api/v1/approvals` | List approval requests filtered by status (`PENDING`, `APPROVED`, `REJECTED`) |
| `POST` | `/api/v1/approvals/{id}/action` | Review approval (APPROVE/REJECT) with replay-resistant execution |
| `GET` | `/api/v1/scenarios` | List the 6 reproducible demonstration scenarios |
| `POST` | `/api/v1/scenarios/run` | Execute one of the 6 scenarios against real gateway logic |
| `POST` | `/api/v1/scenarios/reset` | Reset scenario telemetry and database state |
| `GET` | `/api/v1/value-engine/metrics` | Retrieve live Proof of Value metrics and net savings |
| `POST` | `/api/v1/value-engine/benchmark` | Run 20-action benchmark proving measured cost & latency |
| `GET` | `/api/v1/agents` | List agent trust profiles, budgets, and permitted tools |
| `GET` | `/api/v1/agents/{id}` | Retrieve specific agent trust details and recent actions |

### Runtime Telemetry & Security Defense (`/api/`)
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Production health check (database, modules, uptime) |
| `GET` | `/api/dashboard/summary` | Gateway metrics, risk score, attacks intercepted, sandboxes active |
| `GET` | `/api/dashboard/events` | Filterable incident feed with full JSON inspection payloads |
| `GET` | `/api/dashboard/stream` | Server-Sent Events (SSE) live telemetry stream |
| `POST` | `/api/security/inspect-response` | Post-execution DLP inspector redacting API keys and passwords |
| `POST` | `/api/sandbox/simulate` | Virtual in-memory honeypot directory traversal containment |
| `GET` | `/api/audit-logs` | Tamper-evident audit log trail with HMAC verification |
| `GET` | `/api/audit-logs/export` | Export compliance logs as JSON or CSV |

---

## 11. Security Threat Boundaries

- **In-Memory Virtual Honeypot:** Traversal breakouts are captured inside a pure Python virtual filesystem (`/etc/passwd`, `/etc/shadow`) with canary signatures. Real host disks and processes are 100% isolated.
- **Fail-Closed Execution:** If an agent payload fails authorization or triggers an injection flag, execution is denied immediately.
- **Defense in Depth:** Deterministic authorization runs first, followed by regex injection shields, budget checks, and post-execution response DLP quarantine.

---

## 12. License

This project is licensed under the MIT License.
