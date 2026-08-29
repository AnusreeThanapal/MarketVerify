import React from 'react';
import { FileText, ExternalLink, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { CitationItem } from '../../types/api';

interface CitationsListProps {
  citations: CitationItem[];
}

export const CitationsList: React.FC<CitationsListProps> = ({ citations }) => {
  if (!citations || citations.length === 0) {
    return (
      <div className="p-4 rounded-portal bg-amber-50/50 border border-amber-200 text-center">
        <AlertTriangle className="w-5 h-5 text-portal-statusUnverified mx-auto mb-1.5" />
        <div className="text-xs font-mono text-portal-navy font-bold">
          No Official Exchange Filings Corroborated
        </div>
        <p className="text-xs text-portal-textMuted mt-1 font-sans">
          The Verification Agent completed both standard and expanded search passes across SEBI/BSE archives without finding matching disclosures.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 text-xs font-mono font-bold uppercase text-portal-navy">
          <FileText className="w-4 h-4 text-portal-navyLight" />
          <span>Official Regulatory Disclosures & SEBI Filings ({citations.length})</span>
        </div>
        <span className="text-[11px] text-portal-statusCorroborated font-mono font-semibold flex items-center gap-1">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>Grounded & Citations Verified</span>
        </span>
      </div>

      <div className="space-y-2.5">
        {citations.map((cite, idx) => (
          <div
            key={idx}
            className="p-3.5 rounded-portal bg-white border border-portal-border hover:border-portal-navyLight transition-all shadow-xs space-y-2"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-blue-50 text-portal-navyLight border border-blue-200">
                  {cite.doc_id}
                </span>
                <span className="text-xs font-mono text-portal-textMuted">
                  {cite.filing_type}
                </span>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono">
                <span className="text-portal-textMuted">Date: {cite.filing_date}</span>
                <span className="text-emerald-700 font-bold bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                  {(cite.similarity_score * 100).toFixed(1)}% match
                </span>
              </div>
            </div>

            <div className="font-serif font-bold text-xs text-portal-navy">
              {cite.headline}
            </div>

            <p className="text-xs text-portal-text leading-relaxed font-sans bg-slate-50 p-2.5 rounded border border-portal-borderLight">
              "{cite.snippet}"
            </p>

            {cite.source_url && (
              <div className="pt-1 flex justify-end">
                <a
                  href={cite.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[11px] font-mono text-portal-navyLight hover:underline font-semibold"
                >
                  <span>View Official Exchange Disclosure Document</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
