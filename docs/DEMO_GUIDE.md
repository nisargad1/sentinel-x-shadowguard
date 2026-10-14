# SENTINEL-X ShadowGuard — 3-Minute Hackathon Demo Guide

## Quick Demo Walkthrough

### Step 1: Open the Deployed Dashboard
Open the public URL in your browser. Notice the real-time telemetry gauges:
- **System Health:** OPERATIONAL
- **Fleet Risk Trend:** Hourly chart showing risk distribution
- **Protection Perimeter:** Enforced modules (Intent, Traversal, Injections, DLP, HMAC)

### Step 2: Open the Demo Scenario Deck
Click the glowing cyan **"DEMO SCENARIOS"** button in the header or sidebar.
The modal contains four standardized, repeatable test scenarios that run **real backend requests**.

---

### Scenario A — Legitimate Agent Request
1. Click **"DEMO A"** tab.
2. Observe input: Goal is *"Summarize report.pdf"* and tool action is `read_demo_file({"filename": "report.pdf"})`.
3. Click **"RUN SCENARIO LIVE"**.
4. **Outcome:**
   - Decision: `ALLOW` (Risk Score: 10/100, Intent Match: 100%).
   - The report content is delivered to the agent.
   - Audit trail records an authorized access event.

---

### Scenario B — Intent Drift & Credential Access
1. Click **"DEMO B"** tab.
2. Observe input: Goal is *"Summarize report.pdf"*, but proposed tool action is `read_demo_file({"filename": "passwords.txt"})`.
3. Click **"RUN SCENARIO LIVE"**.
4. **Outcome:**
   - Decision: `DENY` (Risk Score: 85/100, Intent Match: 10%).
   - Explanation: *"Intent Drift Detected: Unauthorized access to high-risk resource 'passwords.txt'"*.
   - Tool execution is blocked before reaching the demo storage. No credentials returned.

---

### Scenario C — Path Traversal Honeypot Containment
1. Click **"DEMO C"** tab.
2. Observe input: Proposed tool action attempts path traversal `read_demo_file({"filename": "../../../etc/passwd"})`.
3. Click **"RUN SCENARIO LIVE"**.
4. **Outcome:**
   - Decision: `DECEPTION_REDIRECT` (Risk Score: 92/100).
   - Real Filesystem Accessed: **FALSE** (Host OS completely protected).
   - Attacker is fed synthetic decoy accounts with canary token `CANARY-X9821-EXFIL-TRAP`.
   - Sandbox activation incremented on dashboard.

---

### Scenario D — Sensitive Response DLP Quarantine
1. Click **"DEMO D"** tab.
2. Observe input: Calendar tool response contains a synthetic AWS access key and dummy password.
3. Click **"RUN SCENARIO LIVE"**.
4. **Outcome:**
   - Decision: `QUARANTINE` (Risk Score: 95/100).
   - DLP scanner intercepts unredacted output.
   - Agent receives safe payload with `[REDACTED_AWS_ACCESS_KEY]` and `[REDACTED_PASSWORD_FIELD]`.
   - Unredacted secret never logged or passed to the client.

---

### Step 3: Inspect Audit Trail & Export Report
1. Navigate to the **"Audit & Compliance"** tab on the sidebar.
2. Inspect the cryptographically verified HMAC signatures and sanitized event summaries.
3. Click **"Export JSON"** or **"Export CSV"** to download the compliance report.
