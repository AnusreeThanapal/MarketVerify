import React, { useState, useEffect, useCallback } from 'react';
import { RecentClaimsTable } from '../components/claims/RecentClaimsTable';
import { ClaimSummary } from '../types/api';
import { listRecentClaims } from '../api/claims';
import {
  RefreshCw,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  AlertCircle,
  RotateCcw,
  Loader2,
} from 'lucide-react';

export const DashboardView: React.FC = () => {
  const [claims, setClaims] = useState<ClaimSummary[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchClaims = useCallback(async () => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      const data = await listRecentClaims(1, 50);
      if (data && Array.isArray(data.items)) {
        setClaims(data.items);
      } else if (Array.isArray(data)) {
        setClaims(data);
      } else {
        setClaims([]);
      }
    } catch (err: any) {
      console.error('Failed to load recent claims:', err);
      const detail =
        err?.message ||
        err?.data?.detail ||
        'Failed to connect to surveillance database. Please verify backend service.';
      setErrorMsg(detail);
      setClaims([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  const safeClaims = Array.isArray(claims) ? claims : [];

  const corroboratedCount = safeClaims.filter(
    (c) => c && c.verdict_status === 'CORROBORATED_OFFICIAL'
  ).length;
  const contradictedCount = safeClaims.filter(
    (c) => c && c.verdict_status === 'CONTRADICTED_BY_FILING'
  ).length;
  const unverifiedCount = safeClaims.filter(
    (c) => c && c.verdict_status === 'UNVERIFIED_RUMOR'
  ).length;

  return (
    <div className="space-y-4">
      {/* Top Workstation Bar */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-serif font-bold text-[#0F2744]">
            Surveillance Claims Register & Audit Ledger
          </h2>
          <p className="text-[11px] text-[#475569] font-sans">
            Centralized registry of verified rumors and unverified leaks grounded against SEBI LODR filings.
          </p>
        </div>

        <button
          onClick={fetchClaims}
          disabled={isLoading}
          className="px-3 py-1.5 rounded-portal bg-white border border-[#CBD5E1] text-[#0F2744] hover:bg-[#F1F4F9] text-xs font-mono font-medium flex items-center gap-1.5 shadow-2xs transition-colors cursor-pointer disabled:opacity-60"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Visible Error Banner if Request Fails */}
      {errorMsg && (
        <div className="p-4 rounded-portal bg-[#FDF2F2] border border-[#F8B4B4] flex items-center justify-between gap-3 text-[#C53030]">
          <div className="flex items-center gap-2 text-xs font-sans font-medium">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button
            onClick={fetchClaims}
            className="px-3 py-1 bg-white border border-[#F8B4B4] rounded text-xs font-mono font-semibold hover:bg-red-50 flex items-center gap-1 cursor-pointer shrink-0"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Retry</span>
          </button>
        </div>
      )}

      {/* Metric Strip */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="bg-white p-3.5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex items-center justify-between">
          <div>
            <div className="text-[10px] font-mono font-bold uppercase text-[#64748B]">
              Total Surveilled
            </div>
            <div className="text-xl font-mono font-bold text-[#0F2744] mt-0.5">
              {safeClaims.length}
            </div>
          </div>
          <FileText className="w-4 h-4 text-[#1B3A6B] opacity-40" />
        </div>

        <div className="bg-white p-3.5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex items-center justify-between">
          <div>
            <div className="text-[10px] font-mono font-bold uppercase text-[#0D8253]">
              Corroborated
            </div>
            <div className="text-xl font-mono font-bold text-[#0D8253] mt-0.5">
              {corroboratedCount}
            </div>
          </div>
          <CheckCircle2 className="w-4 h-4 text-[#0D8253] opacity-40" />
        </div>

        <div className="bg-white p-3.5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex items-center justify-between">
          <div>
            <div className="text-[10px] font-mono font-bold uppercase text-[#C53030]">
              Contradicted
            </div>
            <div className="text-xl font-mono font-bold text-[#C53030] mt-0.5">
              {contradictedCount}
            </div>
          </div>
          <XCircle className="w-4 h-4 text-[#C53030] opacity-40" />
        </div>

        <div className="bg-white p-3.5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex items-center justify-between">
          <div>
            <div className="text-[10px] font-mono font-bold uppercase text-[#B45309]">
              Unverified
            </div>
            <div className="text-xl font-mono font-bold text-[#B45309] mt-0.5">
              {unverifiedCount}
            </div>
          </div>
          <AlertTriangle className="w-4 h-4 text-[#B45309] opacity-40" />
        </div>
      </div>

      {/* Main Ledger Table */}
      {isLoading ? (
        <div className="bg-white p-16 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col items-center justify-center gap-3 text-xs font-mono text-[#64748B]">
          <Loader2 className="w-6 h-6 animate-spin text-[#1B3A6B]" />
          <span>Fetching surveillance ledger records from PostgreSQL...</span>
        </div>
      ) : (
        <RecentClaimsTable claims={safeClaims} isLoading={false} />
      )}
    </div>
  );
};
