import React, { useState, useEffect } from 'react';
import { Bot, Shield, DollarSign, Award, CheckCircle, XCircle, AlertTriangle, Layers, Info } from 'lucide-react';
import { api } from '../services/api';
import { AgentProfile } from '../types';

export const AgentTrustProfilesView: React.FC = () => {
  const [agents, setAgents] = useState<AgentProfile[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    try {
      const data = await api.getAgents();
      setAgents(data);
    } catch (err) {
      console.error('Failed to load agents:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    if (score >= 70) return 'text-amber-400 bg-amber-500/10 border-amber-500/30';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="bg-slate-900/60 border border-slate-800 p-6 rounded-xl flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Bot className="w-5 h-5 text-cyan-400" />
            <h2 className="text-xl font-bold text-white tracking-wide">Registered Agent Trust Profiles</h2>
          </div>
          <p className="text-sm text-slate-400">
            Per-agent identity, permitted tool allowlists, resource boundaries, and budget utilization.
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono text-slate-400 bg-slate-950/60 px-3 py-2 rounded-lg border border-slate-800">
          <Award className="w-4 h-4 text-cyan-400" />
          <span>Active Fleet: {agents.length} Agents</span>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {agents.map((ag) => {
          const budgetPercent = Math.min(100, Math.round((ag.current_spend_cents / Math.max(1, ag.budget_limit_cents)) * 100));
          const isHighSpend = budgetPercent >= 80;

          return (
            <div
              key={ag.id}
              className="bg-slate-900/40 border border-slate-800 hover:border-slate-700/80 rounded-xl p-5 space-y-4 transition"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-cyan-950/40 border border-cyan-800/40 flex items-center justify-center text-cyan-400">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white leading-tight">{ag.name}</h3>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-slate-400">{ag.role}</span>
                      <span className="text-[10px] font-mono text-slate-500">•</span>
                      <span className="text-[10px] font-mono text-slate-500">{ag.id}</span>
                    </div>
                  </div>
                </div>

                {/* Trust Score Badge */}
                <div className="text-right">
                  <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded text-xs font-mono font-bold border ${getScoreColor(ag.trust_score)}`}>
                    <Shield className="w-3.5 h-3.5" />
                    {ag.trust_score}/100 TRUST
                  </span>
                </div>
              </div>

              {/* Budget Progress Bar */}
              <div className="space-y-1.5 pt-1">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Budget Utilization</span>
                  <span className={isHighSpend ? 'text-amber-400 font-bold' : 'text-slate-300'}>
                    ${(ag.current_spend_cents / 100).toFixed(2)} / ${(ag.budget_limit_cents / 100).toFixed(2)} ({budgetPercent}%)
                  </span>
                </div>
                <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      isHighSpend ? 'bg-amber-400' : 'bg-cyan-500'
                    }`}
                    style={{ width: `${budgetPercent}%` }}
                  />
                </div>
              </div>

              {/* Permitted Tools & Resources */}
              <div className="space-y-2 pt-2 border-t border-slate-800/60 text-xs">
                <div>
                  <span className="text-slate-500 font-mono text-[11px] block mb-1">Permitted Tools:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {ag.permitted_tools.map((t, idx) => (
                      <span key={idx} className="bg-slate-950 border border-slate-800 text-slate-300 px-2 py-0.5 rounded text-[11px] font-mono">
                        {t}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-slate-500 font-mono text-[11px] block mb-1">Permitted Resources:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {ag.permitted_resources.map((r, idx) => (
                      <span key={idx} className="bg-cyan-950/20 border border-cyan-800/30 text-cyan-300 px-2 py-0.5 rounded text-[11px] font-mono">
                        {r}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Evaluation Breakdown Counters */}
              <div className="grid grid-cols-4 gap-2 pt-2 border-t border-slate-800/60 text-center font-mono text-xs">
                <div className="bg-slate-950/50 p-2 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">ALLOWED</span>
                  <span className="text-emerald-400 font-bold">{ag.allowed_count}</span>
                </div>
                <div className="bg-slate-950/50 p-2 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">OPTIMIZED</span>
                  <span className="text-cyan-400 font-bold">{ag.optimized_count}</span>
                </div>
                <div className="bg-slate-950/50 p-2 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">ASK</span>
                  <span className="text-amber-400 font-bold">{ag.ask_count}</span>
                </div>
                <div className="bg-slate-950/50 p-2 rounded border border-slate-800">
                  <span className="text-[10px] text-slate-500 block">BLOCKED</span>
                  <span className="text-rose-400 font-bold">{ag.blocked_count}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Formula Transparency Note */}
      <div className="bg-slate-900/30 border border-slate-800/80 p-5 rounded-xl space-y-1.5 text-xs text-slate-400">
        <div className="flex items-center gap-1.5 text-slate-300 font-semibold">
          <Info className="w-4 h-4 text-cyan-400" />
          Transparent Trust Score Formula
        </div>
        <p className="leading-relaxed">
          <span className="font-mono text-slate-300">Trust Score = 95 + (Allowed * 1) - (Blocked * 10) + (Optimized * 1)</span>. Trust scores serve as historical behavioral indicators only. A high score never grants additional permissions or bypasses mandatory authorization checks.
        </p>
      </div>
    </div>
  );
};
