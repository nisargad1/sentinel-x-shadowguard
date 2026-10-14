import React from 'react';
import {
  ShieldCheck,
  ShieldBan,
  AlertOctagon,
  Lock,
  Box,
  TrendingUp,
  Activity,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import { DashboardSummary, SecurityEvent } from '../types';

interface MetricsOverviewProps {
  summary: DashboardSummary | null;
  onSelectEvent: (event: SecurityEvent) => void;
  onOpenDemo: () => void;
}

export const MetricsOverview: React.FC<MetricsOverviewProps> = ({
  summary,
  onSelectEvent,
  onOpenDemo
}) => {
  if (!summary) {
    return (
      <div className="p-8 text-center text-slate-400 font-mono">
        Loading gateway metrics...
      </div>
    );
  }

  const statCards = [
    {
      label: 'Total Inspected',
      value: summary.total_inspected,
      icon: <Activity className="w-5 h-5 text-cyan-400" />,
      color: 'border-cyan-500/20 bg-cyan-950/20 text-cyan-400',
      change: '+100% active'
    },
    {
      label: 'Allowed Requests',
      value: summary.allowed_count,
      icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
      color: 'border-emerald-500/20 bg-emerald-950/20 text-emerald-400',
      change: 'Verified intent'
    },
    {
      label: 'Blocked Requests',
      value: summary.blocked_count,
      icon: <ShieldBan className="w-5 h-5 text-red-400" />,
      color: 'border-red-500/20 bg-red-950/20 text-red-400',
      change: 'Policy enforced'
    },
    {
      label: 'Attacks Detected',
      value: summary.attacks_detected,
      icon: <AlertOctagon className="w-5 h-5 text-rose-500" />,
      color: 'border-rose-500/20 bg-rose-950/20 text-rose-400',
      change: 'Injections & Drift'
    },
    {
      label: 'DLP Leaks Prevented',
      value: summary.dlp_leaks_prevented,
      icon: <Lock className="w-5 h-5 text-purple-400" />,
      color: 'border-purple-500/20 bg-purple-950/20 text-purple-400',
      change: 'Quarantined tokens'
    },
    {
      label: 'Sandbox Activations',
      value: summary.sandbox_activations,
      icon: <Box className="w-5 h-5 text-amber-400" />,
      color: 'border-amber-500/20 bg-amber-950/20 text-amber-400',
      change: 'Isolated honeypot'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner with Quick Hackathon Action */}
      <div className="cyber-card p-5 bg-gradient-to-r from-cyber-card via-slate-900 to-cyber-panel border-cyan-500/30 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-2">
            <span className="h-2 w-2 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-xs font-mono text-cyan-400 tracking-wider uppercase font-semibold">
              Live Gateway Runtime Active
            </span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">
            MCP Agent Perimeter & Intent Protection
          </h2>
          <p className="text-xs text-slate-400 max-w-2xl">
            Autonomous AI agent tool requests are cryptographically verified via HMAC, checked against dynamically generated intent contracts, filtered for multi-vector injections, and safely isolated in honeypots.
          </p>
        </div>
        <button
          onClick={onOpenDemo}
          className="shrink-0 flex items-center space-x-2 px-4 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold text-xs tracking-wider shadow-lg shadow-cyan-500/20 transition-all hover:scale-105"
        >
          <span>TEST 4 DEMO SCENARIOS</span>
          <TrendingUp className="w-4 h-4" />
        </button>
      </div>

      {/* Primary 6 Metrics Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-6 gap-4">
        {statCards.map((card, idx) => (
          <div
            key={idx}
            className="cyber-card p-4 flex flex-col justify-between space-y-2 hover:border-slate-600 transition"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">{card.label}</span>
              <div className={`p-1.5 rounded-md border ${card.color}`}>
                {card.icon}
              </div>
            </div>
            <div>
              <div className="text-2xl font-bold font-mono text-white tracking-tight">
                {card.value}
              </div>
              <div className="text-[11px] font-mono text-slate-500 mt-0.5">
                {card.change}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Analytics Chart & System Posture */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Trend Chart */}
        <div className="cyber-card p-5 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <span>Agent Fleet Risk Trend (Hourly Telemetry)</span>
              </h3>
              <p className="text-xs text-slate-400">
                Continuous risk score index and attack volume intercepted over recent execution windows
              </p>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono text-slate-400">
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
                <span>Avg Risk</span>
              </div>
              <div className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-red-400"></span>
                <span>Threats Blocked</span>
              </div>
            </div>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary.risk_trend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#00E5FF" stopOpacity={0.0} />
                  </linearGradient>
                  <linearGradient id="blockedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#FF3366" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#FF3366" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E2B45" vertical={false} />
                <XAxis dataKey="time" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0D1424',
                    borderColor: '#1E2B45',
                    borderRadius: '8px',
                    fontSize: '12px',
                    color: '#F8FAFC',
                    fontFamily: 'monospace'
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="avg_risk"
                  stroke="#00E5FF"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#riskGradient)"
                  name="Risk Index"
                />
                <Area
                  type="monotone"
                  dataKey="blocked_count"
                  stroke="#FF3366"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#blockedGradient)"
                  name="Blocked Attacks"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Protection Engine Status Card */}
        <div className="cyber-card p-5 space-y-4 flex flex-col justify-between">
          <div className="space-y-3">
            <div className="flex items-center justify-between border-b border-cyber-border pb-3">
              <h3 className="text-sm font-semibold text-slate-100">Protection Perimeter</h3>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 font-bold">
                ENFORCED
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Intent Drift Engine</span>
                <span className="font-mono text-emerald-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Deterministic + Contract</span>
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Path Traversal Honeypot</span>
                <span className="font-mono text-cyan-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Virtual Isolated FS</span>
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Injection Shields</span>
                <span className="font-mono text-emerald-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Cmd, SQL, Prompt Jailbreaks</span>
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Response DLP Filter</span>
                <span className="font-mono text-purple-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Auto-Quarantine & Mask</span>
                </span>
              </div>
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Cryptographic Integrity</span>
                <span className="font-mono text-cyan-400 flex items-center space-x-1">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>HMAC-SHA256 Nonce Verification</span>
                </span>
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border space-y-1">
            <div className="text-[11px] font-mono text-slate-400">Database Engine</div>
            <div className="text-xs font-mono text-slate-200 font-semibold flex items-center justify-between">
              <span>SQLAlchemy / SQLite Persistence</span>
              <span className="text-emerald-400 text-[10px]">SYNCED</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Security Incidents Table */}
      <div className="cyber-card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-100 flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Recent Agent Security Events</span>
          </h3>
          <span className="text-xs text-slate-500 font-mono">
            Showing latest {summary.recent_events.length} events
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-cyber-border text-slate-400 font-mono uppercase text-[11px]">
                <th className="pb-3 font-semibold">Timestamp</th>
                <th className="pb-3 font-semibold">Event Type</th>
                <th className="pb-3 font-semibold">Proposed Action</th>
                <th className="pb-3 font-semibold">Severity</th>
                <th className="pb-3 font-semibold">Decision</th>
                <th className="pb-3 font-semibold">Risk</th>
                <th className="pb-3 font-semibold text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-cyber-border">
              {summary.recent_events.map((event) => {
                const getDecisionBadge = (d: string) => {
                  switch (d) {
                    case 'ALLOW':
                      return 'bg-emerald-950/80 text-emerald-400 border border-emerald-500/30';
                    case 'DENY':
                      return 'bg-red-950/80 text-red-400 border border-red-500/30';
                    case 'QUARANTINE':
                      return 'bg-purple-950/80 text-purple-400 border border-purple-500/30';
                    case 'DECEPTION_REDIRECT':
                      return 'bg-amber-950/80 text-amber-400 border border-amber-500/30';
                    default:
                      return 'bg-slate-800 text-slate-300';
                  }
                };

                const getSeverityColor = (s: string) => {
                  switch (s) {
                    case 'CRITICAL':
                      return 'text-rose-400 font-bold';
                    case 'HIGH':
                      return 'text-red-400 font-semibold';
                    case 'MEDIUM':
                      return 'text-amber-400';
                    default:
                      return 'text-slate-400';
                  }
                };

                return (
                  <tr key={event.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-3 font-mono text-slate-400 text-[11px]">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-3 font-mono font-semibold text-slate-200">
                      {event.event_type}
                    </td>
                    <td className="py-3 font-mono text-slate-300 max-w-xs truncate">
                      {event.proposed_action || event.tool_name || 'N/A'}
                    </td>
                    <td className={`py-3 font-mono text-[11px] ${getSeverityColor(event.severity)}`}>
                      {event.severity}
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${getDecisionBadge(event.decision)}`}>
                        {event.decision}
                      </span>
                    </td>
                    <td className="py-3 font-mono font-bold text-slate-200">
                      {event.risk_score}
                    </td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectEvent(event)}
                        className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-400 text-[11px] font-mono transition"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
