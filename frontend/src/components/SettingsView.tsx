import React, { useState, useEffect } from 'react';
import { Settings, Shield, Key, Database, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { api, API_BASE } from '../services/api';

interface SettingsViewProps {
  onRefreshData: () => void;
}

export const SettingsView: React.FC<SettingsViewProps> = ({ onRefreshData }) => {
  const [healthInfo, setHealthInfo] = useState<any>(null);
  const [intentThreshold, setIntentThreshold] = useState('0.65');
  const [riskCutoff, setRiskCutoff] = useState('60');
  const [resetToken, setResetToken] = useState('shadowguard-reset-authorized-token-2026');
  const [resetStatus, setResetStatus] = useState<string | null>(null);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    api.getHealth().then(setHealthInfo).catch(() => {});
  }, []);

  const handleResetDemo = async () => {
    if (!window.confirm('Reset security events and seed fresh demonstration telemetry?')) return;
    setIsResetting(true);
    setResetStatus(null);
    try {
      const res = await api.resetDemoDatabase(resetToken);
      setResetStatus(res.message || 'Reset complete');
      onRefreshData();
    } catch (err: any) {
      setResetStatus(`Reset failed: ${err.message}`);
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="cyber-card p-5 space-y-2">
        <div className="flex items-center space-x-2">
          <Settings className="w-5 h-5 text-cyan-400" />
          <h2 className="text-base font-bold text-white font-mono">
            GATEWAY POLICIES & HMAC INTEGRITY CONFIGURATION
          </h2>
        </div>
        <p className="text-xs text-slate-400">
          Configure runtime enforcement thresholds, cryptographic request integrity parameters, and inspect gateway environment metadata.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Policy Thresholds */}
        <div className="cyber-card p-5 space-y-4">
          <div className="flex items-center space-x-2 border-b border-cyber-border pb-3">
            <Shield className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-100">Enforcement Thresholds</h3>
          </div>

          <div className="space-y-4 text-xs font-mono">
            <div className="space-y-1">
              <div className="flex justify-between text-slate-300">
                <span>Minimum Intent Contract Match:</span>
                <span className="text-cyan-400 font-bold">{intentThreshold}</span>
              </div>
              <input
                type="range"
                min="0.3"
                max="0.9"
                step="0.05"
                value={intentThreshold}
                onChange={(e) => setIntentThreshold(e.target.value)}
                className="w-full accent-cyan-400"
              />
              <span className="text-[10px] text-slate-500">
                Actions below this threshold are flagged as Intent Drift and rejected or sent for human approval.
              </span>
            </div>

            <div className="space-y-1">
              <div className="flex justify-between text-slate-300">
                <span>Risk Score Block Cutoff:</span>
                <span className="text-red-400 font-bold">{riskCutoff} / 100</span>
              </div>
              <input
                type="range"
                min="30"
                max="85"
                step="5"
                value={riskCutoff}
                onChange={(e) => setRiskCutoff(e.target.value)}
                className="w-full accent-red-400"
              />
              <span className="text-[10px] text-slate-500">
                Composite risk score from path traversal, command injection, or SQL patterns that triggers immediate denial.
              </span>
            </div>
          </div>
        </div>

        {/* HMAC Cryptographic Settings */}
        <div className="cyber-card p-5 space-y-4">
          <div className="flex items-center space-x-2 border-b border-cyber-border pb-3">
            <Key className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-100">HMAC-SHA256 Request Integrity</h3>
          </div>

          <div className="space-y-3 text-xs font-mono">
            <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border space-y-1.5">
              <div className="text-slate-400 text-[11px]">HMAC Verification Algorithm:</div>
              <div className="text-cyan-300 font-bold">HMAC-SHA256 (Canonical Payload + Nonce)</div>
            </div>

            <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border space-y-1.5">
              <div className="text-slate-400 text-[11px]">Maximum Allowed Clock Drift:</div>
              <div className="text-slate-200">300 seconds (5 minutes)</div>
            </div>

            <div className="p-3 rounded-lg bg-cyber-panel border border-cyber-border space-y-1.5">
              <div className="text-slate-400 text-[11px]">Replay Protection:</div>
              <div className="text-emerald-400 flex items-center space-x-1">
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Active (Sliding-window Nonce Store)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Runtime Environment & Health */}
        <div className="cyber-card p-5 space-y-4">
          <div className="flex items-center space-x-2 border-b border-cyber-border pb-3">
            <Database className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-100">Runtime Health & Environment</h3>
          </div>

          <div className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-1 border-b border-cyber-border text-slate-400">
              <span>Backend Gateway URL:</span>
              <span className="text-cyan-300 font-bold">{API_BASE || '(relative origin)'}</span>
            </div>

            <div className="flex justify-between py-1 border-b border-cyber-border text-slate-400">
              <span>FastAPI Documentation:</span>
              <a
                href={`${API_BASE}/docs`}
                target="_blank"
                rel="noreferrer"
                className="text-cyan-400 underline hover:text-cyan-300"
              >
                /docs (Swagger OpenAPI)
              </a>
            </div>

            <div className="flex justify-between py-1 border-b border-cyber-border text-slate-400">
              <span>Health Endpoint:</span>
              <span className="text-emerald-400 font-bold">
                {healthInfo ? `${healthInfo.status} (v${healthInfo.version})` : 'CHECKING...'}
              </span>
            </div>

            <div className="flex justify-between py-1 border-b border-cyber-border text-slate-400">
              <span>Database Engine:</span>
              <span className="text-slate-200 font-bold">
                {healthInfo?.database?.engine || 'SQLite'} (Persistent)
              </span>
            </div>
          </div>
        </div>

        {/* Demo Telemetry Reset Deck */}
        <div className="cyber-card p-5 space-y-4">
          <div className="flex items-center space-x-2 border-b border-cyber-border pb-3">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <h3 className="text-sm font-semibold text-slate-100">Demo Telemetry Seeder & Reset</h3>
          </div>

          <p className="text-xs text-slate-400">
            Resets the SQLite/Postgres database and seeds realistic baseline historical incidents for presentation demonstrations.
          </p>

          <div className="space-y-3 text-xs font-mono">
            <div className="space-y-1">
              <label className="text-slate-400">Admin Authorization Token:</label>
              <input
                type="password"
                value={resetToken}
                onChange={(e) => setResetToken(e.target.value)}
                className="w-full bg-cyber-panel border border-cyber-border rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <button
              onClick={handleResetDemo}
              disabled={isResetting}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? 'animate-spin' : ''}`} />
              <span>{isResetting ? 'RESETTING...' : 'RESET DEMO TELEMETRY'}</span>
            </button>

            {resetStatus && (
              <div className="p-2.5 rounded bg-cyber-dark border border-cyber-border text-slate-300 text-[11px]">
                {resetStatus}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
