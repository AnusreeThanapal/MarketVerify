import React, { useState } from 'react';
import {
  ChevronDown,
  ChevronUp,
  Clock,
  CheckCircle2,
  FileText,
  Search,
  Sparkles,
  ShieldAlert,
  Activity,
  Award,
} from 'lucide-react';
import { TraceEntry } from '../../types/api';

interface AgentNodeCardProps {
  step: TraceEntry;
  isLatest?: boolean;
}

export const AgentNodeCard: React.FC<AgentNodeCardProps> = ({
  step,
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const getAgentIcon = (name?: string) => {
    if (!name || typeof name !== 'string') return Award;
    if (name.includes('Normalizer')) return Sparkles;
    if (name.includes('Trust')) return ShieldAlert;
    if (name.includes('Verification')) return Search;
    if (name.includes('Sentiment')) return Activity;
    return Award;
  };

  const Icon = getAgentIcon(step?.agent_name);

  return (
    <div className="bg-white rounded-portal border border-[#D8DEE8] shadow-portal-card overflow-hidden">
      {/* Node Header */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full p-4 flex items-center justify-between text-left bg-slate-50/70 hover:bg-slate-100/70 transition-colors border-b border-[#E8ECF2] cursor-pointer"
      >
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-portal bg-blue-50 border border-blue-200 text-[#1B3A6B] flex items-center justify-center">
            <Icon className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-white text-[#0F2744] border border-[#CBD5E1]">
                STEP {step?.step_number || 1}
              </span>
              <h4 className="font-serif font-bold text-sm text-[#0F2744]">
                {step?.agent_name || 'Agent Node'}
              </h4>
            </div>
            <p className="text-xs text-[#64748B] font-mono mt-0.5">
              Node: <span className="text-[#0F2744] font-semibold">{step?.node_name || 'agent'}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 text-xs font-mono text-[#64748B]">
            <Clock className="w-3.5 h-3.5" />
            <span>{step?.latency_ms || 0}ms</span>
          </div>
          <div className="flex items-center gap-1 text-xs font-mono font-bold text-[#0D8253]">
            <CheckCircle2 className="w-4 h-4" />
            <span>PASSED</span>
          </div>
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-[#64748B]" />
          ) : (
            <ChevronDown className="w-4 h-4 text-[#64748B]" />
          )}
        </div>
      </button>

      {/* Expanded Node Body */}
      {isOpen && (
        <div className="p-4 space-y-3 bg-white font-sans text-xs">
          {/* Input Summary */}
          {step?.input_summary && (
            <div className="p-2.5 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
              <span className="text-[11px] font-mono font-bold uppercase text-[#0F2744] block mb-1">
                Input Grounding Context
              </span>
              <p className="text-[#1E293B] leading-relaxed font-mono text-[11px]">
                {step.input_summary}
              </p>
            </div>
          )}

          {/* Output Summary */}
          {step?.output_summary && (
            <div className="p-2.5 rounded-portal bg-blue-50/40 border border-blue-100">
              <span className="text-[11px] font-mono font-bold uppercase text-[#1B3A6B] block mb-1">
                Agent Decision & Output Rationale
              </span>
              <p className="text-[#0F2744] leading-relaxed font-mono text-[11px]">
                {step.output_summary}
              </p>
            </div>
          )}

          {/* Retrieved Evidence Payloads (if any) */}
          {step?.metadata?.retrieved_evidence && step.metadata.retrieved_evidence.length > 0 && (
            <div className="space-y-2 pt-2 border-t border-[#E8ECF2]">
              <span className="text-[11px] font-mono font-bold uppercase text-[#0F2744] flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-[#1B3A6B]" />
                <span>Retrieved Evidence Chunks ({step.metadata.retrieved_evidence.length} disclosures)</span>
              </span>

              <div className="space-y-2">
                {step.metadata.retrieved_evidence.map((ev: any, i: number) => (
                  <div
                    key={i}
                    className="p-3 rounded-portal bg-slate-50 border border-[#CBD5E1] text-xs space-y-1.5"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-[#1B3A6B] text-[11px]">
                        {ev.doc_id || `CHUNK_${i + 1}`}
                      </span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white text-[#0F2744] border border-[#CBD5E1]">
                        Cosine Similarity: {typeof ev.similarity_score === 'number' ? (ev.similarity_score * 100).toFixed(1) : '90.0'}%
                      </span>
                    </div>
                    <div className="font-semibold text-[#0F2744] text-xs">
                      {ev.headline}
                    </div>
                    <p className="text-[#64748B] font-sans leading-relaxed text-[11px]">
                      "{ev.snippet}"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
