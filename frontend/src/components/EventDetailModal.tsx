import React from 'react';
import { X, Shield, AlertTriangle, Terminal, Info, CheckCircle2 } from 'lucide-react';
import { SecurityEvent } from '../types';

interface EventDetailModalProps {
  event: SecurityEvent | null;
  onClose: () => void;
}

export const EventDetailModal: React.FC<EventDetailModalProps> = ({ event, onClose }) => {
  if (!event) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-2xl bg-cyber-dark border border-cyan-500/40 rounded-2xl shadow-2xl shadow-cyan-950/50 overflow-hidden flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-cyber-border bg-cyber-card flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-500/40">
              <Shield className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
                <span>SECURITY INCIDENT INSPECTOR</span>
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                ID: {event.id} | Timestamp: {new Date(event.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 overflow-y-auto space-y-4 text-xs font-mono">
          {/* Key Metric Gauges */}
          <div className="grid grid-cols-3 gap-3">
            <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border">
              <div className="text-slate-500 text-[10px]">EVENT TYPE</div>
              <div className="text-sm font-bold text-slate-200 mt-0.5">{event.event_type}</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border">
              <div className="text-slate-500 text-[10px]">DECISION</div>
              <div className={`text-sm font-bold mt-0.5 ${
                event.decision === 'ALLOW' ? 'text-emerald-400' :
                event.decision === 'DENY' ? 'text-red-400' :
                event.decision === 'QUARANTINE' ? 'text-purple-400' : 'text-amber-400'
              }`}>{event.decision}</div>
            </div>
            <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border">
              <div className="text-slate-500 text-[10px]">RISK SCORE</div>
              <div className={`text-sm font-bold mt-0.5 ${
                event.risk_score >= 70 ? 'text-red-400' :
                event.risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400'
              }`}>{event.risk_score} / 100</div>
            </div>
          </div>

          {/* User Goal & Proposed Action */}
          <div className="p-3.5 rounded-xl bg-cyber-panel border border-cyber-border space-y-2">
            <div>
              <span className="text-slate-500 text-[10px] block">ORIGINAL USER GOAL</span>
              <span className="text-slate-200">{event.user_goal || 'N/A'}</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block">PROPOSED AGENT TOOL ACTION</span>
              <span className="text-cyan-300">{event.proposed_action || event.tool_name || 'N/A'}</span>
            </div>
          </div>

          {/* Detection Rule & Remediation */}
          <div className="p-3.5 rounded-xl bg-cyber-panel border border-cyber-border space-y-2">
            <div>
              <span className="text-slate-500 text-[10px] block">MATCHED POLICY RULE</span>
              <span className="text-red-300 font-bold">{event.detection_rule || 'STANDARD_PERIMETER'}</span>
            </div>
            <div>
              <span className="text-slate-500 text-[10px] block">RECOMMENDED REMEDIATION</span>
              <span className="text-emerald-300">{event.remediation || 'None'}</span>
            </div>
          </div>

          {/* Sanitized Payload Preview */}
          <div className="space-y-1">
            <span className="text-slate-400 text-[10px] uppercase">Sanitized Payload Representation</span>
            <pre className="p-3 rounded-xl bg-black/60 border border-cyber-border text-slate-300 overflow-x-auto text-[11px]">
              {event.payload_preview || 'No payload logged.'}
            </pre>
          </div>

          {/* Raw Metadata JSON */}
          {event.details && (
            <div className="space-y-1">
              <span className="text-slate-400 text-[10px] uppercase">Event Metadata</span>
              <pre className="p-3 rounded-xl bg-black/60 border border-cyber-border text-slate-400 overflow-x-auto text-[10px]">
                {JSON.stringify(event.details, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
