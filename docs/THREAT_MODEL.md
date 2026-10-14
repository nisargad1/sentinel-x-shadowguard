# SENTINEL-X ShadowGuard — Threat Model & Security Posture

## 1. Threat Landscape for MCP AI Agents

Autonomous AI agents utilizing the Model Context Protocol (MCP) face unique attack vectors:

1. **Intent Drift**: An agent prompted to summarize a harmless file is manipulated by indirect prompt injection to query credentials or exfiltrate private keys.
2. **Path Traversal & Host Breakout**: Agents requesting file resources may execute `../` sequences to access host configuration files (`/etc/passwd`, `.env`, `~/.aws/credentials`).
3. **Command & SQL Injection**: Untrusted parameters passed to shell or database tools can result in remote code execution (RCE) or data breaches.
4. **Data Loss Prevention (DLP) Failures**: Tools querying internal APIs may inadvertently return raw tokens, session cookies, or passwords directly to an LLM context.
5. **Request Tampering & Replay**: Adversaries positioned between client and gateway may modify proposed tool arguments or replay captured actions.

---

## 2. Gateway Defenses

| Threat Vector | Defense Mechanism | Action Taken |
| :--- | :--- | :--- |
| **Intent Drift** | Dynamic Intent Contract Engine | Blocks actions on resources outside user goal scope (`DENY`). |
| **Path Traversal** | PathTraversalDetector & Deception Sandbox | Redirects traversal to in-memory honeypot with decoy files (`DECEPTION_REDIRECT`). |
| **Command Injection** | Operator & Binary Regex Parser | Fails closed on shell delimiters and execution binaries (`DENY`). |
| **SQL Injection** | Tautology & UNION Attack Detector | Blocks malformed SQL queries (`DENY`). |
| **Prompt Injection** | Jailbreak & Override Heuristics | Flags instruction disregard or system prompt leaks (`DENY`). |
| **Response Leakage** | DLP High-Entropy & Key Scanner | Quarantines unredacted response and delivers masked payload (`QUARANTINE`). |
| **Payload Tampering** | HMAC-SHA256 Canonical Signing | Rejects signature mismatches with constant-time comparison (`DENY`). |
| **Replay Attacks** | In-Memory Sliding Nonce Store | Rejects previously processed nonces within drift window (`DENY`). |

---

## 3. Assumptions and Security Boundaries

1. **Isolated Honeypot**: The virtual filesystem is held entirely in memory. It has no bindings or mounts to host filesystem inodes.
2. **Fail Closed**: In strict HMAC enforcement mode, any unsigned or expired request is immediately dropped before invoking intent parsing.
3. **Sanitized Telemetry**: Audit logs and security event records pass through regex redaction before database persistence to prevent password or key leakage in log storage.
