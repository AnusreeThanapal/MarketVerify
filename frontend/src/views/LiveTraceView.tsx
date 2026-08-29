import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Activity,
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import {
  ClaimResponse,
  TraceEntry,
  VerdictResponse,
} from '../types/api';
import { getClaim, connectTraceStream } from '../api/claims';
import { AgentDAGFlow } from '../components/trace/AgentDAGFlow';
import { AgentNodeCard } from '../components/trace/AgentNodeCard';
import { VerdictPayoffCard } from '../components/trace/VerdictPayoffCard';

export const LiveTraceView: React.FC = () => {
  const { claimId } = useParams<{ claimId?: string }>();
  const navigate = useNavigate();

  const [claim, setClaim] = useState<ClaimResponse | null>(null);
  const [traceSteps, setTraceSteps] = useState<TraceEntry[]>([]);
  const [verdict, setVerdict] = useState<VerdictResponse | null>(null);
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [errorNotice, setErrorNotice] = useState<string | null>(null);

  useEffect(() => {
    if (!claimId) return;

    setErrorNotice(null);
    setIsStreaming(true);

    // Initial fetch to load claim details and any existing trace/verdict
    getClaim(claimId)
      .then((c) => {
        setClaim(c);
        if (c?.agent_run_log?.execution_trace && Array.isArray(c.agent_run_log.execution_trace)) {
          setTraceSteps(c.agent_run_log.execution_trace);
        }
        if (c?.verdict) {
          setVerdict(c.verdict);
          setIsStreaming(false);
        }
      })
      .catch((err) => {
        console.warn('Error fetching claim:', err);
        setErrorNotice('Could not load claim information from database.');
        setIsStreaming(false);
      });

    // Connect to live SSE endpoint
    const disconnectStream = connectTraceStream(
      claimId,
      (step: TraceEntry) => {
        if (!step) return;
        setTraceSteps((prev) => {
          const safePrev = Array.isArray(prev) ? prev : [];
          const exists = safePrev.some((s) => s?.step_number === step.step_number);
          if (exists) return safePrev;
          return [...safePrev, step];
        });
      },
      (finalVerdict: VerdictResponse) => {
        if (finalVerdict) {
          setVerdict(finalVerdict);
        }
        setIsStreaming(false);
      },
      (err: any) => {
        console.warn('SSE stream closed or completed:', err);
        setIsStreaming(false);
      }
    );

    return () => {
      disconnectStream();
    };
  }, [claimId]);

  if (!claimId) {
    return (
      <div className="bg-white p-12 rounded-portal border border-[#D8DEE8] shadow-portal-card text-center space-y-4">
        <Activity className="w-10 h-10 text-[#1B3A6B] mx-auto opacity-70" />
        <h3 className="text-base font-serif font-bold text-[#0F2744]">
          No Active Surveillance Docket Selected
        </h3>
        <p className="text-xs text-[#64748B] max-w-md mx-auto font-sans">
          Select a claim from the Claims Register or submit a new market rumor to view its live multi-agent execution trace.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <button
            onClick={() => navigate('/verify')}
            className="px-4 py-2 bg-[#1B3A6B] text-white text-xs font-semibold rounded-portal hover:bg-[#0F2744] transition-colors cursor-pointer"
          >
            Verify a Claim
          </button>
          <button
            onClick={() => navigate('/claims')}
            className="px-4 py-2 bg-[#F1F4F9] text-[#0F2744] text-xs font-semibold rounded-portal hover:bg-[#E2E8F0] border border-[#CBD5E1] transition-colors cursor-pointer"
          >
            Open Claims Register
          </button>
        </div>
      </div>
    );
  }

  const safeSteps = Array.isArray(traceSteps) ? traceSteps : [];
  const currentRunningIndex = safeSteps.length;
  const isCompleted = !isStreaming && verdict !== null;

  // Check for dynamic branch triggers safely
  const deepSearchTriggered = safeSteps.some(
    (s) =>
      s?.metadata?.deep_retrieval_active === true ||
      (typeof s?.output_summary === 'string' && s.output_summary.includes('DEEP'))
  );

  const loopbackTriggered = safeSteps.some(
    (s) =>
      s?.metadata?.loopback_triggered === true ||
      (typeof s?.output_summary === 'string' && s.output_summary.includes('Loop-back'))
  );

  return (
    <div className="space-y-5">
      {/* Top Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-white p-3.5 rounded-portal border border-[#D8DEE8] shadow-portal-card">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/verify')}
            className="p-1.5 rounded-portal border border-[#CBD5E1] hover:bg-[#F1F4F9] text-[#0F2744] transition-colors flex items-center gap-1.5 text-xs font-mono font-medium cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>New Verification</span>
          </button>

          <div className="border-l border-[#CBD5E1] pl-3">
            <span className="text-[10px] font-mono font-bold uppercase text-[#64748B] block">
              Surveillance Docket ID
            </span>
            <span className="text-xs font-mono font-bold text-[#0F2744]">
              {claimId}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {isStreaming ? (
            <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-blue-50 border border-blue-200 text-[#1B3A6B] text-[11px] font-mono font-bold">
              <span className="w-2 h-2 rounded-full bg-[#1B3A6B] animate-ping" />
              <span>LIVE SSE AGENT TRACE STREAMING...</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-emerald-50 border border-emerald-300 text-[#0D8253] text-[11px] font-mono font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>TRACE REPLAY COMPLETE</span>
            </div>
          )}
        </div>
      </div>

      {errorNotice && (
        <div className="p-3 rounded-portal bg-[#FDF2F2] border border-[#F8B4B4] flex items-center gap-2 text-[#C53030] text-xs">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{errorNotice}</span>
        </div>
      )}

      {/* Claim Summary Card */}
      {claim && (
        <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card space-y-1.5 font-sans text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-mono font-bold px-2 py-0.2 rounded bg-[#F1F4F9] text-[#1B3A6B] border border-[#CBD5E1]">
                ${claim.ticker || 'GENERAL'}
              </span>
              <span className="font-mono text-[#64748B] text-[11px]">
                Source: <strong className="text-[#0F2744]">{claim.source_handle}</strong>
              </span>
            </div>
            <span className="text-[10px] font-mono text-[#64748B]">
              Language: {claim.language?.toUpperCase() || 'EN'} • Submitted: {claim.submitted_at ? new Date(claim.submitted_at).toLocaleTimeString() : 'Recent'}
            </span>
          </div>
          <p className="text-sm font-serif font-bold text-[#0F2744] leading-relaxed">
            "{claim.raw_text}"
          </p>
        </div>
      )}

      {/* 5-Node DAG Flow Visualization */}
      <AgentDAGFlow
        trace={safeSteps}
        currentRunningIndex={currentRunningIndex}
        isCompleted={isCompleted}
        deepSearchTriggered={deepSearchTriggered}
        loopbackTriggered={loopbackTriggered}
      />

      {/* Verdict Payoff Card (Hero Payoff when completed) */}
      {verdict && (
        <div className="pt-1">
          <VerdictPayoffCard
            verdict={verdict}
            ticker={claim?.ticker}
            sourceHandle={claim?.source_handle || '@unknown'}
          />
        </div>
      )}

      {/* Step-by-Step Agent Trace Logs */}
      <div className="space-y-2.5 pt-1">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#0F2744] flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-[#1B3A6B]" />
            <span>Agent Execution Log & Intermediate Retrieval State ({safeSteps.length}/5)</span>
          </h3>
          <span className="text-[10px] text-[#64748B] font-mono">
            Structured LangGraph Trace
          </span>
        </div>

        <div className="space-y-2.5">
          {safeSteps.map((step) => (
            <AgentNodeCard key={step.step_number} step={step} />
          ))}
        </div>
      </div>
    </div>
  );
};
