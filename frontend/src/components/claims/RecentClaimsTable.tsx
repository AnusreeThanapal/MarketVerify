import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  ShieldCheck,
  XCircle,
  AlertTriangle,
  HelpCircle,
  Sparkles,
  ArrowRight,
  Clock,
  Filter,
} from 'lucide-react';
import { ClaimSummary, VerdictStatus } from '../../types/api';

interface RecentClaimsTableProps {
  claims: ClaimSummary[];
  isLoading: boolean;
}

export const RecentClaimsTable: React.FC<RecentClaimsTableProps> = ({
  claims,
  isLoading,
}) => {
  const navigate = useNavigate();
  const [filterTicker, setFilterTicker] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const tickers = ['ALL', ...Array.from(new Set(claims.map((c) => c.ticker).filter(Boolean)))];

  const filteredClaims = claims.filter((c) => {
    const matchesTicker = filterTicker === 'ALL' || c.ticker === filterTicker;
    const matchesSearch =
      searchQuery === '' ||
      c.raw_text.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.source_handle.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (c.ticker && c.ticker.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesTicker && matchesSearch;
  });

  const getVerdictBadge = (status?: VerdictStatus) => {
    switch (status) {
      case 'CORROBORATED_OFFICIAL':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono font-bold bg-emerald-50 text-[#0D8253] border border-emerald-300 shadow-2xs">
            <ShieldCheck className="w-4 h-4 text-[#0D8253]" />
            <span>CORROBORATED</span>
          </span>
        );
      case 'CONTRADICTED_BY_FILING':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono font-bold bg-red-50 text-[#C53030] border border-red-300 shadow-2xs">
            <XCircle className="w-4 h-4 text-[#C53030]" />
            <span>CONTRADICTED</span>
          </span>
        );
      case 'UNVERIFIED_RUMOR':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono font-bold bg-amber-50 text-[#B45309] border border-amber-300 shadow-2xs">
            <AlertTriangle className="w-4 h-4 text-[#B45309]" />
            <span>UNVERIFIED</span>
          </span>
        );
      case 'LIKELY_CREDIBLE':
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono font-bold bg-blue-50 text-[#1B3A6B] border border-blue-300 shadow-2xs">
            <Sparkles className="w-4 h-4 text-[#1B3A6B]" />
            <span>LIKELY CREDIBLE</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded text-xs font-mono text-[#64748B] bg-slate-100 border border-[#CBD5E1]">
            <HelpCircle className="w-4 h-4" />
            <span>PENDING</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-portal border border-[#D8DEE8] shadow-portal-card overflow-hidden">
      {/* Table Header Filter Controls */}
      <div className="p-5 border-b border-[#E8ECF2] bg-[#F8FAFC] flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <Filter className="w-4 h-4 text-[#1B3A6B]" />
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#0F2744]">
            Official Surveillance Claims Register
          </h3>
          <span className="text-xs text-[#64748B] font-mono">
            ({filteredClaims.length} records)
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Ticker Filter Pills */}
          <div className="flex items-center gap-1 overflow-x-auto">
            {tickers.map((t) => (
              <button
                key={t}
                onClick={() => setFilterTicker(t || 'ALL')}
                className={`text-xs font-mono px-2.5 py-1 rounded transition-colors cursor-pointer ${
                  filterTicker === t
                    ? 'bg-[#1B3A6B] text-white font-bold'
                    : 'bg-white text-[#475569] hover:text-[#0F2744] border border-[#CBD5E1]'
                }`}
              >
                {t === 'ALL' ? 'All Equities' : `$${t}`}
              </button>
            ))}
          </div>

          {/* Text Search Box */}
          <div className="relative">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search statements, tickers, sources..."
              className="pl-8 pr-3 py-1.5 bg-white border border-[#CBD5E1] rounded-portal text-xs text-[#1E293B] placeholder-[#94A3B8] font-sans w-64 focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B]"
            />
            <Search className="w-3.5 h-3.5 text-[#64748B] absolute left-2.5 top-2.5" />
          </div>
        </div>
      </div>

      {/* Claims List */}
      {isLoading ? (
        <div className="p-16 text-center text-xs font-mono text-[#64748B]">
          Loading surveillance registry records...
        </div>
      ) : filteredClaims.length === 0 ? (
        <div className="p-16 text-center text-xs font-mono text-[#64748B]">
          No market claims found matching the active filter.
        </div>
      ) : (
        <div className="divide-y divide-[#E8ECF2]">
          {filteredClaims.map((claim) => (
            <div
              key={claim.id}
              onClick={() => navigate(`/trace/${claim.id}`)}
              className="p-5 hover:bg-[#F8FAFC] transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4 group"
            >
              {/* Primary Content: Claim Statement with Clear Hierarchy */}
              <div className="space-y-2 flex-1">
                <p className="text-sm font-serif font-bold text-[#0F2744] group-hover:text-[#1B3A6B] transition-colors leading-relaxed">
                  "{claim.raw_text}"
                </p>

                {/* Secondary Metadata Row (De-emphasized) */}
                <div className="flex items-center gap-3 text-xs font-mono text-[#64748B] flex-wrap">
                  <span className="font-bold text-[#1B3A6B] bg-[#F1F4F9] px-2 py-0.5 rounded border border-[#CBD5E1]">
                    ${claim.ticker || 'GENERAL'}
                  </span>
                  <span>
                    Source: <strong className="text-[#334155]">{claim.source_handle}</strong>
                  </span>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-[#94A3B8]" />
                    <span>{new Date(claim.submitted_at).toLocaleDateString()} {new Date(claim.submitted_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>
                  <span>•</span>
                  <span className="text-[#94A3B8]">Docket: {claim.id.substring(0, 8)}...</span>
                </div>
              </div>

              {/* Prominent Verdict Badge & Action Button */}
              <div className="flex items-center gap-3 shrink-0">
                {getVerdictBadge(claim.verdict_status)}
                
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/trace/${claim.id}`);
                  }}
                  className="px-3 py-1.5 rounded-portal bg-[#F1F4F9] group-hover:bg-[#1B3A6B] group-hover:text-white border border-[#CBD5E1] text-[#0F2744] text-xs font-mono font-semibold transition-all flex items-center gap-1 cursor-pointer"
                >
                  <span>Trace</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
