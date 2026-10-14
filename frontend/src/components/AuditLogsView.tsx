import React, { useState, useEffect } from 'react';
import { FileText, Download, Search, CheckCircle, XCircle, ShieldCheck } from 'lucide-react';
import { api } from '../services/api';
import { AuditLog } from '../types';

export const AuditLogsView: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [search, setSearch] = useState('');
  const [outcomeFilter, setOutcomeFilter] = useState('ALL');
  const [isLoading, setIsLoading] = useState(true);

  const fetchLogs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAuditLogs(search || undefined, outcomeFilter !== 'ALL' ? outcomeFilter : undefined);
      setLogs(data);
    } catch {
      // ignore
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [outcomeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchLogs();
  };

  const handleExport = async (format: 'json' | 'csv') => {
    try {
      const blob = await api.exportAuditLogs(format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `sentinel-x-audit-report.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch {
      alert('Failed to export audit report');
    }
  };

  return (
    <div className="space-y-6">
      {/* Search and Export Bar */}
      <div className="cyber-card p-4 flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search request ID or action..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-cyber-panel border border-cyber-border rounded-lg pl-9 pr-3 py-1.5 text-xs font-mono text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </form>

        <div className="flex items-center space-x-3 w-full md:w-auto">
          <select
            value={outcomeFilter}
            onChange={(e) => setOutcomeFilter(e.target.value)}
            className="bg-cyber-panel border border-cyber-border rounded-lg px-2.5 py-1.5 text-xs font-mono text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="ALL">All Outcomes</option>
            <option value="ALLOW">ALLOW</option>
            <option value="DENY">DENY</option>
            <option value="QUARANTINED">QUARANTINED</option>
            <option value="DECEPTION_REDIRECT">DECEPTION_REDIRECT</option>
          </select>

          <button
            onClick={() => handleExport('json')}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-cyber-panel hover:bg-slate-800 border border-cyber-border text-slate-200 text-xs font-mono transition"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export JSON</span>
          </button>

          <button
            onClick={() => handleExport('csv')}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-cyber-panel hover:bg-slate-800 border border-cyber-border text-slate-200 text-xs font-mono transition"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="cyber-card p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-cyber-border pb-3">
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-semibold text-slate-100">Cryptographically Verified Audit Trail</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">
            {logs.length} records retrieved
          </span>
        </div>

        {isLoading ? (
          <div className="py-12 text-center text-slate-400 text-xs font-mono">
            Loading audit records...
          </div>
        ) : logs.length === 0 ? (
          <div className="py-12 text-center text-slate-500 text-xs font-mono">
            No audit records found.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-cyber-border text-slate-400 uppercase text-[10px]">
                  <th className="pb-3">Timestamp</th>
                  <th className="pb-3">Request ID</th>
                  <th className="pb-3">Action</th>
                  <th className="pb-3">Outcome</th>
                  <th className="pb-3">HMAC Integrity</th>
                  <th className="pb-3">Sanitized Summary</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-cyber-border">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-900/40 transition">
                    <td className="py-2.5 text-slate-400 text-[11px] whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="py-2.5 text-cyan-300 font-bold text-[11px]">
                      {log.request_id}
                    </td>
                    <td className="py-2.5 text-slate-200">
                      {log.action}
                    </td>
                    <td className="py-2.5">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.outcome === 'ALLOW' || log.outcome === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' :
                        log.outcome === 'DENY' || log.outcome === 'BLOCKED' ? 'bg-red-950 text-red-400 border border-red-500/30' :
                        log.outcome === 'QUARANTINED' ? 'bg-purple-950 text-purple-400 border border-purple-500/30' :
                        'bg-amber-950 text-amber-400 border border-amber-500/30'
                      }`}>
                        {log.outcome}
                      </span>
                    </td>
                    <td className="py-2.5">
                      {log.hmac_verified ? (
                        <span className="flex items-center space-x-1 text-emerald-400 text-[10px]">
                          <ShieldCheck className="w-3.5 h-3.5" />
                          <span>HMAC-SHA256 OK</span>
                        </span>
                      ) : (
                        <span className="flex items-center space-x-1 text-red-400 text-[10px]">
                          <XCircle className="w-3.5 h-3.5" />
                          <span>UNVERIFIED</span>
                        </span>
                      )}
                    </td>
                    <td className="py-2.5 text-slate-300 text-[11px] max-w-sm truncate">
                      {log.sanitized_summary}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
