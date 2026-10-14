import React from 'react';
import { Shield, Sparkles, CheckCircle2, XCircle, Clock, ArrowRight, Cpu, Layers, DollarSign, Bot, Terminal, Lock } from 'lucide-react';

interface LandingPageViewProps {
  onEnterConsole: () => void;
  onExploreScenarios: () => void;
}

export const LandingPageView: React.FC<LandingPageViewProps> = ({ onEnterConsole, onExploreScenarios }) => {
  return (
    <div className="space-y-16 pb-12">
      {/* Hero Section */}
      <div className="text-center space-y-6 pt-8 max-w-4xl mx-auto">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono font-semibold tracking-wider uppercase animate-fade-in">
          <Sparkles className="w-3.5 h-3.5" />
          The Trust Layer for Autonomous AI Agents
        </div>

        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-tight">
          Evaluate Agent Actions <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-teal-300 to-blue-500">
            Before They Execute.
          </span>
        </h1>

        <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
          AI agents propose actions that are unnecessary, unauthorized, risky, or expensive.
          <strong className="text-white font-semibold"> SENTINEL-X SmartGuard</strong> interposes at runtime to evaluate intent alignment, permissions, risk, cost, and efficiency before a single tool executes.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button
            onClick={onEnterConsole}
            className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-xl shadow-cyan-950/50 flex items-center gap-2 transition"
          >
            Launch Runtime Console
            <ArrowRight className="w-4 h-4" />
          </button>
          <button
            onClick={onExploreScenarios}
            className="px-6 py-3 rounded-xl bg-slate-800/90 hover:bg-slate-800 text-slate-200 border border-slate-700 font-semibold text-sm flex items-center gap-2 transition"
          >
            Run 6 Demo Scenarios
          </button>
        </div>
      </div>

      {/* The 4 Decisions Cards */}
      <div className="space-y-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white tracking-wide">The Action Value Engine: 4 Primary Decisions</h2>
          <p className="text-sm text-slate-400 max-w-xl mx-auto">
            Every proposed tool execution is evaluated across 5 dimensions and returns exactly one unambiguous decision.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* ALLOW */}
          <div className="bg-slate-900/40 border border-emerald-500/30 p-5 rounded-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center gap-2 text-emerald-400 font-mono font-bold text-sm">
              <CheckCircle2 className="w-5 h-5" />
              ALLOW
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Satisfies applicable intent contracts, agent resource allowlists, and spending budgets. Executes through controlled adapter.
            </p>
            <span className="text-[10px] font-mono text-emerald-400/80 block">Example: Read authorized report.pdf</span>
          </div>

          {/* OPTIMIZE */}
          <div className="bg-slate-900/40 border border-cyan-500/30 p-5 rounded-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center gap-2 text-cyan-400 font-mono font-bold text-sm">
              <Sparkles className="w-5 h-5" />
              OPTIMIZE
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Identifies redundant searches or eligible honeypot redirections. Replaces with safe cached results, saving token costs.
            </p>
            <span className="text-[10px] font-mono text-cyan-400/80 block">Example: Duplicate query cache reuse</span>
          </div>

          {/* ASK */}
          <div className="bg-slate-900/40 border border-amber-500/30 p-5 rounded-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center gap-2 text-amber-400 font-mono font-bold text-sm">
              <Clock className="w-5 h-5" />
              ASK (HUMAN APPROVAL)
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Sensitive write actions, data deactivations, or financial transfers pause execution until an authorized human reviews.
            </p>
            <span className="text-[10px] font-mono text-amber-400/80 block">Example: Update customer status</span>
          </div>

          {/* BLOCK */}
          <div className="bg-slate-900/40 border border-rose-500/30 p-5 rounded-xl space-y-3 relative overflow-hidden">
            <div className="flex items-center gap-2 text-rose-400 font-mono font-bold text-sm">
              <XCircle className="w-5 h-5" />
              BLOCK
            </div>
            <p className="text-xs text-slate-300 leading-relaxed">
              Strictly denies unauthorized file access, prompt injections, shell/SQL injections, or budget limit violations.
            </p>
            <span className="text-[10px] font-mono text-rose-400/80 block">Example: Restricted payroll CSV access</span>
          </div>
        </div>
      </div>

      {/* 5-Stage Architecture Section */}
      <div className="bg-slate-900/40 border border-slate-800 p-8 rounded-2xl space-y-8">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white tracking-wide">Runtime Enforcement Architecture</h2>
          <p className="text-sm text-slate-400">
            A hardened inline perimeter separating autonomous AI reasoning from real infrastructure.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-center font-mono text-xs">
          <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2">
            <div className="text-cyan-400 font-bold">1. AUTHENTICATE</div>
            <p className="text-[11px] text-slate-400 font-sans">HMAC-SHA256 signature and nonce replay protection</p>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2">
            <div className="text-cyan-400 font-bold">2. INTENT MATCH</div>
            <p className="text-[11px] text-slate-400 font-sans">Deterministic set allowlists bound to user prompt</p>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2">
            <div className="text-cyan-400 font-bold">3. SHIELD GATES</div>
            <p className="text-[11px] text-slate-400 font-sans">Canonical traversal, shell, SQL, & prompt injection scans</p>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2">
            <div className="text-cyan-400 font-bold">4. COST & BUDGET</div>
            <p className="text-[11px] text-slate-400 font-sans">Atomic per-agent & workspace spending limit checks</p>
          </div>
          <div className="bg-slate-950/70 border border-slate-800 p-4 rounded-xl space-y-2">
            <div className="text-cyan-400 font-bold">5. CONTROLLED EXEC</div>
            <p className="text-[11px] text-slate-400 font-sans">Controlled adapter execution + DLP token redaction</p>
          </div>
        </div>
      </div>

      {/* Developer Integration Snippet */}
      <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-3 font-mono text-xs">
        <div className="flex items-center justify-between text-slate-400">
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-cyan-400" />
            <span>Integrate with SmartGuard in 3 Lines of Python</span>
          </div>
          <span className="text-[11px] text-slate-500">Python 3.11+ / MCP Native</span>
        </div>
        <pre className="text-slate-200 overflow-x-auto p-4 bg-slate-900/60 rounded border border-slate-800/80 leading-relaxed">
{`from smartguard_client import SmartGuardClient

client = SmartGuardClient(base_url="http://localhost:8000")

# Intercept tool call before execution
decision = client.propose_action(
    agent_id="finance-analyst-agent",
    user_intent="Summarize Q3 earnings report",
    tool_name="read_demo_file",
    parameters={"filename": "report.pdf"}
)

if decision["decision"] == "ALLOW":
    result = decision["execution_result"]`}
        </pre>
      </div>

      {/* CTA Box */}
      <div className="text-center p-8 bg-gradient-to-r from-cyan-950/30 via-slate-900 to-slate-950 border border-cyan-500/30 rounded-2xl space-y-4">
        <h3 className="text-xl font-bold text-white">Ready to secure your autonomous AI agent fleet?</h3>
        <p className="text-xs text-slate-400 max-w-md mx-auto">
          Explore the runtime console, run the 6 battle-tested demo scenarios, or inspect live audit records.
        </p>
        <button
          onClick={onEnterConsole}
          className="px-6 py-2.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs uppercase tracking-wider transition"
        >
          Open Runtime Console
        </button>
      </div>
    </div>
  );
};
