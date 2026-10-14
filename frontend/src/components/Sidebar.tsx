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
  ShieldAlert,
  PlayCircle,
  UserCheck,
  TrendingUp,
  Bot
} from 'lucide-react';
import { TabType } from '../types';

interface SidebarProps {
  activeTab: TabType;
  onSelectTab: (tab: TabType) => void;
  attacksDetected: number;
  sandboxActivations: number;
  onOpenDemo: () => void;
}

interface NavItem {
  id: TabType;
  label: string;
  icon: React.ReactNode;
  badge?: string;
  badgeColor?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  attacksDetected,
  sandboxActivations,
  onOpenDemo
}) => {
  const primaryNav: NavItem[] = [
    {
      id: 'landing',
      label: 'Product Overview',
      icon: <Sparkles className="w-4 h-4 text-cyan-400" />
    },
    {
      id: 'overview',
      label: 'Runtime Console',
      icon: <LayoutDashboard className="w-4 h-4" />
    },
    {
      id: 'scenarios',
      label: '6 Demo Scenarios',
      icon: <PlayCircle className="w-4 h-4 text-cyan-400" />
    },
    {
      id: 'approvals',
      label: 'Approval Inbox',
      icon: <UserCheck className="w-4 h-4 text-amber-400" />
    },
    {
      id: 'value',
      label: 'Proof of Value & ROI',
      icon: <TrendingUp className="w-4 h-4 text-emerald-400" />
    },
    {
      id: 'agents',
      label: 'Agent Trust Profiles',
      icon: <Bot className="w-4 h-4 text-indigo-400" />
    }
  ];

  const securityNav: NavItem[] = [
    {
      id: 'events',
      label: 'Live Security Feed',
      icon: <Activity className="w-4 h-4" />,
      badge: attacksDetected > 0 ? `${attacksDetected}` : undefined,
      badgeColor: 'bg-red-500/20 text-red-400 border border-red-500/30'
    },
    {
      id: 'intents',
      label: 'Intent Monitoring',
      icon: <Compass className="w-4 h-4" />
    },
    {
      id: 'threats',
      label: 'Threat Intelligence',
      icon: <AlertTriangle className="w-4 h-4" />
    },
    {
      id: 'sandbox',
      label: 'Shadow Sandbox',
      icon: <Box className="w-4 h-4" />,
      badge: sandboxActivations > 0 ? `${sandboxActivations}` : undefined,
      badgeColor: 'bg-amber-500/20 text-amber-400 border border-amber-500/30'
    },
    {
      id: 'audit',
      label: 'Audit & Compliance',
      icon: <FileText className="w-4 h-4" />
    },
    {
      id: 'settings',
      label: 'Policy Settings',
      icon: <Settings className="w-4 h-4" />
    }
  ];

  const renderNavGroup = (title: string, items: NavItem[]) => (
    <div className="space-y-1 mb-4">
      <div className="px-3 py-1.5 text-[11px] font-mono font-semibold text-slate-500 uppercase tracking-wider">
        {title}
      </div>
      {items.map((item) => {
        const isActive = activeTab === item.id;
        return (
          <button
            key={item.id}
            onClick={() => onSelectTab(item.id)}
            className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
              isActive
                ? 'bg-cyan-950/60 text-cyan-300 border border-cyan-500/30 shadow-sm shadow-cyan-950'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <div className="flex items-center space-x-2.5">
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
  );

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col justify-between py-4 shrink-0 overflow-y-auto">
      <div className="px-3">
        {renderNavGroup('Action Value Engine', primaryNav)}
        {renderNavGroup('Security & Forensics', securityNav)}
      </div>

      {/* Demo Callout Card */}
      <div className="p-3">
        <div className="rounded-xl border border-cyan-500/30 bg-gradient-to-b from-cyan-950/40 to-slate-900/80 p-3.5 space-y-2.5">
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>6 DEMO SCENARIOS</span>
          </div>
          <p className="text-[11px] text-slate-300 leading-relaxed">
            Run the 6 reproducible demo scenarios live against real backend policy logic.
          </p>
          <button
            onClick={() => onSelectTab('scenarios')}
            className="w-full flex items-center justify-center space-x-1.5 py-2 px-3 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-mono font-bold tracking-wide transition"
          >
            <PlayCircle className="w-3.5 h-3.5" />
            <span>OPEN 6 SCENARIOS</span>
          </button>
        </div>
      </div>
    </aside>
  );
};
