import React, { useState, useEffect, useCallback } from 'react';
import {
  Database,
  Search,
  Users,
  FileText,
  Activity,
  Layers,
  Code2,
  RefreshCw,
  Eye,
  X,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  RotateCcw,
} from 'lucide-react';
import {
  fetchRawUsers,
  fetchRawClaims,
  fetchRawAgentRuns,
  fetchRawTrustDocs,
  fetchRawFilingDocs,
  fetchRawSentimentDocs,
} from '../api/admin';

type TabType = 'claims' | 'agent-runs' | 'users' | 'trust-tier' | 'filings' | 'sentiment';

const TABS: { id: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'claims', label: 'Claims (Postgres)', icon: FileText },
  { id: 'agent-runs', label: 'Agent Run Logs (Postgres)', icon: Activity },
  { id: 'users', label: 'Users (Postgres)', icon: Users },
  { id: 'trust-tier', label: 'Trust-Tier Store (Qdrant)', icon: Layers },
  { id: 'filings', label: 'Filing Store (Qdrant)', icon: Layers },
  { id: 'sentiment', label: 'Sentiment Corpus (Qdrant)', icon: Layers },
];

export const DataExplorerView: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('claims');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(0);
  const pageSize = 15;

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [data, setData] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedJson, setSelectedJson] = useState<any | null>(null);

  const loadData = useCallback(async (tab: TabType, pageNum: number, search: string) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      if (tab === 'users') {
        const res = await fetchRawUsers(pageNum * pageSize, pageSize, search || undefined);
        setData(Array.isArray(res?.items) ? res.items : []);
        setTotalCount(res?.total || 0);
      } else if (tab === 'claims') {
        const res = await fetchRawClaims(pageNum * pageSize, pageSize, undefined, search || undefined);
        setData(Array.isArray(res?.items) ? res.items : []);
        setTotalCount(res?.total || 0);
      } else if (tab === 'agent-runs') {
        const res = await fetchRawAgentRuns(pageNum * pageSize, pageSize, search || undefined);
        setData(Array.isArray(res?.items) ? res.items : []);
        setTotalCount(res?.total || 0);
      } else if (tab === 'trust-tier') {
        const res = await fetchRawTrustDocs(50, search || undefined);
        setData(Array.isArray(res?.items) ? res.items : []);
        setTotalCount(res?.total || 0);
      } else if (tab === 'filings') {
        const res = await fetchRawFilingDocs(50, search || undefined);
        setData(Array.isArray(res?.items) ? res.items : []);
        setTotalCount(res?.total || 0);
      } else if (tab === 'sentiment') {
        const res = await fetchRawSentimentDocs(50, search || undefined);
        setData(Array.isArray(res?.items) ? res.items : []);
        setTotalCount(res?.total || 0);
      }
    } catch (err: any) {
      console.error('Failed to load raw explorer data:', err);
      const detail = err?.message || 'Could not fetch data for this store.';
      setErrorMsg(detail);
      setData([]);
    } finally {
      setLoading(false);
    }
  }, [pageSize]);

  useEffect(() => {
    loadData(activeTab, page, searchQuery);
  }, [activeTab, page, loadData]);

  const handleTabChange = (newTab: TabType) => {
    if (newTab === activeTab) return;
    setData([]); // Instantly clear stale data from previous tab to prevent render mismatches
    setPage(0);
    setSearchQuery('');
    setActiveTab(newTab);
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(0);
    loadData(activeTab, 0, searchQuery);
  };

  const formatId = (val: any): string => {
    if (val === null || val === undefined) return 'N/A';
    const str = String(val);
    return str.length > 8 ? `${str.substring(0, 8)}...` : str;
  };

  const getStatusPill = (status?: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-emerald-50 text-[#0D8253] border-emerald-300';
      case 'PROCESSING':
        return 'bg-blue-50 text-[#1B3A6B] border-blue-300';
      case 'FAILED':
        return 'bg-red-50 text-[#C53030] border-red-300';
      default:
        return 'bg-slate-50 text-[#64748B] border-[#CBD5E1]';
    }
  };

  return (
    <div className="space-y-5">
      {/* Official Section Masthead */}
      <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Database className="w-5 h-5 text-purple-700" />
            <h2 className="text-lg font-serif font-bold text-[#0F2744]">
              System Data Explorer & Qdrant Store Inspector
            </h2>
          </div>
          <p className="text-xs text-[#64748B] mt-0.5 font-sans">
            Raw PostgreSQL records and Qdrant vector collection points for surveillance auditing and verification sanity checks.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <form onSubmit={handleSearchSubmit} className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by keyword / ticker / ID..."
              className="pl-8 pr-3 py-1.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs font-mono text-[#0F2744] w-64 focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B]"
            />
            <Search className="w-3.5 h-3.5 text-[#64748B] absolute left-2.5 top-2.5" />
          </form>
          <button
            onClick={() => loadData(activeTab, page, searchQuery)}
            className="p-2 border border-[#CBD5E1] rounded-portal hover:bg-[#F1F4F9] text-[#0F2744] cursor-pointer"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Explorer Tabs */}
      <div className="border-b border-[#D8DEE8] flex space-x-1 overflow-x-auto">
        {TABS.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              onClick={() => handleTabChange(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-xs font-mono font-medium border-b-2 transition-all cursor-pointer ${
                isActive
                  ? 'border-purple-700 text-purple-950 bg-white font-bold shadow-2xs'
                  : 'border-transparent text-[#64748B] hover:text-[#0F2744] hover:bg-slate-100'
              }`}
            >
              <Icon className="w-3.5 h-3.5 text-purple-700" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Error Banner */}
      {errorMsg && (
        <div className="p-3.5 rounded-portal bg-[#FDF2F2] border border-[#F8B4B4] flex items-center justify-between gap-3 text-[#C53030]">
          <div className="flex items-center gap-2 text-xs font-sans font-medium">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={() => loadData(activeTab, page, searchQuery)}
            className="px-3 py-1 bg-white border border-[#F8B4B4] rounded text-xs font-mono font-semibold hover:bg-red-50 flex items-center gap-1 cursor-pointer shrink-0"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Data Table */}
      <div className="bg-white rounded-portal border border-[#D8DEE8] shadow-portal-card overflow-hidden">
        <div className="p-3 bg-[#F8FAFC] border-b border-[#E8ECF2] flex items-center justify-between text-xs font-mono text-[#64748B]">
          <span>Displaying {data.length} records (Total indexed: {totalCount})</span>
          <div className="flex items-center gap-1">
            <button
              disabled={page === 0 || loading}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="p-1 border border-[#CBD5E1] rounded bg-white disabled:opacity-40 cursor-pointer"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="px-2">Page {page + 1}</span>
            <button
              disabled={(page + 1) * pageSize >= totalCount || loading}
              onClick={() => setPage((p) => p + 1)}
              className="p-1 border border-[#CBD5E1] rounded bg-white disabled:opacity-40 cursor-pointer"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-12 text-center text-xs font-mono text-[#64748B]">
              Querying database records for {activeTab}...
            </div>
          ) : data.length === 0 ? (
            <div className="p-12 text-center text-xs font-mono text-[#64748B]">
              No matching records found in this collection.
            </div>
          ) : (
            <table className="w-full text-left text-xs font-mono table-register">
              <thead className="bg-slate-100/80 border-b border-[#D8DEE8] text-[#0F2744] uppercase tracking-wider font-semibold">
                {activeTab === 'claims' && (
                  <tr>
                    <th className="p-3">Claim ID</th>
                    <th className="p-3">Ticker</th>
                    <th className="p-3">Source</th>
                    <th className="p-3">Language</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Submitted At</th>
                    <th className="p-3">Raw Rumor Statement</th>
                  </tr>
                )}
                {activeTab === 'agent-runs' && (
                  <tr>
                    <th className="p-3">Run Log ID</th>
                    <th className="p-3">Claim ID</th>
                    <th className="p-3">Steps</th>
                    <th className="p-3">Executed At</th>
                    <th className="p-3 text-right">Inspect State Snapshot</th>
                  </tr>
                )}
                {activeTab === 'users' && (
                  <tr>
                    <th className="p-3">User ID</th>
                    <th className="p-3">Email</th>
                    <th className="p-3">Full Name</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Status</th>
                    <th className="p-3">Created At</th>
                  </tr>
                )}
                {(activeTab === 'trust-tier' || activeTab === 'filings' || activeTab === 'sentiment') && (
                  <tr>
                    <th className="p-3">Vector Point ID</th>
                    <th className="p-3">Collection</th>
                    <th className="p-3">Key Metadata</th>
                    <th className="p-3">Retrieved Chunk Preview</th>
                    <th className="p-3 text-right">Raw Payload</th>
                  </tr>
                )}
              </thead>
              <tbody className="divide-y divide-[#E8ECF2]">
                {activeTab === 'claims' &&
                  data.map((c, idx) => (
                    <tr key={c?.id || idx} className="hover:bg-[#F8FAFC]">
                      <td className="p-3 font-semibold text-[#0F2744]">{formatId(c?.id)}</td>
                      <td className="p-3">
                        <span className="font-bold text-[#1B3A6B]">${c?.ticker || 'GENERAL'}</span>
                      </td>
                      <td className="p-3 text-[#1E293B]">{c?.source_handle || 'N/A'}</td>
                      <td className="p-3 uppercase text-[#64748B]">{c?.language || 'EN'}</td>
                      <td className="p-3">
                        <span className={`px-2 py-0.5 rounded text-[10px] border font-bold ${getStatusPill(c?.status)}`}>
                          {c?.status || 'COMPLETED'}
                        </span>
                      </td>
                      <td className="p-3 text-[#64748B]">{c?.submitted_at ? new Date(c.submitted_at).toLocaleString() : 'N/A'}</td>
                      <td className="p-3 max-w-xs truncate text-[#1E293B]">{c?.raw_text || ''}</td>
                    </tr>
                  ))}

                {activeTab === 'agent-runs' &&
                  data.map((r, idx) => (
                    <tr key={r?.id || idx} className="hover:bg-[#F8FAFC]">
                      <td className="p-3 font-semibold text-[#0F2744]">{formatId(r?.id)}</td>
                      <td className="p-3 text-[#1B3A6B] font-mono">{formatId(r?.claim_id)}</td>
                      <td className="p-3 font-bold">{Array.isArray(r?.execution_trace) ? r.execution_trace.length : 0} agent nodes</td>
                      <td className="p-3 text-[#64748B]">{r?.created_at ? new Date(r.created_at).toLocaleString() : 'N/A'}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => setSelectedJson(r)}
                          className="px-2.5 py-1 rounded bg-purple-50 text-purple-700 border border-purple-200 hover:bg-purple-100 flex items-center gap-1.5 ml-auto font-sans font-medium cursor-pointer"
                        >
                          <Eye className="w-3.5 h-3.5" />
                          <span>View Trace JSON</span>
                        </button>
                      </td>
                    </tr>
                  ))}

                {activeTab === 'users' &&
                  data.map((u, idx) => (
                    <tr key={u?.id || idx} className="hover:bg-[#F8FAFC]">
                      <td className="p-3 font-semibold text-[#0F2744]">{formatId(u?.id)}</td>
                      <td className="p-3 font-medium text-[#0F2744]">{u?.email || 'N/A'}</td>
                      <td className="p-3">{u?.full_name || 'N/A'}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-blue-50 text-blue-900 border border-blue-200 text-[10px] font-bold">
                          {u?.role || 'ANALYST'}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className="text-[#0D8253] font-bold">ACTIVE</span>
                      </td>
                      <td className="p-3 text-[#64748B]">{u?.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}</td>
                    </tr>
                  ))}

                {(activeTab === 'trust-tier' || activeTab === 'filings' || activeTab === 'sentiment') &&
                  data.map((doc, idx) => (
                    <tr key={doc?.id || idx} className="hover:bg-[#F8FAFC]">
                      <td className="p-3 font-semibold text-[#0F2744]">{formatId(doc?.id)}</td>
                      <td className="p-3 text-purple-700">{doc?.collection_name || activeTab}</td>
                      <td className="p-3 text-[#64748B]">
                        {activeTab === 'trust-tier' && `Handle: ${doc?.payload?.source_handle || 'N/A'}`}
                        {activeTab === 'filings' && `Doc: ${doc?.payload?.doc_id || 'N/A'} • Ticker: $${doc?.payload?.ticker || 'N/A'}`}
                        {activeTab === 'sentiment' && `Lang: ${doc?.payload?.language || 'N/A'} • Tone: ${doc?.payload?.tone || 'N/A'}`}
                      </td>
                      <td className="p-3 max-w-md truncate text-[#1E293B] font-sans text-xs">
                        {doc?.text_snippet || JSON.stringify(doc?.payload || {})}
                      </td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => setSelectedJson(doc?.payload || doc)}
                          className="px-2 py-1 rounded bg-[#F1F4F9] text-[#0F2744] hover:bg-[#E2E8F0] border border-[#CBD5E1] flex items-center gap-1 ml-auto font-sans text-[11px] cursor-pointer"
                        >
                          <Code2 className="w-3.5 h-3.5" />
                          <span>Payload</span>
                        </button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Detail JSON Modal */}
      {selectedJson && (
        <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-portal border border-[#D8DEE8] shadow-portal-elevated w-full max-w-3xl max-h-[85vh] flex flex-col">
            <div className="p-4 border-b border-[#E8ECF2] flex items-center justify-between bg-[#F8FAFC]">
              <div className="flex items-center gap-2">
                <Code2 className="w-4 h-4 text-purple-700" />
                <h3 className="text-sm font-mono font-bold text-[#0F2744]">
                  Raw State / Trace Snapshot Viewer
                </h3>
              </div>
              <button
                onClick={() => setSelectedJson(null)}
                className="p-1 text-[#64748B] hover:text-[#0F2744] cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            <div className="p-4 overflow-auto flex-1 bg-slate-900 text-slate-100 font-mono text-xs leading-relaxed">
              <pre>{JSON.stringify(selectedJson, null, 2)}</pre>
            </div>
            <div className="p-3 border-t border-[#E8ECF2] bg-[#F8FAFC] flex justify-end">
              <button
                onClick={() => setSelectedJson(null)}
                className="px-4 py-1.5 bg-[#1B3A6B] text-white text-xs font-medium rounded-portal hover:bg-[#0F2744] cursor-pointer"
              >
                Close Viewer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
