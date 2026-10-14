import {
  DashboardSummary,
  SecurityEvent,
  AuditLog,
  IntentContract,
  MCPToolResponse,
  ApprovalItem,
  AgentProfile,
  ProofOfValueMetrics,
  ScenarioMeta,
  ScenarioRunResult
} from '../types';

export const API_BASE = import.meta.env.VITE_API_URL || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'
    : ''
);

export const api = {
  async getHealth() {
    const res = await fetch(`${API_BASE}/health`);
    if (!res.ok) throw new Error(`Health check failed: ${res.statusText}`);
    return res.json();
  },

  async getDashboardSummary(): Promise<DashboardSummary> {
    const res = await fetch(`${API_BASE}/api/dashboard/summary`);
    if (!res.ok) throw new Error(`Failed to fetch dashboard: ${res.statusText}`);
    return res.json();
  },

  async getEvents(params?: { event_type?: string; severity?: string; decision?: string; limit?: number }): Promise<SecurityEvent[]> {
    const query = new URLSearchParams();
    if (params?.event_type) query.set('event_type', params.event_type);
    if (params?.severity) query.set('severity', params.severity);
    if (params?.decision) query.set('decision', params.decision);
    if (params?.limit) query.set('limit', params.limit.toString());

    const res = await fetch(`${API_BASE}/api/dashboard/events?${query.toString()}`);
    if (!res.ok) throw new Error(`Failed to fetch events: ${res.statusText}`);
    return res.json();
  },

  async getAuditLogs(search?: string, outcome?: string): Promise<AuditLog[]> {
    const query = new URLSearchParams();
    if (search) query.set('search', search);
    if (outcome) query.set('outcome', outcome);

    const res = await fetch(`${API_BASE}/api/audit-logs?${query.toString()}`);
    if (!res.ok) throw new Error(`Failed to fetch audit logs: ${res.statusText}`);
    return res.json();
  },

  async exportAuditLogs(format: 'json' | 'csv' = 'json'): Promise<Blob> {
    const res = await fetch(`${API_BASE}/api/audit-logs/export?format=${format}`);
    if (!res.ok) throw new Error(`Export failed: ${res.statusText}`);
    return res.blob();
  },

  async getSandboxStatus() {
    const res = await fetch(`${API_BASE}/api/sandbox/status`);
    if (!res.ok) throw new Error(`Sandbox status failed: ${res.statusText}`);
    return res.json();
  },

  async simulateSandbox(requested_path: string) {
    const res = await fetch(`${API_BASE}/api/sandbox/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ requested_path })
    });
    if (!res.ok) throw new Error(`Sandbox simulation failed: ${res.statusText}`);
    return res.json();
  },

  async evaluateCustomIntent(user_goal: string, tool_name: string, tool_arguments: Record<string, any>) {
    const res = await fetch(`${API_BASE}/api/intents/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_goal, tool_name, tool_arguments })
    });
    if (!res.ok) throw new Error(`Intent evaluation failed: ${res.statusText}`);
    return res.json();
  },

  async generateIntentContract(user_goal: string): Promise<IntentContract> {
    const res = await fetch(`${API_BASE}/api/intents/contract?user_goal=${encodeURIComponent(user_goal)}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`Contract generation failed: ${res.statusText}`);
    return res.json();
  },

  // SmartGuard 6 Demo Scenarios
  async getScenarios(): Promise<ScenarioMeta[]> {
    const res = await fetch(`${API_BASE}/api/v1/scenarios`);
    if (!res.ok) throw new Error(`Failed to fetch scenarios: ${res.statusText}`);
    return res.json();
  },

  async runScenarioV1(scenario_id: string): Promise<ScenarioRunResult> {
    const res = await fetch(`${API_BASE}/api/v1/scenarios/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id })
    });
    if (!res.ok) throw new Error(`Scenario run failed: ${res.statusText}`);
    return res.json();
  },

  async resetScenariosV1() {
    const res = await fetch(`${API_BASE}/api/v1/scenarios/reset`, { method: 'POST' });
    if (!res.ok) throw new Error(`Scenario reset failed: ${res.statusText}`);
    return res.json();
  },

  // Human Approval Inbox
  async getApprovals(status?: string): Promise<ApprovalItem[]> {
    const url = status ? `${API_BASE}/api/v1/approvals?status=${status}` : `${API_BASE}/api/v1/approvals`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch approvals: ${res.statusText}`);
    return res.json();
  },

  async decideApproval(approval_id: string, action: 'APPROVE' | 'REJECT', reason?: string) {
    const res = await fetch(`${API_BASE}/api/v1/approvals/${approval_id}/action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, reason })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Approval action failed');
    }
    return res.json();
  },

  // Proof of Value & Analytics
  async getProofOfValueMetrics(): Promise<ProofOfValueMetrics> {
    const res = await fetch(`${API_BASE}/api/v1/value-engine/metrics`);
    if (!res.ok) throw new Error(`Failed to fetch value metrics: ${res.statusText}`);
    return res.json();
  },

  async runBenchmark() {
    const res = await fetch(`${API_BASE}/api/v1/value-engine/benchmark`, { method: 'POST' });
    if (!res.ok) throw new Error(`Benchmark run failed: ${res.statusText}`);
    return res.json();
  },

  // Agent Trust Profiles
  async getAgents(): Promise<AgentProfile[]> {
    const res = await fetch(`${API_BASE}/api/v1/agents`);
    if (!res.ok) throw new Error(`Failed to fetch agents: ${res.statusText}`);
    return res.json();
  },

  async getAgentProfile(agent_id: string): Promise<AgentProfile> {
    const res = await fetch(`${API_BASE}/api/v1/agents/${agent_id}`);
    if (!res.ok) throw new Error(`Failed to fetch agent profile: ${res.statusText}`);
    return res.json();
  },

  // Legacy scenario runner (preserved)
  async runLegacyScenario(scenario_id: 'DEMO_A' | 'DEMO_B' | 'DEMO_C' | 'DEMO_D'): Promise<MCPToolResponse> {
    const res = await fetch(`${API_BASE}/api/demo/run-scenario`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_id })
    });
    if (!res.ok) throw new Error(`Scenario run failed: ${res.statusText}`);
    return res.json();
  },

  async runScenario(scenario_id: 'DEMO_A' | 'DEMO_B' | 'DEMO_C' | 'DEMO_D'): Promise<MCPToolResponse> {
    return this.runLegacyScenario(scenario_id);
  },

  async resetDemoDatabase(token?: string) {
    const headers: Record<string, string> = {};
    if (token) headers['x-admin-token'] = token;
    const res = await fetch(`${API_BASE}/api/demo/reset`, {
      method: 'POST',
      headers
    });
    if (!res.ok) throw new Error(`Reset failed: ${res.statusText}`);
    return res.json();
  }
};
