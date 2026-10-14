import React from 'react';
import {
  LayoutDashboard,
  Activity,
  Compass,
  AlertTriangle,
  Box,
  FileText,
  Settings,
  Sparkles,
  ShieldAlert
} from 'lucide-react';
import { TabType } from '../types';

interface SidebarProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
  attacksDetected: number;
  sandboxActivations: number;
  onOpenDemo: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  attacksDetected,
  sandboxActivations,
  onOpenDemo
}) => {
  const navItems = [
    {
      id: 'overview' as TabType,
      label: 'Overview',
      icon: <LayoutDashboard className="w-4 h-4" />
    },
    {
      id: 'events' as TabType,
      label: 'Live Security Feed',
      icon: <Activity className="w-4 h-4" />,
      badge: attacksDetected > 0 ? `${attacksDetected}` : undefined,
      badgeColor: 'bg-red-500/20 text-red-400 border border-red-500/30'
    },
    {
      id: 'intents' as TabType,
      label: 'Intent Monitoring',
      icon: <Compass className="w-4 h-4" />
    },
    {
      id: 'threats' as TabType,
      label: 'Threat Intelligence',
      icon: <AlertTriangle className="w-4 h-4" />
    },
    {
      id: 'sandbox' as TabType,
      label: 'Shadow Sandbox',
      icon: <Box className="w-4 h-4" />,
      badge: sandboxActivations > 0 ? `${sandboxActivations}` : undefined,
      badgeColor: 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
    },
    {
      id: 'audit' as TabType,
      label: 'Audit & Compliance',
      icon: <FileText className="w-4 h-4" />
    },
    {
      id: 'settings' as TabType,
      label: 'Policy Settings',
      icon: <Settings className="w-4 h-4" />
    }
  ];

  return (
    <aside className="w-64 border-r border-cyber-border bg-cyber-dark flex flex-col justify-between py-4 shrink-0">
      <div className="px-3 space-y-1">
        <div className="px-3 py-2 text-xs font-mono font-semibold text-slate-500 uppercase tracking-wider">
          Security Gateway
        </div>

        {navItems.map((item) => {
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-950'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className={isActive ? 'text-cyan-400' : 'text-slate-400'}>
                  {item.icon}
                </span>
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded-full font-bold ${item.badgeColor}`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Demo Callout Card */}
      <div className="p-3">
        <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-b from-cyan-950/40 to-slate-900/80 p-3.5 space-y-2.5">
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>HACKATHON DEMO</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            Run the 4 standardized test scenarios live against the MCP security gateway.
          </p>
          <button
            onClick={onOpenDemo}
            className="w-full flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-black text-xs font-mono font-bold tracking-wide transition"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            <span>LAUNCH DEMO</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
