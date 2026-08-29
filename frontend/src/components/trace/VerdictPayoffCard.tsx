import React from 'react';
import {
  ShieldCheck,
  XCircle,
  AlertTriangle,
  Sparkles,
  TrendingUp,
  TrendingDown,
  Minus,
  FileCheck2,
} from 'lucide-react';
import { VerdictResponse, VerdictStatus } from '../../types/api';
import { TrustScoreGauge } from './TrustScoreGauge';
import { CitationsList } from './CitationsList';

interface VerdictPayoffCardProps {
  verdict: VerdictResponse;
  ticker?: string;
  sourceHandle: string;
}

export const VerdictPayoffCard: React.FC<VerdictPayoffCardProps> = ({
  verdict,
  ticker,
  sourceHandle,
}) => {
  const getVerdictPresentation = (status?: VerdictStatus) => {
    switch (status) {
      case 'CORROBORATED_OFFICIAL':
        return {
          title: 'CORROBORATED BY OFFICIAL FILING',
          subtitle: 'VERIFIED REGULATORY FACT',
          color: 'bg-emerald-50 text-[#0D8253] border-emerald-300',
          badgeBg: 'bg-[#0D8253] text-white',
          icon: ShieldCheck,
          accentBorder: 'border-l-4 border-l-[#0D8253]',
        };
      case 'CONTRADICTED_BY_FILING':
        return {
          title: 'CONTRADICTED BY OFFICIAL FILING / CLARIFICATION',
          subtitle: 'REFUTED SPECULATIVE RUMOR',
          color: 'bg-red-50 text-[#C53030] border-red-300',
          badgeBg: 'bg-[#C53030] text-white',
          icon: XCircle,
          accentBorder: 'border-l-4 border-l-[#C53030]',
        };
      case 'UNVERIFIED_RUMOR':
        return {
          title: 'UNVERIFIED SOCIAL MEDIA RUMOR',
          subtitle: 'NO SUPPORTING DISCLOSURE LOCATED',
          color: 'bg-amber-50 text-[#B45309] border-amber-300',
          badgeBg: 'bg-[#B45309] text-white',
          icon: AlertTriangle,
          accentBorder: 'border-l-4 border-l-[#B45309]',
        };
      case 'LIKELY_CREDIBLE':
        return {
          title: 'LIKELY CREDIBLE INTELLIGENCE',
          subtitle: 'HIGH TRUST SOURCE TRACK RECORD',
          color: 'bg-blue-50 text-[#1B3A6B] border-blue-300',
          badgeBg: 'bg-[#1B3A6B] text-white',
          icon: Sparkles,
          accentBorder: 'border-l-4 border-l-[#1B3A6B]',
        };
      default:
        return {
          title: 'INCONCLUSIVE EVIDENCE / NO OFFICIAL FILING',
          subtitle: 'NO CORROBORATING FILINGS FOUND',
          color: 'bg-slate-50 text-[#64748B] border-[#CBD5E1]',
          badgeBg: 'bg-[#64748B] text-white',
          icon: AlertTriangle,
          accentBorder: 'border-l-4 border-l-[#64748B]',
        };
    }
  };

  const getSentimentIcon = (sentiment?: string) => {
    if (!sentiment) return Minus;
    if (sentiment.includes('POSITIVE')) return TrendingUp;
    if (sentiment.includes('NEGATIVE')) return TrendingDown;
    return Minus;
  };

  const p = getVerdictPresentation(verdict?.verdict_status);
  const StatusIcon = p.icon;
  const SentimentIcon = getSentimentIcon(verdict?.sentiment);
  const confidencePercent = typeof verdict?.confidence_score === 'number'
    ? (verdict.confidence_score * 100).toFixed(1)
    : '0.0';

  return (
    <div className={`bg-white rounded-portal border border-[#D8DEE8] shadow-portal-elevated overflow-hidden ${p.accentBorder}`}>
      {/* Hero Header */}
      <div className={`p-5 ${p.color} border-b flex flex-col md:flex-row md:items-center justify-between gap-4`}>
        <div className="flex items-center gap-3.5">
          <div className={`w-11 h-11 rounded-portal ${p.badgeBg} flex items-center justify-center shadow-xs shrink-0`}>
            <StatusIcon className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-white text-[#0F2744] border border-[#CBD5E1]">
                FINAL SURVEILLANCE DETERMINATION
              </span>
              <span className="text-xs font-mono font-semibold">
                Confidence: {confidencePercent}%
              </span>
            </div>
            <h3 className="text-lg font-serif font-bold tracking-tight mt-0.5">
              {p.title}
            </h3>
          </div>
        </div>

        {/* Ticker & Source Docket Badges */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-portal bg-white border border-[#CBD5E1] text-[#0F2744]">
            <span className="text-[#64748B] text-[10px] block uppercase">Equity</span>
            <span className="font-bold text-[#1B3A6B]">${ticker || 'GENERAL'}</span>
          </div>
          <div className="px-3 py-1.5 rounded-portal bg-white border border-[#CBD5E1] text-[#0F2744]">
            <span className="text-[#64748B] text-[10px] block uppercase">Source</span>
            <span className="font-medium text-[#1E293B]">{sourceHandle}</span>
          </div>
        </div>
      </div>

      {/* Main Analysis Body */}
      <div className="p-6 space-y-6">
        {/* Synthesis Explanation Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left 2 Cols: Aggregator Rationale & Sentiment */}
          <div className="lg:col-span-2 space-y-4">
            <div className="p-4 rounded-portal bg-[#F8FAFC] border border-[#D8DEE8]">
              <div className="flex items-center gap-2 mb-2">
                <FileCheck2 className="w-4 h-4 text-[#1B3A6B]" />
                <h4 className="text-xs font-mono font-bold uppercase text-[#0F2744]">
                  Evidence Synthesis & Grounded Determination
                </h4>
              </div>
              <p className="text-xs text-[#1E293B] leading-relaxed font-sans">
                {verdict?.explanation || 'No summary explanation recorded for this verdict.'}
              </p>
            </div>

            {/* Sentiment & Lead-Lag Dynamic Note */}
            <div className="p-4 rounded-portal bg-slate-50 border border-[#D8DEE8] space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <SentimentIcon className="w-4 h-4 text-[#1B3A6B]" />
                  <span className="text-xs font-mono font-bold uppercase text-[#0F2744]">
                    Market Sentiment & Price Lead-Lag Signal
                  </span>
                </div>
                <span className="text-[11px] font-mono font-bold uppercase px-2 py-0.5 rounded bg-white text-[#0F2744] border border-[#CBD5E1]">
                  {verdict?.sentiment ? verdict.sentiment.replace('_', ' ') : 'NEUTRAL'}
                </span>
              </div>
              <p className="text-xs text-[#64748B] font-sans leading-relaxed">
                {verdict?.lead_lag_note || 'Standard lead-lag parameters applied.'}
              </p>
            </div>
          </div>

          {/* Right Col: Trust Gauge */}
          <div className="flex flex-col justify-between space-y-3">
            <TrustScoreGauge score={typeof verdict?.trust_score === 'number' ? verdict.trust_score : 0.5} />
            <div className="p-3 rounded-portal bg-[#F8FAFC] border border-[#D8DEE8] text-[11px] text-[#64748B] font-sans leading-snug">
              <span className="font-mono font-bold text-[#0F2744] block mb-0.5">Trust Rationale</span>
              {verdict?.trust_rationale || 'Source Bayesian prior evaluated from historical accuracy.'}
            </div>
          </div>
        </div>

        {/* Regulatory Citations Drawer */}
        <div className="pt-4 border-t border-[#E8ECF2]">
          <CitationsList citations={Array.isArray(verdict?.citations) ? verdict.citations : []} />
        </div>
      </div>
    </div>
  );
};
