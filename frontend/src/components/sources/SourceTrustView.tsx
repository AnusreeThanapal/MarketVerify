import React, { useState, useEffect } from 'react';
import {
  User,
  XCircle,
  Search,
  CheckCircle2,
  AlertCircle,
  RotateCcw,
  Loader2,
} from 'lucide-react';
import { SourceTrustHistory } from '../../types/api';
import { getSourceTrustHistory } from '../../api/sources';
import { TrustScoreGauge } from '../trace/TrustScoreGauge';

const POPULAR_SOURCES = [
  '@dalalstreetinsider',
  '@tamil_market_guru',
  '@fin_leaks_raw',
  '@pump_and_dump_scanner',
  '@reliable_news_wire',
  '@market_rumor_feed',
];

export const SourceTrustView: React.FC = () => {
  const [selectedHandle, setSelectedHandle] = useState('@dalalstreetinsider');
  const [customInput, setCustomInput] = useState('');
  const [data, setData] = useState<SourceTrustHistory | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadHistory(selectedHandle);
  }, [selectedHandle]);

  const loadHistory = async (handle: string) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const res = await getSourceTrustHistory(handle);
      setData(res);
    } catch (err: any) {
      console.error('Failed to load source history:', err);
      const detail = err?.message || 'Could not retrieve trust history for this source handle.';
      setErrorMsg(detail);
      setData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!customInput.trim()) return;
    const h = customInput.trim().startsWith('@') ? customInput.trim() : `@${customInput.trim()}`;
    setSelectedHandle(h);
  };

  // Safe normalized values from backend schema
  const trajectories = Array.isArray(data?.recent_trajectories)
    ? data.recent_trajectories
    : Array.isArray(data?.trajectories)
    ? data.trajectories
    : [];

  const trustScore = typeof data?.trust_score === 'number'
    ? data.trust_score
    : typeof data?.bayesian_trust_score === 'number'
    ? data.bayesian_trust_score
    : 0.5;

  const totalClaims = data?.total_claims_evaluated ?? data?.total_historical_claims ?? trajectories.length;
  const accurateClaims = data?.accurate_claims_count ?? data?.accurate_claims ?? trajectories.filter((t) => t?.was_accurate).length;
  const falseClaims = data?.false_claims ?? Math.max(0, totalClaims - accurateClaims);
  const accuracyPercent = typeof data?.accuracy_rate === 'number'
    ? (data.accuracy_rate <= 1 ? (data.accuracy_rate * 100).toFixed(1) : data.accuracy_rate.toFixed(1))
    : totalClaims > 0
    ? ((accurateClaims / totalClaims) * 100).toFixed(1)
    : '0.0';

  return (
    <div className="space-y-5">
      {/* Search Header */}
      <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#E8ECF2] pb-4 mb-3.5">
          <div>
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-[#1B3A6B]" />
              <h2 className="text-base font-serif font-bold text-[#0F2744]">
                Social Intelligence Source Surveillance & Accuracy Docket
              </h2>
            </div>
            <p className="text-xs text-[#64748B] mt-0.5 font-sans">
              Bayesian historical track record tracking calculated across past market rumors and actual corporate disclosures.
            </p>
          </div>

          <form onSubmit={handleCustomSubmit} className="flex items-center gap-2">
            <input
              type="text"
              value={customInput}
              onChange={(e) => setCustomInput(e.target.value)}
              placeholder="Search source e.g. @dalalstreetinsider"
              className="px-3 py-1.5 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs font-mono text-[#0F2744] w-64 focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B]"
            />
            <button
              type="submit"
              className="px-3.5 py-1.5 bg-[#1B3A6B] hover:bg-[#0F2744] text-white rounded-portal text-xs font-semibold transition-colors flex items-center gap-1 cursor-pointer"
            >
              <Search className="w-3.5 h-3.5" />
              <span>Inspect</span>
            </button>
          </form>
        </div>

        {/* Quick Select Preset Handles */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] font-mono text-[#64748B]">Surveilled Handles:</span>
          {POPULAR_SOURCES.map((handle) => (
            <button
              key={handle}
              onClick={() => setSelectedHandle(handle)}
              className={`text-xs font-mono px-2.5 py-1 rounded transition-colors cursor-pointer ${
                selectedHandle === handle
                  ? 'bg-[#1B3A6B] text-white font-bold'
                  : 'bg-[#F1F4F9] text-[#0F2744] hover:bg-[#E2E8F0] border border-[#CBD5E1]'
              }`}
            >
              {handle}
            </button>
          ))}
        </div>
      </div>

      {/* Error Banner */}
      {errorMsg && (
        <div className="p-3.5 rounded-portal bg-[#FDF2F2] border border-[#F8B4B4] flex items-center justify-between gap-3 text-[#C53030]">
          <div className="flex items-center gap-2 text-xs font-sans font-medium">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={() => loadHistory(selectedHandle)}
            className="px-3 py-1 bg-white border border-[#F8B4B4] rounded text-xs font-mono font-semibold hover:bg-red-50 flex items-center gap-1 cursor-pointer shrink-0"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Main Content */}
      {isLoading ? (
        <div className="bg-white p-12 rounded-portal border border-[#D8DEE8] shadow-portal-card text-center text-xs font-mono text-[#64748B] flex flex-col items-center justify-center gap-2.5">
          <Loader2 className="w-6 h-6 animate-spin text-[#1B3A6B]" />
          <span>Querying Bayesian historical trajectory models for {selectedHandle}...</span>
        </div>
      ) : !data ? (
        <div className="bg-white p-12 rounded-portal border border-[#D8DEE8] shadow-portal-card text-center text-xs font-mono text-[#64748B]">
          No historical surveillance data available for {selectedHandle}.
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
          {/* Left Column: Source Profile & Gauge */}
          <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card space-y-5 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-3 border-b border-[#E8ECF2] pb-3">
                <div className="w-10 h-10 rounded-portal bg-blue-50 border border-blue-200 text-[#1B3A6B] flex items-center justify-center font-mono font-bold text-sm">
                  {selectedHandle.substring(1, 3).toUpperCase()}
                </div>
                <div>
                  <h3 className="font-serif font-bold text-sm text-[#0F2744]">
                    {data.source_name || selectedHandle}
                  </h3>
                  <p className="font-mono text-xs text-[#64748B]">{selectedHandle}</p>
                </div>
              </div>

              <div className="pt-1">
                <TrustScoreGauge score={trustScore} label="Calibrated Credibility" />
              </div>

              {/* Stats Breakdown Grid */}
              <div className="grid grid-cols-2 gap-2 pt-1 text-center text-xs font-mono">
                <div className="p-2.5 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
                  <div className="text-[#64748B] text-[10px] uppercase">Historical Claims</div>
                  <div className="font-bold text-[#0F2744] text-sm mt-0.5">{totalClaims}</div>
                </div>
                <div className="p-2.5 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
                  <div className="text-[#64748B] text-[10px] uppercase">Raw Accuracy</div>
                  <div className="font-bold text-[#0D8253] text-sm mt-0.5">{accuracyPercent}%</div>
                </div>
                <div className="p-2.5 rounded-portal bg-emerald-50 border border-emerald-200">
                  <div className="text-emerald-800 text-[10px] uppercase">Confirmed True</div>
                  <div className="font-bold text-emerald-800 text-sm mt-0.5">{accurateClaims}</div>
                </div>
                <div className="p-2.5 rounded-portal bg-red-50 border border-red-200">
                  <div className="text-red-800 text-[10px] uppercase">False / Refuted</div>
                  <div className="font-bold text-red-800 text-sm mt-0.5">{falseClaims}</div>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1] text-[11px] font-sans text-[#64748B]">
              Bayesian Beta distribution prior ($\alpha=2, \beta=2$) applied to prevent overconfidence on sparse social data.
            </div>
          </div>

          {/* Right 2 Columns: Trajectory History Ledger */}
          <div className="lg:col-span-2 bg-white rounded-portal border border-[#D8DEE8] shadow-portal-card overflow-hidden flex flex-col justify-between">
            <div className="p-3.5 border-b border-[#E8ECF2] bg-[#F8FAFC] flex items-center justify-between">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-[#0F2744]">
                Historical Rumor Trajectory & Corporate Outcomes ({trajectories.length})
              </span>
              <span className="text-[10px] font-mono text-[#64748B]">SEBI Grounded Ledger</span>
            </div>

            <div className="divide-y divide-[#E8ECF2] max-h-[520px] overflow-y-auto">
              {trajectories.length === 0 ? (
                <div className="p-12 text-center text-xs font-mono text-[#64748B]">
                  No past claims recorded for this handle.
                </div>
              ) : (
                trajectories.map((item, idx) => (
                  <div key={item?.id || idx} className="p-4 hover:bg-[#F8FAFC] transition-colors space-y-2 font-sans text-xs">
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-[#1B3A6B]">
                          ${item?.ticker || 'GENERAL'}
                        </span>
                        <span className="font-mono text-[10px] px-1.5 py-0.2 rounded bg-[#F1F4F9] text-[#64748B] uppercase border border-[#CBD5E1]">
                          {item?.category || 'MARKET RUMOR'}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 font-mono text-[11px]">
                        <span className="text-[#64748B]">Date: {item?.outcome_date ? String(item.outcome_date).substring(0, 10) : 'Recorded'}</span>
                        {item?.was_accurate ? (
                          <span className="inline-flex items-center gap-1 text-[#0D8253] font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                            <CheckCircle2 className="w-3 h-3" />
                            <span>Confirmed True</span>
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 text-[#C53030] font-bold bg-red-50 px-2 py-0.5 rounded border border-red-200">
                            <XCircle className="w-3 h-3" />
                            <span>Debunked / False</span>
                          </span>
                        )}
                      </div>
                    </div>

                    <p className="text-[#1E293B] font-medium leading-snug">
                      "{item?.past_claim_text}"
                    </p>

                    <div className="p-2.5 rounded bg-[#F8FAFC] border border-[#CBD5E1] text-[#64748B] text-[11px] leading-relaxed font-sans">
                      <span className="font-mono font-bold text-[#0F2744] block mb-0.5">Outcome Determination:</span>
                      {item?.outcome_summary || 'Verified against regulatory disclosure records.'}
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="p-2.5 border-t border-[#E8ECF2] bg-[#FAFAFA] text-right text-[10px] font-mono text-[#64748B]">
              Grounding: SEBI LODR Regulation 30 Historical Verification Database
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
