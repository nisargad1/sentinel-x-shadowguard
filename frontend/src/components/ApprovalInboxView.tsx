import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle2, XCircle, AlertOctagon, UserCheck, ShieldAlert, ArrowRight, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { ApprovalItem } from '../types';

export const ApprovalInboxView: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [filter, setFilter] = useState<string>('PENDING');
  const [loading, setLoading] = useState<boolean>(true);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<{ id: string; message: string; success: boolean } | null>(null);

  useEffect(() => {
    loadApprovals();
  }, [filter]);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data = await api.getApprovals(filter === 'ALL' ? undefined : filter);
      setApprovals(data);
    } catch (err) {
      console.error('Failed to load approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (approvalId: string, action: 'APPROVE' | 'REJECT') => {
    setProcessingId(approvalId);
    setFeedback(null);
    try {
      const res = await api.decideApproval(approvalId, action, `Action ${action.toLowerCase()}d by human operator`);
      setFeedback({
        id: approvalId,
        message: res.message || `Successfully marked ${action}`,
        success: true
      });
      // Refresh list
      loadApprovals();
    } catch (err: any) {
      setFeedback({
        id: approvalId,
        message: err.message || 'Operation failed',
        success: false
      });
    } finally {
      setProcessingId(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 border border-slate-800 p-6 rounded-xl backdrop-blur-sm">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <UserCheck className="w-5 h-5 text-amber-400" />
            <h2 className="text-xl font-bold text-white tracking-wide">Human Approval Inbox</h2>
            <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2.5 py-0.5 rounded-full font-mono font-semibold">
              Zero-Trust Gate
            </span>
          </div>
          <p className="text-sm text-slate-400">
            Sensitive AI agent actions (data modifications, status deactivations, financial transfers) are paused pre-execution until an authorized human approves.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex items-center gap-2">
          {['PENDING', 'APPROVED', 'REJECTED', 'ALL'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition ${
                filter === status
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                  : 'bg-slate-800/80 text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-slate-700/60'
              }`}
            >
              {status}
            </button>
          ))}
          <button
            onClick={loadApprovals}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-slate-200 border border-slate-700 transition ml-1"
            title="Refresh"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-cyan-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* List of Approval Items */}
      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-500 font-mono text-sm">
          <RefreshCw className="w-5 h-5 animate-spin mr-2 text-cyan-400" /> Loading approval queue...
        </div>
      ) : approvals.length === 0 ? (
        <div className="bg-slate-900/40 border border-slate-800 rounded-xl p-12 text-center text-slate-400">
          <CheckCircle2 className="w-10 h-10 text-slate-600 mx-auto mb-3" />
          <h3 className="text-base font-semibold text-slate-200 mb-1">Approval Queue Clean</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            No items matching "{filter}". When an autonomous agent attempts a sensitive write action (such as Scenario 4), it will appear here awaiting review.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {approvals.map((item) => {
            const isProcessing = processingId === item.id;
            const itemFeedback = feedback?.id === item.id ? feedback : null;

            return (
              <div
                key={item.id}
                className={`bg-slate-900/50 border rounded-xl p-5 transition space-y-4 ${
                  item.status === 'PENDING'
                    ? 'border-amber-500/40 bg-amber-950/10'
                    : item.status === 'APPROVED'
                    ? 'border-emerald-500/30'
                    : 'border-slate-800'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs text-cyan-400 font-bold bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-800/40">
                        {item.agent_id}
                      </span>
                      <span className="text-slate-400 text-xs">proposes</span>
                      <span className="font-mono text-xs text-amber-300 font-semibold bg-amber-950/30 px-2 py-0.5 rounded border border-amber-800/30">
                        {item.tool_name}:{item.action_name}
                      </span>
                      <span
                        className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${
                          item.status === 'PENDING'
                            ? 'bg-amber-500/20 text-amber-300 border-amber-500/40 animate-pulse'
                            : item.status === 'APPROVED'
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                            : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                    <p className="text-sm text-slate-200 font-medium">
                      "{item.user_intent}"
                    </p>
                  </div>

                  <div className="text-xs font-mono text-slate-400 text-right space-y-0.5">
                    <div>Expires: <span className="text-slate-300">{new Date(item.expires_at).toLocaleTimeString()}</span></div>
                    <div>Est. Cost: <span className="text-cyan-400">${(item.cost_estimate_cents / 100).toFixed(2)}</span></div>
                  </div>
                </div>

                {/* Parameters Box */}
                <div className="bg-slate-950/80 border border-slate-800 rounded-lg p-3 font-mono text-xs text-slate-300">
                  <span className="text-slate-500 block mb-1 text-[11px]">Proposed Parameters (Cryptographically Bound):</span>
                  <pre className="text-cyan-300 whitespace-pre-wrap">{JSON.stringify(item.parameters, null, 2)}</pre>
                </div>

                {/* Feedback Message */}
                {itemFeedback && (
                  <div
                    className={`text-xs p-2.5 rounded-lg border font-mono ${
                      itemFeedback.success
                        ? 'bg-emerald-950/40 border-emerald-500/40 text-emerald-300'
                        : 'bg-rose-950/40 border-rose-500/40 text-rose-300'
                    }`}
                  >
                    {itemFeedback.message}
                  </div>
                )}

                {/* Operator Decision Actions (Only if PENDING) */}
                {item.status === 'PENDING' ? (
                  <div className="flex items-center justify-end gap-3 pt-2 border-t border-slate-800/80">
                    <button
                      onClick={() => handleAction(item.id, 'REJECT')}
                      disabled={isProcessing}
                      className="px-4 py-2 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-50"
                    >
                      <XCircle className="w-3.5 h-3.5" />
                      Reject Action
                    </button>
                    <button
                      onClick={() => handleAction(item.id, 'APPROVE')}
                      disabled={isProcessing}
                      className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 shadow-md shadow-emerald-950/40 transition disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      {isProcessing ? 'Authorizing...' : 'Authorize & Execute'}
                    </button>
                  </div>
                ) : (
                  <div className="pt-2 border-t border-slate-800/60 flex items-center justify-between text-xs font-mono text-slate-500">
                    <span>Reviewed by: {item.approved_by || 'secops-operator@enterprise.com'}</span>
                    <span>Replay Defense: Active (Token Expended)</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
