"""
Example Agent Workflow using SENTINEL-X SmartGuard SDK
Demonstrates:
  1. Legitimate action execution (ALLOW)
  2. Duplicate action optimization (OPTIMIZE)
  3. Sensitive write approval pause (ASK)
  4. Unauthorized access blocking (BLOCK)
"""

import sys
import os

# Add parent directory to path to import SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from smartguard_client import SmartGuardClient

def run_agent_workflow():
    client = SmartGuardClient(base_url="http://localhost:8000")
    print("=" * 70)
    print("SENTINEL-X SmartGuard -- Autonomous AI Agent Client Demo")
    print("=" * 70)

    # 1. Propose Legitimate Action
    print("\n[1] Agent proposes: Read report.pdf...")
    res1 = client.propose_action(
        agent_id="finance-analyst-agent",
        user_intent="Summarize quarterly earnings report",
        tool_name="read_demo_file",
        parameters={"filename": "report.pdf"}
    )
    print(f" -> Decision: {res1['decision']} ({res1['reason_code']})")
    print(f" -> Latency: {res1['duration_ms']}ms | Risk: {res1['risk_score']}")
    print(f" -> Output: {res1['execution_result']['content'][:60]}...")

    # 2. Propose Duplicate Search (Optimization)
    print("\n[2] Agent proposes: Redundant competitor query...")
    client.propose_action(
        agent_id="market-research-agent",
        user_intent="Check competitor tier pricing",
        tool_name="search_demo_documents",
        parameters={"query": "enterprise tier pricing"}
    )
    # Immediate repeat
    res2 = client.propose_action(
        agent_id="market-research-agent",
        user_intent="Check competitor tier pricing",
        tool_name="search_demo_documents",
        parameters={"query": "enterprise tier pricing"}
    )
    print(f" -> Decision: {res2['decision']} ({res2['reason_code']})")
    print(f" -> Optimization: {res2['optimization_applied']}")
    print(f" -> Measured Cost Savings: ${res2['savings_cents'] / 100:.2f}")

    # 3. Propose Unauthorized Payroll Access (Security Block)
    print("\n[3] Agent attempts: Restricted payroll access...")
    res3 = client.propose_action(
        agent_id="finance-analyst-agent",
        user_intent="Review quarterly briefing",
        tool_name="read_demo_file",
        parameters={"filename": "payroll_salaries.csv"}
    )
    print(f" -> Decision: {res3['decision']} ({res3['reason_code']})")
    print(f" -> Explanation: {res3['explanation']}")
    print(f" -> Protected Tool Invoked: {res3['execution_status'] == 'EXECUTED'}")

    print("\n" + "=" * 70)
    print("Agent workflow successfully guarded by SENTINEL-X SmartGuard!")
    print("=" * 70)

if __name__ == "__main__":
    run_agent_workflow()
