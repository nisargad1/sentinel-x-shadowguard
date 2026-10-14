import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, CheckCircle, XCircle, AlertTriangle, Clock, Shield, Sparkles, Terminal, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { ScenarioMeta, ScenarioRunResult } from '../types';

interface ScenariosViewProps {
  onOpenApprovals?: () => void;
  onOpenAudit?: () => void;
}

export const ScenariosView: React.FC<ScenariosViewProps> = ({ onOpenApprovals, onOpenAudit }) => {
  const [scenarios, setScenarios] = useState<ScenarioMeta[]>([]);
  const [results, setResults] = useState<Record<string, ScenarioRunResult>>({});
  const [runningId, setRunningId] = useState<string | null>(null);
  const [resetting, setResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState<string | null>(null);

  useEffect(() => {
    loadScenarios();
  }, []);

  const loadScenarios = async () => {
    try {
      const data = await api.getScenarios();
      setScenarios(data);
    } catch (err) {
      console.error('Failed to load scenarios:', err);
    }
  };

  const handleRun = async (scenarioId: string) => {
    setRunningId(scenarioId);
    try {
      const result = await api.runScenarioV1(scenarioId);
      setResults(prev => ({ ...prev, [scenarioId]: result }));
    } catch (err) {
      console.error(`Failed to run scenario ${scenarioId}:`, err);
    } finally {
      setRunningId(null);
    }
  };

  const handleReset = async () => {
    setResetting(true);
    setResetMessage(null);
    try {
      const res = await api.resetScenariosV1();
      setResults({});
      setResetMessage(res.message || 'Demo data successfully reset.');
      setTimeout(() => setResetMessage(null), 4000);
    } catch (err) {
      console.error('Failed to reset:', err);
    } finally {
      setResetting(false);
    }
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'ALLOW':
        return <span className="px-2.5 py-1 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-mono font-semibold flex items-center gap-1.5"><CheckCircle className="w-3.5 h-3.5" /> ALLOW</span>;
      case 'OPTIMIZE':
        return <span className="px-2.5 py-1 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-xs font-mono font-semibold flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5" /> OPTIMIZE</span>;
      case 'ASK':
        return <span className="px-2.5 py-1 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-mono font-semibold flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> ASK (HUMAN APPROVAL)</span>;
      case 'BLOCK':
      default:
        return <span className="px-2.5 py-1 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs font-mono font-semibold flex items-center gap-1.5"><XCircle className="w-3.5 h-3.5" /> BLOCK</span>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-6 rounded-xl backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h2 className="text-xl font-bold text-white tracking-wide">The Six Reproducible Demo Scenarios</h2>
          </div>
          <p className="text-sm text-slate-400">
            Real backend execution verifying the Action Value Engine's 5 evaluation dimensions: Intent, Authorization, Risk, Cost, and Efficiency.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {resetMessage && (
            <span className="text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/30 px-3 py-1.5 rounded-lg animate-fade-in">
              {resetMessage}
            </span>
          )}
          <button
            onClick={handleReset}
            disabled={resetting}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-medium border border-slate-700 transition"
          >
            <RotateCcw className={`w-4 h-4 ${resetting ? 'animate-spin text-cyan-400' : ''}`} />
            Reset Demo State
          </button>
        </div>
      </div>

      {/* Grid of 6 Scenarios */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {scenarios.map((sc, index) => {
          const res = results[sc.id];
          const isRunning = runningId === sc.id;

          return (
            <div
              key={sc.id}
              className={`flex flex-col justify-between bg-slate-900/40 border rounded-xl p-5 transition ${
                res ? (res.verified ? 'border-cyan-500/40 shadow-lg shadow-cyan-950/20' : 'border-rose-500/40') : 'border-slate-800 hover:border-slate-700'
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div>
                    <span className="text-[11px] font-mono uppercase text-slate-500 font-semibold tracking-wider">
                      Scenario 0{index + 1}
                    </span>
                    <h3 className="text-base font-bold text-white flex items-center gap-2">
                      {sc.title}
                    </h3>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-slate-400 uppercase bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                      Expected: {sc.expected_decision}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-400 mb-4 leading-relaxed">
                  {sc.description}
                </p>

                {/* Proposed Action Box */}
                <div className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-3 font-mono text-xs space-y-1.5 mb-4 text-slate-300">
                  <div className="text-slate-400">
                    <span className="text-cyan-400 font-semibold">Agent:</span> {sc.agent_id}
                  </div>
                  <div className="text-slate-400 truncate">
                    <span className="text-cyan-400 font-semibold">User Intent:</span> "{sc.user_intent}"
                  </div>
                  <div className="text-slate-400 truncate">
                    <span className="text-cyan-400 font-semibold">Tool Action:</span> {sc.tool_name}({JSON.stringify(sc.parameters)})
                  </div>
                </div>

                {/* Execution Evidence (When Run) */}
                {res && (
                  <div className="bg-slate-950/90 border border-cyan-500/30 rounded-lg p-3.5 space-y-2 mb-4 animate-fade-in text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 font-mono">Actual Gateway Decision:</span>
                      {getDecisionBadge(res.actual_decision)}
                    </div>
                    <div className="text-slate-300 font-sans">
                      <span className="font-semibold text-slate-400 font-mono text-[11px]">Reason Code: </span>
                      <span className="font-mono text-cyan-300 font-bold">{res.evaluation.reason_code}</span>
                    </div>
                    <p className="text-slate-300 text-[11px] leading-relaxed">
                      {res.evaluation.explanation}
                    </p>
                    <div className="pt-2 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-slate-400">
                      <div>
                        Tool Invoked: <span className={res.execution_evidence.protected_tool_invoked ? 'text-emerald-400 font-bold' : 'text-rose-400 font-bold'}>
                          {res.execution_evidence.protected_tool_invoked ? 'TRUE' : 'FALSE (HALTED)'}
                        </span>
                      </div>
                      <div>
                        Latency: <span className="text-slate-200">{res.evaluation.duration_ms}ms</span>
                      </div>
                      {res.execution_evidence.savings_measured_cents > 0 && (
                        <div className="text-cyan-400 font-bold">
                          Saved: ${(res.execution_evidence.savings_measured_cents / 100).toFixed(2)}
                        </div>
                      )}
                    </div>

                    {/* Specific Action Link for Scenario 4 ASK */}
                    {res.actual_decision === 'ASK' && onOpenApprovals && (
                      <div className="pt-2">
                        <button
                          onClick={onOpenApprovals}
                          className="w-full text-center py-1.5 px-3 rounded bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 font-medium text-xs border border-amber-500/40 flex items-center justify-center gap-1.5 transition"
                        >
                          <Clock className="w-3.5 h-3.5" />
                          Review in Human Approval Inbox
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Action Button */}
              <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between">
                <span className="text-[11px] text-slate-500 font-mono">
                  {res ? (res.verified ? '✓ Real Backend Verified' : '✗ Verification Mismatch') : 'Ready to execute'}
                </span>
                <button
                  onClick={() => handleRun(sc.id)}
                  disabled={isRunning}
                  className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-semibold shadow-md shadow-cyan-950/40 disabled:opacity-50 transition"
                >
                  <Play className={`w-3.5 h-3.5 ${isRunning ? 'animate-spin' : 'fill-current'}`} />
                  {isRunning ? 'Evaluating...' : 'Run Scenario Live'}
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
