import React from 'react';
import {
  Sparkles,
  ShieldAlert,
  Search,
  Activity,
  Award,
  ArrowRight,
  CheckCircle2,
  Clock,
  RotateCcw,
} from 'lucide-react';
import { TraceEntry } from '../../types/api';

interface AgentDAGFlowProps {
  trace?: TraceEntry[];
  currentRunningIndex: number; // 0 to 4
  isCompleted: boolean;
  deepSearchTriggered: boolean;
  loopbackTriggered: boolean;
}

export const AgentDAGFlow: React.FC<AgentDAGFlowProps> = ({
  currentRunningIndex,
  isCompleted,
  deepSearchTriggered,
  loopbackTriggered,
}) => {
  const nodes = [
    {
      id: 'normalizer',
      name: 'Normalizer Agent',
      code: 'INGEST_01',
      desc: 'Entity extraction & language detection (EN / தமிழ்)',
      icon: Sparkles,
    },
    {
      id: 'trust_tier',
      name: 'Trust-Tier Agent',
      code: 'TRUST_02',
      desc: 'Bayesian historical confirmation rate & credibility scoring',
      icon: ShieldAlert,
    },
    {
      id: 'verification',
      name: 'Verification Agent',
      code: 'VERIFY_03',
      desc: 'Dual-pass vector retrieval across official SEBI / BSE disclosures',
      icon: Search,
    },
    {
      id: 'sentiment',
      name: 'Sentiment Agent',
      code: 'SENT_04',
      desc: 'Multilingual sentiment classification & lead-lag dynamics',
      icon: Activity,
    },
    {
      id: 'aggregator',
      name: 'Aggregator Verdict',
      code: 'VERDICT_05',
      desc: 'Evidence synthesis, citation grounding & final determination',
      icon: Award,
    },
  ];

  const getNodeState = (index: number) => {
    if (isCompleted) return 'completed';
    if (index < currentRunningIndex) return 'completed';
    if (index === currentRunningIndex) return 'running';
    return 'pending';
  };

  return (
    <div className="bg-white p-5 rounded-portal border border-portal-border shadow-portal-card space-y-4">
      {/* Top Header with Active Branches */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 border-b border-portal-borderLight gap-2">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-portal-navyLight" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-portal-navy">
              LangGraph Multi-Agent Orchestration Topology
            </h3>
          </div>
          <p className="text-xs text-portal-textMuted mt-0.5 font-sans">
            5 sequential specialized agents with conditional deep retrieval and loop-back query expansion.
          </p>
        </div>

        {/* Dynamic Branch Status Badges */}
        <div className="flex items-center gap-2 flex-wrap">
          {deepSearchTriggered && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-amber-50 text-portal-statusUnverified border border-amber-300">
              <Search className="w-3 h-3" />
              <span>DEEP RETRIEVAL (k=7) ACTIVE</span>
            </span>
          )}
          {loopbackTriggered && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-purple-50 text-purple-800 border border-purple-300">
              <RotateCcw className="w-3 h-3" />
              <span>LOOP-BACK QUERY EXPANSION</span>
            </span>
          )}
        </div>
      </div>

      {/* DAG Flow Grid */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
        {nodes.map((node, index) => {
          const state = getNodeState(index);
          const Icon = node.icon;

          return (
            <div
              key={node.id}
              className={`relative p-3 rounded-portal border transition-all flex flex-col justify-between ${
                state === 'completed'
                  ? 'bg-emerald-50/50 border-emerald-300 text-portal-navy shadow-xs'
                  : state === 'running'
                  ? 'bg-blue-50 border-portal-navyLight ring-2 ring-portal-navyLight/20 text-portal-navy'
                  : 'bg-portal-bg border-portal-border text-portal-textMuted'
              }`}
            >
              <div>
                {/* Node Header */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-white border border-portal-border">
                    {node.code}
                  </span>
                  {state === 'completed' && (
                    <CheckCircle2 className="w-4 h-4 text-portal-statusCorroborated" />
                  )}
                  {state === 'running' && (
                    <span className="w-2.5 h-2.5 rounded-full bg-portal-navyLight animate-ping" />
                  )}
                  {state === 'pending' && (
                    <Clock className="w-3.5 h-3.5 text-portal-textMuted" />
                  )}
                </div>

                <div className="flex items-center gap-1.5 mb-1">
                  <Icon className="w-4 h-4 text-portal-navyLight shrink-0" />
                  <span className="font-serif font-bold text-xs leading-tight">
                    {node.name}
                  </span>
                </div>

                <p className="text-[11px] text-portal-textMuted line-clamp-2 leading-snug font-sans">
                  {node.desc}
                </p>
              </div>

              {/* Edge arrow indicator for wide screens */}
              {index < nodes.length - 1 && (
                <div className="hidden md:block absolute -right-2 top-1/2 -translate-y-1/2 z-10">
                  <div className="w-4 h-4 rounded-full bg-white border border-portal-border flex items-center justify-center text-portal-textMuted shadow-xs">
                    <ArrowRight className="w-2.5 h-2.5" />
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
