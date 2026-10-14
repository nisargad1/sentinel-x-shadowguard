import React from 'react';
import { Shield, ShieldAlert, ShieldCheck, RefreshCw, Play, Radio, Sparkles } from 'lucide-react';
import { SystemHealth } from '../types';

interface HeaderProps {
  systemHealth: SystemHealth;
  avgRisk: number;
  onRefresh: () => void;
  isRefreshing: boolean;
  onOpenDemo: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  systemHealth,
  avgRisk,
  onRefresh,
  isRefreshing,
  onOpenDemo
}) => {
  const getHealthBadge = () => {
    switch (systemHealth) {
      case 'OPERATIONAL':
        return {
          icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
          label: 'GATEWAY ACTIVE',
          bg: 'bg-emerald-950/50 border-emerald-500/30 text-emerald-300'
        };
      case 'ELEVATED_THREAT':
        return {
          icon: <Shield className="w-4 h-4 text-amber-400" />,
          label: 'ELEVATED THREAT',
          bg: 'bg-amber-950/50 border-amber-500/30 text-amber-300'
        };
      case 'CRITICAL':
        return {
          icon: <ShieldAlert className="w-4 h-4 text-red-400 animate-pulse" />,
          label: 'CRITICAL THREAT ACTIVE',
          bg: 'bg-red-950/50 border-red-500/30 text-red-300'
        };
      default:
        return {
          icon: <ShieldCheck className="w-4 h-4 text-emerald-400" />,
          label: 'OPERATIONAL',
          bg: 'bg-emerald-950/50 border-emerald-500/30 text-emerald-300'
        };
    }
  };

  const badge = getHealthBadge();

  return (
    <header className="border-b border-slate-800 bg-slate-950/90 backdrop-blur sticky top-0 z-40 px-6 py-3 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <div className="relative flex items-center justify-center w-10 h-10 rounded-lg bg-slate-900 border border-cyan-500/40 shadow-md shadow-cyan-950/50">
          <Shield className="w-6 h-6 text-cyan-400" />
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
          </span>
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-lg font-bold tracking-wider text-slate-100 font-mono">
              SENTINEL<span className="text-cyan-400">-X</span>
            </h1>
            <span className="text-xs px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 font-mono font-bold tracking-wide">
              SMARTGUARD
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">
            The Trust Layer for Autonomous AI Agents
          </p>
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Health status pill */}
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border text-xs font-mono font-semibold ${badge.bg}`}>
          {badge.icon}
          <span>{badge.label}</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300">Avg Risk: {avgRisk}</span>
        </div>

        {/* Live SSE indicator */}
        <div className="hidden md:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
          <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
          <span>LIVE TELEMETRY</span>
        </div>

        {/* 6 Demo Scenarios Shortcut */}
        <button
          onClick={onOpenDemo}
          className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-mono font-bold tracking-wide shadow-lg shadow-cyan-900/30 transition-all hover:scale-105 active:scale-95"
        >
          <Play className="w-3.5 h-3.5 fill-white" />
          <span>6 DEMO SCENARIOS</span>
        </button>

        {/* Refresh */}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          title="Refresh telemetry"
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 transition"
        >
          <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
        </button>

        {/* GitHub link */}
        <a
          href="https://github.com/nisargad1/sentinel-x-shadowguard"
          target="_blank"
          rel="noopener noreferrer"
          title="View on GitHub"
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-600 text-slate-300 hover:text-white transition"
        >
          <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
            <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
          </svg>
        </a>
      </div>
    </header>
  );
};
