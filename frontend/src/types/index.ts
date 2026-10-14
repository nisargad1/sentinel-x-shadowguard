export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type Decision = 'ALLOW' | 'DENY' | 'QUARANTINE' | 'DECEPTION_REDIRECT' | 'REQUIRE_APPROVAL';
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

export type TabType = 'overview' | 'events' | 'intents' | 'threats' | 'sandbox' | 'audit' | 'settings';
