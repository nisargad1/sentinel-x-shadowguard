export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type Decision = 'ALLOW' | 'OPTIMIZE' | 'ASK' | 'BLOCK' | 'DENY' | 'QUARANTINE' | 'DECEPTION_REDIRECT' | 'REQUIRE_APPROVAL';
export type SystemHealth = 'OPERATIONAL' | 'ELEVATED_THREAT' | 'CRITICAL';

export interface SecurityEvent {
  id: string;
  timestamp: string;
  event_type: string;
  severity: Severity;
  decision: Decision;
  source: string;
  user_goal?: string;
  proposed_action?: string;
  tool_name?: string;
  risk_score: number;
  intent_score: number;
  payload_preview?: string;
  detection_rule?: string;
  remediation?: string;
  details?: Record<string, any>;
}

export interface RiskTrendPoint {
  time: string;
  avg_risk: number;
  blocked_count: number;
  allowed_count: number;
}

export interface DashboardSummary {
  total_inspected: number;
  allowed_count: number;
  blocked_count: number;
  attacks_detected: number;
  dlp_leaks_prevented: number;
  sandbox_activations: number;
  system_health: SystemHealth;
  average_risk_score: number;
  risk_trend: RiskTrendPoint[];
  recent_events: SecurityEvent[];
}

export interface IntentContract {
  contract_id: string;
  user_goal: string;
  permitted_resources: string[];
  permitted_actions: string[];
  prohibited_actions: string[];
  risk_constraints: Record<string, any>;
}

export interface AuditLog {
  id: string;
  request_id: string;
  timestamp: string;
  caller_ip: string;
  action: string;
  outcome: string;
  hmac_verified: boolean;
  sanitized_summary: string;
  metadata?: Record<string, any>;
}

export interface MCPToolResponse {
  request_id: string;
  decision: Decision;
  execution_success: boolean;
  tool_name: string;
  result: any;
  quarantined: boolean;
  deception_redirect: boolean;
  risk_score: number;
  intent_match_score: number;
  explanation: string;
  timestamp: string;
}

export interface ApprovalItem {
  id: string;
  workspace_id: string;
  agent_id: string;
  evaluation_id: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  expires_at: string;
  created_at: string;
  approved_by?: string;
  tool_name: string;
  action_name: string;
  parameters: Record<string, any>;
  user_intent: string;
  cost_estimate_cents: number;
  risk_level: string;
}

export interface AgentProfile {
  id: string;
  workspace_id: string;
  name: string;
  role: string;
  status: string;
  permitted_tools: string[];
  permitted_resources: string[];
  budget_limit_cents: number;
  current_spend_cents: number;
  trust_score: number;
  total_actions: number;
  allowed_count: number;
  blocked_count: number;
  ask_count: number;
  optimized_count: number;
  recent_evaluations?: Array<Record<string, any>>;
}

export interface ProofOfValueMetrics {
  total_proposed_actions: number;
  total_executed_actions: number;
  total_prevented_actions: number;
  total_approval_actions: number;
  total_optimized_actions: number;
  baseline_cost_cents: number;
  enforced_cost_cents: number;
  gateway_overhead_cents: number;
  net_savings_cents: number;
  average_policy_latency_ms: number;
  duplicate_calls_avoided: number;
  currency: string;
  measurement_mode: string;
}

export interface ScenarioMeta {
  id: string;
  title: string;
  expected_decision: string;
  agent_id: string;
  user_intent: string;
  tool_name: string;
  action_name: string;
  parameters: Record<string, any>;
  description: string;
}

export interface ScenarioRunResult {
  scenario_id: string;
  title: string;
  expected_decision: string;
  actual_decision: string;
  evaluation: {
    correlation_id: string;
    evaluation_id: string;
    decision: string;
    reason_code: string;
    explanation: string;
    risk_level: string;
    risk_score: number;
    intent_alignment_score: number;
    cost_estimate_cents: number;
    cost_actual_cents: number;
    savings_cents: number;
    optimization_applied?: string;
    execution_status: string;
    execution_result?: any;
    approval_token?: string;
    approval_id?: string;
    duration_ms: number;
    timestamp: string;
  };
  execution_evidence: {
    execution_status: string;
    protected_tool_invoked: boolean;
    savings_measured_cents: number;
    cost_incurred_cents: number;
    result_payload?: any;
  };
  audit_event_id: string;
  verified: boolean;
}

export type TabType =
  | 'landing'
  | 'overview'
  | 'scenarios'
  | 'approvals'
  | 'value'
  | 'agents'
  | 'events'
  | 'intents'
  | 'threats'
  | 'sandbox'
  | 'audit'
  | 'settings';
