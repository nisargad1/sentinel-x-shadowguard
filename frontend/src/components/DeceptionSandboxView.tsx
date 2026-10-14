import React, { useState, useEffect } from 'react';
import { Box, ShieldCheck, Terminal, AlertTriangle, FileCode, CheckCircle2, Play } from 'lucide-react';
import { api } from '../services/api';

export const DeceptionSandboxView: React.FC = () => {
  const [status, setStatus] = useState<any>(null);
  const [selectedFile, setSelectedFile] = useState<string>('/etc/passwd');
  const [testPath, setTestPath] = useState<string>('../../../etc/passwd');
  const [simulationResult, setSimulationResult] = useState<any>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    api.getSandboxStatus().then(setStatus).catch(() => {});
  }, []);

  const handleSimulate = async () => {
    setIsSimulating(true);
    setSimulationResult(null);
    try {
      const res = await api.simulateSandbox(testPath);
      setSimulationResult(res);
    } catch (err: any) {
      setSimulationResult({ error: err.message });
    } finally {
      setIsSimulating(false);
    }
  };

  const syntheticFilesContent: Record<string, string> = {
    '/etc/passwd': `# SHADOWGUARD HONEYPOT DECEPTION FS - SYNTHETIC DATA ONLY
root:x:0:0:Fake Deception Root:/root:/bin/sh
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
shadowguard_canary:x:1001:1001:Honeypot Canary:/home/canary:/bin/false
demo_admin:x:1002:1002:Deception Admin Account:/home/admin:/bin/bash
# CANARY_ID: CANARY-X9821-EXFIL-TRAP`,

    '/etc/shadow': `# SHADOWGUARD HONEYPOT DECEPTION FS
root:$6$canary$DUMMY_SALT_HASH_DO_NOT_CRACK:19000:0:99999:7:::
demo_admin:$6$fake$SIMULATED_HASH_CANARY_VALUE:19000:0:99999:7:::`,

    '/fake_credentials.txt': `=== SHADOWGUARD HONEYPOT DECOY CREDENTIALS ===
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE_DECOY
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY_DECOY
CANARY_ENDPOINT=https://canary.sentinel-x.security/trap?id=9921
STATUS=ISOLATED_DECEPTION_ACTIVE`,

    '/fake_users.txt': `username,role,last_login,access_level
honeypot_user1,read_only,2026-10-14,synthetic
trap_admin,sysadmin,2026-10-13,canary_monitored
dummy_auditor,compliance,2026-10-12,synthetic`
  };

  return (
    <div className="space-y-6">
      {/* Intro Card */}
      <div className="cyber-card p-5 space-y-2 border-amber-500/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Box className="w-5 h-5 text-amber-400" />
            <h2 className="text-base font-bold text-white font-mono">
              SHADOW DECEPTION HONEYPOT SANDBOX
            </h2>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-950 text-amber-400 border border-amber-500/30 font-bold">
            SAFE ISOLATION ACTIVE
          </span>
        </div>
        <p className="text-xs text-slate-400 max-w-3xl">
          When an agent attempts path traversal (e.g. <code>../../etc/passwd</code>), SENTINEL-X never touches the real operating system. Instead, it traps the attacker inside an isolated in-memory virtual filesystem populated with synthetic decoy honeypots and canary tokens.
        </p>
      </div>

      {/* Architecture Indicator */}
      <div className="cyber-card p-5 space-y-4">
        <h3 className="text-sm font-semibold text-slate-200 font-mono">
          Containment Architecture & Host Safety
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
          <div className="p-3.5 rounded-xl bg-red-950/20 border border-red-500/30 space-y-2">
            <div className="text-red-400 font-bold flex items-center justify-between">
              <span>REAL HOST DISK</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-red-950 border border-red-500/40">AIR-GAPPED</span>
            </div>
            <p className="text-[11px] text-slate-400">
              Host /etc/passwd, C:\Windows, .env, and production volumes are strictly inaccessible. Zero host filesystem read or write syscalls.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-500/30 space-y-2">
            <div className="text-cyan-400 font-bold flex items-center justify-between">
              <span>GATEWAY PERIMETER</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-cyan-950 border border-cyan-500/40">INTERCEPTING</span>
            </div>
            <p className="text-[11px] text-slate-400">
              PathTraversalDetector parses decoded, encoded, and canonical path syntax. Traversal attempts trigger immediate honeypot routing.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2">
            <div className="text-amber-400 font-bold flex items-center justify-between">
              <span>VIRTUAL HONEYPOT FS</span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-950 border border-amber-500/40">IN-MEMORY</span>
            </div>
            <p className="text-[11px] text-slate-400">
              Synthetic decoys embedded with canary signatures: <code>CANARY-X9821-EXFIL-TRAP</code> to monitor exfiltration telemetry.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Sandbox Simulator */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Simulator Workbench */}
        <div className="cyber-card p-5 space-y-4">
          <h3 className="text-sm font-semibold text-slate-200 font-mono">
            Test Path Traversal Containment
          </h3>

          <div className="space-y-3 text-xs">
            <div className="space-y-1">
              <label className="text-slate-400 font-mono">Simulated Attacker Path Traversal Input:</label>
              <input
                type="text"
                value={testPath}
                onChange={(e) => setTestPath(e.target.value)}
                className="w-full bg-cyber-panel border border-cyber-border rounded-lg px-2.5 py-2 text-slate-200 font-mono focus:outline-none focus:border-amber-500"
              />
            </div>

            <div className="flex gap-2">
              {['../../../etc/passwd', '../../../../etc/shadow', '../../credentials', '..\\..\\windows\\system32'].map((p) => (
                <button
                  key={p}
                  onClick={() => setTestPath(p)}
                  className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono transition"
                >
                  {p}
                </button>
              ))}
            </div>

            <button
              onClick={handleSimulate}
              disabled={isSimulating}
              className="w-full flex items-center justify-center space-x-2 py-2.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black font-mono font-bold text-xs tracking-wider transition shadow-lg shadow-amber-500/20"
            >
              <Play className="w-4 h-4 fill-black" />
              <span>{isSimulating ? 'INTERCEPTING PATH...' : 'PROBE DECEPTION SANDBOX'}</span>
            </button>

            {simulationResult && (
              <div className="p-3.5 rounded-xl bg-amber-950/40 border border-amber-500/40 space-y-2 text-xs font-mono">
                <div className="flex items-center justify-between text-amber-300 font-bold">
                  <span>TRAPPED IN VIRTUAL SANDBOX</span>
                  <span>Risk: {simulationResult.risk_score}</span>
                </div>
                <div className="text-[11px] text-slate-300">
                  Real Filesystem Accessed: <strong className="text-emerald-400">FALSE</strong>
                </div>
                <div className="text-[11px] text-slate-300">
                  Target Served: <span className="text-cyan-300">{simulationResult.served_virtual_target}</span>
                </div>
                <pre className="p-2.5 rounded bg-black/60 border border-cyber-border text-amber-200 text-[10px] overflow-x-auto max-h-36">
                  {simulationResult.content}
                </pre>
              </div>
            )}
          </div>
        </div>

        {/* Synthetic File Decoy Catalog */}
        <div className="cyber-card p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-cyber-border pb-3">
            <h3 className="text-sm font-semibold text-slate-200 font-mono">
              In-Memory Decoy File Catalog
            </h3>
            <span className="text-[10px] font-mono text-emerald-400">
              ALL SYNTHETIC / NO REAL DATA
            </span>
          </div>

          <div className="flex gap-2">
            {Object.keys(syntheticFilesContent).map((file) => (
              <button
                key={file}
                onClick={() => setSelectedFile(file)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition ${
                  selectedFile === file
                    ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/40 font-bold'
                    : 'bg-slate-900 text-slate-400 hover:text-white border border-cyber-border'
                }`}
              >
                {file}
              </button>
            ))}
          </div>

          <pre className="p-3 rounded-xl bg-cyber-dark border border-cyber-border text-slate-300 font-mono text-[11px] overflow-x-auto max-h-64">
            {syntheticFilesContent[selectedFile]}
          </pre>
        </div>
      </div>
    </div>
  );
};
