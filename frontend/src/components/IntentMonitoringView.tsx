import React, { useState } from 'react';
import { Compass, CheckCircle, XCircle, AlertCircle, ArrowRight, Play, Shield } from 'lucide-react';
import { api } from '../services/api';

export const IntentMonitoringView: React.FC = () => {
  const [userGoal, setUserGoal] = useState('Summarize report.pdf for the weekly team sync.');
  const [toolName, setToolName] = useState('read_demo_file');
  const [toolArgsStr, setToolArgsStr] = useState('{"filename": "report.pdf"}');
  const [evalResult, setEvalResult] = useState<any>(null);
  const [isEvaluating, setIsEvaluating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const presets = [
    {
      label: 'Legitimate: Summarize report.pdf',
      goal: 'Summarize report.pdf for the quarterly security briefing.',
      tool: 'read_demo_file',
      args: '{"filename": "report.pdf"}'
    },
    {
      label: 'Drift: Exfiltrate Passwords',
      goal: 'Summarize report.pdf for the quarterly security briefing.',
      tool: 'read_demo_file',
      args: '{"filename": "passwords.txt"}'
    },
    {
      label: 'Action Drift: Delete Files',
      goal: 'Review report.pdf and check metrics.',
      tool: 'delete_file',
      args: '{"filename": "report.pdf"}'
    },
    {
      label: 'Authorized: Read Calendar',
      goal: 'Check security team calendar for today.',
      tool: 'get_demo_calendar',
      args: '{"day": "today"}'
    }
  ];

  const handleEvaluate = async () => {
    setIsEvaluating(true);
    setError(null);
    setEvalResult(null);

    let parsedArgs = {};
    try {
      parsedArgs = JSON.parse(toolArgsStr);
    } catch {
      setError('Invalid JSON in tool arguments field');
      setIsEvaluating(false);
      return;
    }

    try {
      const res = await api.evaluateCustomIntent(userGoal, toolName, parsedArgs);
      setEvalResult(res);
    } catch (err: any) {
      setError(err.message || 'Evaluation error');
    } finally {
      setIsEvaluating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <div className="cyber-card p-5 space-y-2">
        <div className="flex items-center space-x-2">
          <Compass className="w-5 h-5 text-cyan-400" />
          <h2 className="text-base font-bold text-white font-mono">
            INTENT DRIFT DETECTION ENGINE
          </h2>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          AI agents can diverge from user intent due to prompt injection, hallucination, or lateral movement.
          SENTINEL-X synthesizes an immutable <strong>Intent Contract</strong> at prompt ingestion time and strictly enforces resource boundaries before dispatching any tool.
        </p>

        {/* Quick Presets */}
        <div className="pt-2 flex flex-wrap gap-2">
          <span className="text-[11px] font-mono text-slate-500 self-center mr-1">Presets:</span>
          {presets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => {
                setUserGoal(p.goal);
                setToolName(p.tool);
                setToolArgsStr(p.args);
                setEvalResult(null);
              }}
              className="px-2.5 py-1 rounded bg-slate-800 hover:bg-cyan-950 text-slate-300 hover:text-cyan-400 border border-cyber-border text-xs font-mono transition"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Input Workbench */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="cyber-card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 font-mono">
            1. Intent & Action Parameters
          </h3>

          <div className="space-y-3 text-xs">
            <div className="space-y-1">
              <label className="text-slate-400 font-mono">Original User Goal / Prompt:</label>
              <textarea
                value={userGoal}
                onChange={(e) => setUserGoal(e.target.value)}
                rows={3}
                className="w-full bg-cyber-panel border border-cyber-border rounded-lg p-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-mono">Proposed MCP Tool Name:</label>
              <input
                type="text"
                value={toolName}
                onChange={(e) => setToolName(e.target.value)}
                className="w-full bg-cyber-panel border border-cyber-border rounded-lg px-2.5 py-2 text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="space-y-1">
              <label className="text-slate-400 font-mono">Tool Arguments (JSON):</label>
              <textarea
                value={toolArgsStr}
                onChange={(e) => setToolArgsStr(e.target.value)}
                rows={3}
                className="w-full bg-cyber-panel border border-cyber-border rounded-lg p-2.5 text-slate-200 font-mono focus:outline-none focus:border-cyan-500"
              />
            </div>

            {error && (
              <div className="p-2.5 rounded bg-red-950/60 border border-red-500/30 text-red-300 text-xs font-mono">
                {error}
              </div>
            )}

            <button
              onClick={handleEvaluate}
              disabled={isEvaluating}
              className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black font-mono font-bold text-xs tracking-wider transition shadow-lg shadow-cyan-500/20"
            >
              <Play className="w-4 h-4 fill-black" />
              <span>{isEvaluating ? 'EVALUATING CONTRACT...' : 'EVALUATE INTENT DRIFT'}</span>
            </button>
          </div>
        </div>

        {/* Evaluation Outcome */}
        <div className="cyber-card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 font-mono">
            2. Synthesized Contract & Drift Analysis
          </h3>

          {!evalResult ? (
            <div className="py-16 text-center text-slate-500 text-xs font-mono">
              Click "Evaluate Intent Drift" to generate contract and view real-time decision.
            </div>
          ) : (
            <div className="space-y-4 animate-fade-in text-xs font-mono">
              {/* Decision Banner */}
              <div className={`p-3.5 rounded-xl border flex items-center justify-between ${
                evalResult.decision === 'ALLOW'
                  ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300'
                  : evalResult.decision === 'DENY'
                  ? 'bg-red-950/60 border-red-500/40 text-red-300'
                  : 'bg-amber-950/60 border-amber-500/40 text-amber-300'
              }`}>
                <div className="flex items-center space-x-2.5">
                  {evalResult.decision === 'ALLOW' ? <CheckCircle className="w-5 h-5 text-emerald-400" /> : <XCircle className="w-5 h-5 text-red-400" />}
                  <div>
                    <div className="text-sm font-bold">GATEWAY DECISION: {evalResult.decision}</div>
                    <div className="text-[11px] opacity-80">{evalResult.explanation}</div>
                  </div>
                </div>
              </div>

              {/* Gauges */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border">
                  <div className="text-slate-500 text-[10px]">INTENT MATCH SCORE</div>
                  <div className="text-xl font-bold text-cyan-400 mt-0.5">
                    {(evalResult.intent_match_score * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border">
                  <div className="text-slate-500 text-[10px]">RISK SCORE</div>
                  <div className={`text-xl font-bold mt-0.5 ${
                    evalResult.risk_score >= 60 ? 'text-red-400' : 'text-emerald-400'
                  }`}>
                    {evalResult.risk_score} / 100
                  </div>
                </div>
              </div>

              {/* Generated Contract Summary */}
              {evalResult.contract && (
                <div className="p-3.5 rounded-xl bg-cyber-dark border border-cyber-border space-y-2.5">
                  <div className="text-slate-400 font-bold text-[11px] uppercase flex items-center justify-between">
                    <span>Generated Contract ({evalResult.contract.contract_id})</span>
                    <span className="text-cyan-400 text-[10px]">DETERMINISTIC RULES</span>
                  </div>

                  <div className="space-y-1.5 text-[11px]">
                    <div>
                      <span className="text-slate-500">Permitted Resources: </span>
                      <span className="text-emerald-400 font-semibold">
                        {JSON.stringify(evalResult.contract.permitted_resources)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Permitted Actions: </span>
                      <span className="text-cyan-400">
                        {JSON.stringify(evalResult.contract.permitted_actions)}
                      </span>
                    </div>
                    <div>
                      <span className="text-slate-500">Prohibited Actions: </span>
                      <span className="text-red-400">
                        {JSON.stringify(evalResult.contract.prohibited_actions)}
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
