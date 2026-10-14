import React, { useState } from 'react';
import { Activity, Filter, Search, ArrowUpDown, Shield } from 'lucide-react';
import { SecurityEvent } from '../types';

interface LiveEventFeedProps {
  events: SecurityEvent[];
  onSelectEvent: (event: SecurityEvent) => void;
}

export const LiveEventFeed: React.FC<LiveEventFeedProps> = ({ events, onSelectEvent }) => {
  const [filterType, setFilterType] = useState<string>('ALL');
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const filteredEvents = events.filter((ev) => {
    if (filterType !== 'ALL' && ev.event_type !== filterType) return false;
    if (filterSeverity !== 'ALL' && ev.severity !== filterSeverity) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchType = ev.event_type.toLowerCase().includes(q);
      const matchAction = (ev.proposed_action || '').toLowerCase().includes(q);
      const matchGoal = (ev.user_goal || '').toLowerCase().includes(q);
      const matchRule = (ev.detection_rule || '').toLowerCase().includes(q);
      if (!matchType && !matchAction && !matchGoal && !matchRule) return false;
    }
    return true;
  });

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

  const getSeverityBadge = (s: string) => {
    switch (s) {
      case 'CRITICAL':
        return 'bg-rose-950/80 text-rose-400 border border-rose-500/40';
      case 'HIGH':
        return 'bg-red-950/80 text-red-400 border border-red-500/30';
      case 'MEDIUM':
        return 'bg-amber-950/80 text-amber-400 border border-amber-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border border-slate-700';
    }
  };

  return (
    <div className="space-y-4">
      {/* Search and Filters Bar */}
      <div className="cyber-card p-4 flex flex-col md:flex-row items-center justify-between gap-3">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search events, actions, rules..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-cyber-panel border border-cyber-border rounded-lg pl-9 pr-3 py-1.5 text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <div className="flex items-center space-x-1.5 text-xs text-slate-400">
            <Filter className="w-3.5 h-3.5" />
            <span>Category:</span>
          </div>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-cyber-panel border border-cyber-border rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Categories</option>
            <option value="INTENT_DRIFT">INTENT_DRIFT</option>
            <option value="PATH_TRAVERSAL">PATH_TRAVERSAL</option>
            <option value="COMMAND_INJECTION">COMMAND_INJECTION</option>
            <option value="SQL_INJECTION">SQL_INJECTION</option>
            <option value="PROMPT_INJECTION">PROMPT_INJECTION</option>
            <option value="DLP_LEAK_PREVENTED">DLP_LEAK_PREVENTED</option>
            <option value="DECEPTION_ACTIVATED">DECEPTION_ACTIVATED</option>
            <option value="AUTHORIZED_ACCESS">AUTHORIZED_ACCESS</option>
          </select>

          <select
            value={filterSeverity}
            onChange={(e) => setFilterSeverity(e.target.value)}
            className="bg-cyber-panel border border-cyber-border rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* Events List */}
      <div className="cyber-card p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-cyber-border pb-3">
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-100">Live Security Event Log</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Showing {filteredEvents.length} events
          </span>
        </div>

        {filteredEvents.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs font-mono">
            No events matching criteria.
          </div>
        ) : (
          <div className="space-y-2">
            {filteredEvents.map((ev) => (
              <div
                key={ev.id}
                onClick={() => onSelectEvent(ev)}
                className="p-3.5 rounded-xl border border-cyber-border bg-cyber-panel/60 hover:border-cyan-500/40 hover:bg-slate-900/80 transition cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-3"
              >
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex items-center space-x-2.5 flex-wrap gap-y-1">
                    <span className="text-[11px] font-mono text-slate-500">
                      {new Date(ev.timestamp).toLocaleTimeString()}
                    </span>
                    <span className="text-xs font-mono font-bold text-slate-200">
                      {ev.event_type}
                    </span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${getSeverityBadge(ev.severity)}`}>
                      {ev.severity}
                    </span>
                    <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${getDecisionBadge(ev.decision)}`}>
                      {ev.decision}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400">
                      Rule: {ev.detection_rule || 'STANDARD'}
                    </span>
                  </div>

                  <div className="text-xs font-mono text-slate-300 truncate">
                    <span className="text-slate-500">Proposed: </span>
                    {ev.proposed_action || ev.tool_name || 'N/A'}
                  </div>

                  {ev.user_goal && (
                    <div className="text-[11px] text-slate-400 truncate">
                      <span className="text-slate-500 font-mono">Goal: </span>
                      "{ev.user_goal}"
                    </div>
                  )}
                </div>

                <div className="flex items-center space-x-4 shrink-0 justify-between md:justify-end">
                  <div className="text-right">
                    <div className="text-[10px] font-mono text-slate-500">RISK SCORE</div>
                    <div className={`text-sm font-mono font-bold ${
                      ev.risk_score >= 70 ? 'text-red-400' :
                      ev.risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400'
                    }`}>
                      {ev.risk_score}/100
                    </div>
                  </div>

                  <button className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-mono transition">
                    Inspect
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
