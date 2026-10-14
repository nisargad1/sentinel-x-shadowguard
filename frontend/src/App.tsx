import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { LandingPageView } from './components/LandingPageView';
import { MetricsOverview } from './components/MetricsOverview';
import { ScenariosView } from './components/ScenariosView';
import { ApprovalInboxView } from './components/ApprovalInboxView';
import { ProofOfValueView } from './components/ProofOfValueView';
import { AgentTrustProfilesView } from './components/AgentTrustProfilesView';
import { LiveEventFeed } from './components/LiveEventFeed';
import { IntentMonitoringView } from './components/IntentMonitoringView';
import { ThreatIntelView } from './components/ThreatIntelView';
import { DeceptionSandboxView } from './components/DeceptionSandboxView';
import { AuditLogsView } from './components/AuditLogsView';
import { SettingsView } from './components/SettingsView';
import { DemoControlPanel } from './components/DemoControlPanel';
import { EventDetailModal } from './components/EventDetailModal';
import { api, API_BASE } from './services/api';
import { TabType, DashboardSummary, SecurityEvent } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<SecurityEvent | null>(null);
  const [isDemoOpen, setIsDemoOpen] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadData = async () => {
    setIsRefreshing(true);
    try {
      const [sum, evts] = await Promise.all([
        api.getDashboardSummary(),
        api.getEvents({ limit: 100 })
      ]);
      setSummary(sum);
      setEvents(evts);
    } catch (err) {
      console.error('Failed to fetch gateway telemetry:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();

    // Polling fallback every 6 seconds to keep live metrics synced
    const interval = setInterval(loadData, 6000);

    let eventSource: EventSource | null = null;
    try {
      eventSource = new EventSource(`${API_BASE}/api/dashboard/stream`);
      eventSource.onmessage = (e) => {
        if (e.data && !e.data.includes('heartbeat')) {
          loadData();
        }
      };
    } catch {
      // Polling handles update
    }

    return () => {
      clearInterval(interval);
      if (eventSource) eventSource.close();
    };
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        systemHealth={summary?.system_health || 'OPERATIONAL'}
        avgRisk={summary?.average_risk_score || 0}
        onRefresh={loadData}
        isRefreshing={isRefreshing}
        onOpenDemo={() => setActiveTab('scenarios')}
      />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          activeTab={activeTab}
          onSelectTab={setActiveTab}
          attacksDetected={summary?.attacks_detected || 0}
          sandboxActivations={summary?.sandbox_activations || 0}
          onOpenDemo={() => setActiveTab('scenarios')}
        />

        <main className="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-slate-950 via-slate-900 to-[#080d1a]">
          <div className="max-w-7xl mx-auto space-y-6">
            {activeTab === 'landing' && (
              <LandingPageView
                onEnterConsole={() => setActiveTab('overview')}
                onExploreScenarios={() => setActiveTab('scenarios')}
              />
            )}

            {activeTab === 'overview' && (
              <MetricsOverview
                summary={summary}
                onSelectEvent={setSelectedEvent}
                onOpenDemo={() => setActiveTab('scenarios')}
              />
            )}

            {activeTab === 'scenarios' && (
              <ScenariosView
                onOpenApprovals={() => setActiveTab('approvals')}
                onOpenAudit={() => setActiveTab('audit')}
              />
            )}

            {activeTab === 'approvals' && (
              <ApprovalInboxView />
            )}

            {activeTab === 'value' && (
              <ProofOfValueView />
            )}

            {activeTab === 'agents' && (
              <AgentTrustProfilesView />
            )}

            {activeTab === 'events' && (
              <LiveEventFeed
                events={events}
                onSelectEvent={setSelectedEvent}
              />
            )}

            {activeTab === 'intents' && (
              <IntentMonitoringView />
            )}

            {activeTab === 'threats' && (
              <ThreatIntelView />
            )}

            {activeTab === 'sandbox' && (
              <DeceptionSandboxView />
            )}

            {activeTab === 'audit' && (
              <AuditLogsView />
            )}

            {activeTab === 'settings' && (
              <SettingsView onRefreshData={loadData} />
            )}
          </div>
        </main>
      </div>

      {/* Modal for viewing detailed security events */}
      {selectedEvent && (
        <EventDetailModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}

      {/* Legacy 4-scenario modal preserved as secondary option */}
      {isDemoOpen && (
        <DemoControlPanel
          isOpen={isDemoOpen}
          onClose={() => setIsDemoOpen(false)}
          onScenarioCompleted={loadData}
        />
      )}
    </div>
  );
};

export default App;

