# SENTINEL-X ShadowGuard — Architecture Documentation

## System Architecture

```text
       +--------------------------------------------------------+
       |               User Prompt / AI Agent Goal              |
       +--------------------------------------------------------+
                                   |
                                   v
             [ POST /api/mcp/call-tool or /security/evaluate ]
                                   |
                                   v
+-----------------------------------------------------------------------+
|                     SENTINEL-X SECURITY GATEWAY                       |
|                                                                       |
|  [ LAYER 1: Cryptographic Integrity ]                                 |
|  - HMAC-SHA256 Canonical Signature Check                              |
|  - Nonce Replay Prevention (Sliding-window Cache)                     |
|  - Clock Drift Boundary Enforcement (<= 300s)                         |
|                                                                       |
|  [ LAYER 2: Intent Contract Engine ]                                  |
|  - Immutable Contract Generation (Permitted Resources & Actions)     |
|  - Deterministic Intent Drift Scoring (0.0 to 1.0)                    |
|  - Prohibited Action Overrides (Least Privilege)                      |
|                                                                       |
|  [ LAYER 3: Multi-Vector Injection Detectors ]                        |
|  - Path Traversal & Canonical Boundary Breakout                      |
|  - Command Injection (Shell Operators & Binaries)                    |
|  - SQL Injection (Tautologies & UNION SELECT)                         |
|  - Prompt Injection & Jailbreak (DAN / System Prompt Exfiltration)    |
|                                                                       |
|  [ LAYER 4: Shadow Deception Sandbox (Honeypot) ]                     |
|  - Intercepts Traversal without real host disk access                 |
|  - Serves Synthetic Decoys (/etc/passwd, /fake_credentials.txt)       |
|  - Embeds Canary Signatures (CANARY-X9821-EXFIL-TRAP)                 |
|                                                                       |
|  [ LAYER 5: Safe Tool Dispatch & DLP Inspection ]                     |
|  - Proxied Model Context Protocol (MCP) Tool Invocation               |
|  - Pre-Ingestion Output Scanning (API Keys, Passwords, Tokens)        |
|  - Automated Response Quarantining & Masking                          |
+-----------------------------------------------------------------------+
            |                                           |
            v                                           v
+-----------------------+                   +-----------------------+
|  Real MCP Tool Server |                   | Persistent Audit DB   |
|  (Safe Demo Tools)    |                   | (SQLite / PostgreSQL) |
+-----------------------+                   +-----------------------+
                                                        |
                                                        v
                                            +-----------------------+
                                            | React Dark Dashboard  |
                                            | (Live SSE Telemetry)  |
                                            +-----------------------+
```

## Component Responsibilities

1. **Gateway Proxy (`app/services/mcp_service.py`)**:
   Mediates all tool requests between AI agents and MCP servers. Guarantees that neither requests nor responses bypass security policies.
2. **Intent Engine (`app/services/intent_engine.py`)**:
   Synthesizes structured Intent Contracts from original user goals. Computes deterministic intent scores and denies actions targeting resources outside the approved perimeter.
3. **Multi-Vector Detectors (`app/security/detectors/`)**:
   Independent detectors for Path Traversal, Command Injection, SQL Injection, Prompt Injection, and DLP Leaks.
4. **Deception Simulator (`app/sandbox/deception_fs.py`)**:
   Maintains an isolated in-memory virtual filesystem with synthetic honeypots (`fake_users.txt`, `fake_credentials.txt`). Keeps the host OS 100% untouched.
5. **DLP Inspector (`app/security/detectors/dlp_inspector.py`)**:
   Scans tool outputs before returning to the AI agent. Quarantines responses containing synthetic keys or credentials and delivers redacted payloads.
6. **Telemetry & Dashboard (`frontend/src/`)**:
   Provides real-time visibility into fleet risk trends, live security event feeds, intent contracts, deception honeypots, and audit trails.
