import React, { useState } from 'react';
import {
  Play,
  CheckCircle,
  XCircle,
  ShieldAlert,
  Lock,
  Box,
  Terminal,
  FileCode,
  Clock,
  Sparkles,
  X
} from 'lucide-react';
import { api } from '../services/api';
import { MCPToolResponse } from '../types';

interface DemoControlPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onScenarioCompleted: () => void;
}

type ScenarioKey = 'DEMO_A' | 'DEMO_B' | 'DEMO_C' | 'DEMO_D';

export const DemoControlPanel: React.FC<DemoControlPanelProps> = ({
  isOpen,
  onClose,
  onScenarioCompleted
}) => {
  const [selectedScenario, setSelectedScenario] = useState<ScenarioKey>('DEMO_A');
  const [isRunning, setIsRunning] = useState(false);
  const [result, setResult] = useState<MCPToolResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const scenarios = [
    {
      id: 'DEMO_A' as ScenarioKey,
      title: 'DEMO A: Legitimate Agent Request',
      badge: 'AUTHORIZED',
      badgeColor: 'bg-emerald-950 text-emerald-400 border border-emerald-500/30',
      inputGoal: 'Summarize report.pdf for quarterly briefing',
      toolAction: 'read_demo_file({"filename": "report.pdf"})',
      expected: 'Permitted document read from synthetic storage. Verified intent match. ALLOW decision.',
      icon: <CheckCircle className="w-5 h-5 text-emerald-400" />
    },
    {
      id: 'DEMO_B' as ScenarioKey,
      title: 'DEMO B: Intent Drift & Credential Access',
      badge: 'INTENT DRIFT',
      badgeColor: 'bg-red-950 text-red-400 border border-red-500/30',
      inputGoal: 'Summarize report.pdf for quarterly briefing',
      toolAction: 'read_demo_file({"filename": "passwords.txt"})',
      expected: 'Contract drift intercepted. Unauthorized resource access denied. No sensitive data exposed.',
      icon: <XCircle className="w-5 h-5 text-red-400" />
    },
    {
      id: 'DEMO_C' as ScenarioKey,
      title: 'DEMO C: Path Traversal Honeypot Containment',
      badge: 'DECEPTION ACTIVE',
      badgeColor: 'bg-amber-950 text-amber-400 border border-amber-500/30',
      inputGoal: 'Analyze system report',
      toolAction: 'read_demo_file({"filename": "../../../etc/passwd"})',
      expected: 'Perimeter breach trapped. Redirected to in-memory deception sandbox. Synthetic canary served.',
      icon: <Box className="w-5 h-5 text-amber-400" />
    },
    {
      id: 'DEMO_D' as ScenarioKey,
      title: 'DEMO D: Sensitive Response DLP Quarantine',
      badge: 'DLP QUARANTINE',
      badgeColor: 'bg-purple-950 text-purple-400 border border-purple-500/30',
      inputGoal: 'Check security team calendar for today',
      toolAction: 'get_demo_calendar({"day": "today", "inject_leak": true})',
      expected: 'Output scanner flags synthetic AWS key and dummy password. Response quarantined & masked.',
      icon: <Lock className="w-5 h-5 text-purple-400" />
    }
  ];

  const currentScenario = scenarios.find((s) => s.id === selectedScenario)!;

  const handleRun = async () => {
    setIsRunning(true);
    setError(null);
    setResult(null);
    try {
      const res = await api.runScenario(selectedScenario);
      setResult(res);
      onScenarioCompleted();
    } catch (err: any) {
      setError(err.message || 'Execution error');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-4xl bg-cyber-dark border border-cyan-500/40 rounded-2xl shadow-2xl shadow-cyan-950/50 overflow-hidden flex flex-col max-h-[92vh]">
        {/* Modal Header */}
        <div className="px-6 py-4 border-b border-cyber-border bg-cyber-card flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 rounded-lg bg-cyan-950/80 border border-cyan-500/40">
              <Sparkles className="w-5 h-5 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
                <span>SENTINEL-X DEMO SCENARIO DECK</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-900/60 text-cyan-300 border border-cyan-500/30">
                  REAL BACKEND EXECUTION
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Execute end-to-end hackathon test scenarios against the live runtime security gateway
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

        {/* Modal Body */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {/* Scenario Selector Tabs */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
            {scenarios.map((scen) => {
              const isSelected = selectedScenario === scen.id;
              return (
                <button
                  key={scen.id}
                  onClick={() => {
                    setSelectedScenario(scen.id);
                    setResult(null);
                    setError(null);
                  }}
                  className={`p-3.5 rounded-xl border text-left transition-all flex flex-col justify-between space-y-3 ${
                    isSelected
                      ? 'border-cyan-400 bg-cyan-950/40 shadow-md shadow-cyan-950'
                      : 'border-cyber-border bg-cyber-card hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-slate-300">
                      {scen.id.replace('_', ' ')}
                    </span>
                    {scen.icon}
                  </div>
                  <div>
                    <div className="text-xs font-semibold text-slate-100 line-clamp-1">
                      {scen.title.split(': ')[1]}
                    </div>
                    <span className={`inline-block mt-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded ${scen.badgeColor}`}>
                      {scen.badge}
                    </span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Scenario Specification Panel */}
          <div className="cyber-card p-4 bg-slate-900/80 border-cyber-border space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono font-semibold text-cyan-400 uppercase tracking-wider">
                Scenario Inputs & Parameters
              </span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${currentScenario.badgeColor}`}>
                {currentScenario.badge}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-lg bg-cyber-dark border border-cyber-border space-y-1">
                <span className="text-[11px] font-mono text-slate-400">Original User Goal / Prompt:</span>
                <div className="font-mono text-slate-200 font-medium">
                  "{currentScenario.inputGoal}"
                </div>
              </div>
              <div className="p-3 rounded-lg bg-cyber-dark border border-cyber-border space-y-1">
                <span className="text-[11px] font-mono text-slate-400">Proposed MCP Tool Action:</span>
                <div className="font-mono text-cyan-300 font-medium">
                  {currentScenario.toolAction}
                </div>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-500/20 text-xs text-slate-300 flex items-start space-x-2">
              <Sparkles className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold text-cyan-300">Expected Gateway Behavior: </span>
                {currentScenario.expected}
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={handleRun}
                disabled={isRunning}
                className="flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-black font-mono font-bold text-xs tracking-wider shadow-lg shadow-cyan-500/25 transition disabled:opacity-50"
              >
                <Play className={`w-4 h-4 fill-black ${isRunning ? 'animate-spin' : ''}`} />
                <span>{isRunning ? 'TRANSMITTING TO GATEWAY...' : 'RUN SCENARIO LIVE'}</span>
              </button>
            </div>
          </div>

          {/* Results Viewer */}
          {error && (
            <div className="p-4 rounded-xl bg-red-950/50 border border-red-500/40 text-red-300 text-xs font-mono">
              Gateway Error: {error}
            </div>
          )}

          {result && (
            <div className="cyber-card p-4 border-cyan-500/40 space-y-4 animate-fade-in">
              <div className="flex items-center justify-between border-b border-cyber-border pb-3">
                <div className="flex items-center space-x-2">
                  <Terminal className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-mono font-bold text-slate-200">
                    Live Security Gateway Response ({result.request_id})
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold ${
                    result.decision === 'ALLOW' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' :
                    result.decision === 'DENY' ? 'bg-red-950 text-red-400 border border-red-500/30' :
                    result.decision === 'QUARANTINE' ? 'bg-purple-950 text-purple-400 border border-purple-500/30' :
                    'bg-amber-950 text-amber-400 border border-amber-500/30'
                  }`}>
                    DECISION: {result.decision}
                  </span>
                </div>
              </div>

              {/* Quick Telemetry Gauges */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                <div className="p-2.5 rounded bg-cyber-dark border border-cyber-border">
                  <div className="text-slate-500 text-[10px]">RISK SCORE</div>
                  <div className={`text-lg font-bold ${
                    result.risk_score >= 70 ? 'text-red-400' :
                    result.risk_score >= 40 ? 'text-amber-400' : 'text-emerald-400'
                  }`}>
                    {result.risk_score} / 100
                  </div>
                </div>

                <div className="p-2.5 rounded bg-cyber-dark border border-cyber-border">
                  <div className="text-slate-500 text-[10px]">INTENT MATCH</div>
                  <div className="text-lg font-bold text-cyan-400">
                    {(result.intent_match_score * 100).toFixed(0)}%
                  </div>
                </div>

                <div className="p-2.5 rounded bg-cyber-dark border border-cyber-border">
                  <div className="text-slate-500 text-[10px]">DLP QUARANTINE</div>
                  <div className={`text-lg font-bold ${result.quarantined ? 'text-purple-400' : 'text-slate-400'}`}>
                    {result.quarantined ? 'ACTIVE' : 'NONE'}
                  </div>
                </div>

                <div className="p-2.5 rounded bg-cyber-dark border border-cyber-border">
                  <div className="text-slate-500 text-[10px]">HONEYPOT DECEPTION</div>
                  <div className={`text-lg font-bold ${result.deception_redirect ? 'text-amber-400' : 'text-slate-400'}`}>
                    {result.deception_redirect ? 'CONTAINED' : 'INACTIVE'}
                  </div>
                </div>
              </div>

              {/* Policy Explanation */}
              <div className="p-3 rounded-lg bg-cyber-dark border border-cyber-border space-y-1">
                <div className="text-[10px] font-mono text-slate-400 uppercase">Gateway Policy Explanation</div>
                <div className="text-xs text-slate-200 font-mono leading-relaxed">
                  {result.explanation}
                </div>
              </div>

              {/* Result Payload Inspector */}
              <div className="space-y-1.5">
                <div className="text-[10px] font-mono text-slate-400 uppercase flex items-center justify-between">
                  <span>Delivered Result Payload to Agent</span>
                  <span className="text-slate-500">
                    {result.deception_redirect ? 'SIMULATED DECOY' : result.quarantined ? 'REDACTED SAFE PAYLOAD' : 'NORMAL OUTPUT'}
                  </span>
                </div>
                <pre className="p-3 rounded-lg bg-cyber-dark border border-cyber-border text-slate-300 font-mono text-[11px] overflow-x-auto max-h-48">
                  {typeof result.result === 'string'
                    ? result.result
                    : JSON.stringify(result.result, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
