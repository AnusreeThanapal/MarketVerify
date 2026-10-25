import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Shield,
  ArrowRight,
  Sparkles,
  Search,
  Activity,
  Award,
  CheckCircle2,
  FileCheck2,
  Lock,
  Layers,
  Database,
  HelpCircle,
  TrendingUp,
} from 'lucide-react';

export const WelcomeView: React.FC = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);

  // Animated looping step simulation for the hero mock
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 5);
    }, 2400);
    return () => clearInterval(interval);
  }, []);

  const scrollToHowItWorks = () => {
    const el = document.getElementById('how-it-works');
    if (el) {
      el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const steps = [
    {
      agent: 'Ingestion & Normalizer',
      code: 'INGEST_01',
      desc: 'Extracted $RELIANCE ticker, normalized verbatim English leak text.',
      icon: Sparkles,
      color: 'text-sky-600 bg-sky-50 border-sky-200',
    },
    {
      agent: 'Trust-Tier Credibility',
      code: 'TRUST_02',
      desc: 'Source @dalalstreetinsider evaluated: 3/4 past claims verified. Calibrated prior: 0.80.',
      icon: Shield,
      color: 'text-amber-600 bg-amber-50 border-amber-200',
    },
    {
      agent: 'Regulatory Verification',
      code: 'VERIFY_03',
      desc: 'Vector match found in SEBI Reg 30 archive: 94.2% cosine similarity.',
      icon: Search,
      color: 'text-emerald-600 bg-emerald-50 border-emerald-200',
    },
    {
      agent: 'Sentiment & Lead-Lag',
      code: 'SENT_04',
      desc: 'Positive M&A tone detected; 2-4% pre-announcement momentum lead flag.',
      icon: Activity,
      color: 'text-purple-600 bg-purple-50 border-purple-200',
    },
    {
      agent: 'Aggregator Determination',
      code: 'VERDICT_05',
      desc: 'CORROBORATED BY OFFICIAL FILING issued with SEBI-REL-2024-001 citation.',
      icon: Award,
      color: 'text-emerald-700 bg-emerald-100 border-emerald-300',
    },
  ];

  return (
    <div className="min-h-screen bg-[#F7F8FA] text-[#1E293B] flex flex-col font-sans selection:bg-[#1B3A6B] selection:text-white">
      {/* Restrained Tricolor Hairline Accent */}
      <div className="tricolor-accent" />

      {/* Institutional Top Navigation Masthead */}
      <header className="bg-white border-b border-[#D8DEE8] sticky top-0 z-50 shadow-2xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full border-2 border-[#D97706] bg-[#0F2744] flex items-center justify-center shadow-xs shrink-0">
              <Shield className="w-4 h-4 text-[#D97706]" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-lg font-serif font-bold text-[#0F2744] tracking-tight">
                  MarketVerify
                </span>
                <span className="text-[9px] font-mono font-bold uppercase px-1.5 py-0.2 rounded bg-[#F1F4F9] text-[#1B3A6B] border border-[#CBD5E1]">
                  SURVEILLANCE DESK
                </span>
              </div>
              <span className="text-[10px] text-[#64748B] font-mono hidden sm:inline">
                National Indian Market Rumor Grounding Platform
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={scrollToHowItWorks}
              className="text-xs font-mono font-medium text-[#475569] hover:text-[#0F2744] px-3 py-1.5 rounded transition-colors hidden sm:inline cursor-pointer"
            >
              How It Works
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-4 py-2 bg-[#1B3A6B] hover:bg-[#0F2744] text-white rounded-portal font-semibold text-xs font-sans tracking-wide transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
            >
              <span>Sign In / Demo Access</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </header>

      {/* 1. HERO SECTION */}
      <section className="relative overflow-hidden pt-12 pb-16 lg:pt-16 lg:pb-24 border-b border-[#E8ECF2] bg-gradient-to-b from-white to-[#F7F8FA]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            
            {/* Hero Text & Value Proposition */}
            <div className="lg:col-span-6 space-y-6">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#F1F4F9] border border-[#CBD5E1] text-[11px] font-mono text-[#1B3A6B]">
                <span className="w-2 h-2 rounded-full bg-[#0D8253] animate-pulse" />
                <span className="font-bold">SEBI LODR REG 30 GROUNDED</span>
              </div>

              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold text-[#0F2744] tracking-tight leading-[1.15]">
                Every market rumor, checked against the filing.
              </h1>

              <p className="text-sm sm:text-base text-[#475569] font-sans leading-relaxed">
                MarketVerify coordinates 5 specialized LangGraph agents to verify unverified Indian equities rumors (BSE / NSE) against authentic regulatory disclosures and source credibility histories before anyone trades on noise.
              </p>

              <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
                <button
                  onClick={() => navigate('/login')}
                  className="px-6 py-3.5 bg-[#1B3A6B] hover:bg-[#0F2744] text-white rounded-portal font-semibold text-sm font-sans tracking-wide transition-all shadow-sm flex items-center justify-center gap-2 cursor-pointer group"
                >
                  <span>Get Started & Demo Roles</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </button>
                <button
                  onClick={scrollToHowItWorks}
                  className="px-5 py-3.5 bg-white hover:bg-[#F1F4F9] border border-[#CBD5E1] text-[#0F2744] rounded-portal font-semibold text-sm font-sans transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-2xs"
                >
                  <HelpCircle className="w-4 h-4 text-[#64748B]" />
                  <span>How the Multi-Agent System Works</span>
                </button>
              </div>

              {/* Multilingual Highlight */}
              <div className="pt-3 flex items-center gap-3 text-xs text-[#64748B] font-mono border-t border-[#E8ECF2]">
                <span className="font-bold text-[#0F2744]">Supported Languages:</span>
                <span className="px-2 py-0.5 rounded bg-white border border-[#CBD5E1] text-[#1B3A6B] font-semibold">English</span>
                <span className="px-2 py-0.5 rounded bg-white border border-[#CBD5E1] text-[#1B3A6B] font-semibold">தமிழ் (Tamil)</span>
              </div>
            </div>

            {/* Hero Live Visual Anchor: Animated Multi-Agent Trace Simulator */}
            <div className="lg:col-span-6">
              <div className="bg-white rounded-portal border border-[#CBD5E1] shadow-portal-elevated overflow-hidden">
                {/* Visual Window Header */}
                <div className="p-3.5 bg-[#F1F4F9] border-b border-[#D8DEE8] flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-2">
                    <div className="flex gap-1.5">
                      <span className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                      <span className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                      <span className="w-2.5 h-2.5 rounded-full bg-slate-300" />
                    </div>
                    <span className="font-bold text-[#0F2744] ml-1">Live Multi-Agent Trace Stream</span>
                  </div>
                  <span className="text-[10px] text-[#0D8253] font-bold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                    SSE ACTIVE
                  </span>
                </div>

                {/* Simulated Rumor Card */}
                <div className="p-4 bg-slate-50 border-b border-[#E8ECF2] font-sans text-xs space-y-1">
                  <div className="flex items-center justify-between text-[11px] font-mono text-[#64748B]">
                    <span>Source: <strong className="text-[#0F2744]">@dalalstreetinsider</strong></span>
                    <span className="font-bold text-[#1B3A6B]">$RELIANCE</span>
                  </div>
                  <p className="font-serif font-bold text-xs text-[#0F2744] leading-snug">
                    "Reliance Retail Ventures executes agreement to acquire 40% strategic stake in Zepto for Rs 4,200 Cr."
                  </p>
                </div>

                {/* Animated 5-Agent Step Progress */}
                <div className="p-4 space-y-2.5">
                  {steps.map((s, idx) => {
                    const Icon = s.icon;
                    const isCurrent = activeStep === idx;
                    const isPassed = activeStep > idx;

                    return (
                      <div
                        key={s.code}
                        className={`p-2.5 rounded-portal border transition-all flex items-start gap-3 ${
                          isCurrent
                            ? 'bg-blue-50/70 border-[#1B3A6B] ring-1 ring-[#1B3A6B]/20 shadow-xs'
                            : isPassed
                            ? 'bg-emerald-50/40 border-emerald-200 opacity-90'
                            : 'bg-[#F8FAFC] border-slate-200 opacity-50'
                        }`}
                      >
                        <div className={`p-1.5 rounded shrink-0 border ${s.color}`}>
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-[#0F2744] font-serif">
                              {s.agent}
                            </span>
                            <span className="text-[9px] font-mono font-bold uppercase text-[#64748B]">
                              {isCurrent ? 'RUNNING...' : isPassed ? 'COMPLETE' : 'PENDING'}
                            </span>
                          </div>
                          <p className="text-[11px] text-[#475569] font-mono truncate mt-0.5">
                            {s.desc}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Final Determination Payoff Banner */}
                <div className="p-3.5 bg-emerald-50 border-t border-emerald-200 flex items-center justify-between text-xs font-mono">
                  <div className="flex items-center gap-1.5 text-[#0D8253] font-bold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>CORROBORATED BY OFFICIAL DISCLOSURE</span>
                  </div>
                  <span className="text-[10px] text-[#0D8253] font-bold bg-white px-2 py-0.5 rounded border border-emerald-300">
                    Confidence: 92.0%
                  </span>
                </div>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* 2. TRUST STRIP */}
      <section className="bg-white py-6 border-b border-[#E8ECF2]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
              <FileCheck2 className="w-5 h-5 text-[#1B3A6B] mx-auto mb-1" />
              <div className="text-xs font-mono font-bold text-[#0F2744]">SEBI & BSE Grounded</div>
              <div className="text-[10px] text-[#64748B] font-sans">LODR Regulation 30 verified</div>
            </div>

            <div className="p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
              <Layers className="w-5 h-5 text-[#0D8253] mx-auto mb-1" />
              <div className="text-xs font-mono font-bold text-[#0F2744]">5-Agent LangGraph</div>
              <div className="text-[10px] text-[#64748B] font-sans">Sequential DAG orchestration</div>
            </div>

            <div className="p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
              <Database className="w-5 h-5 text-purple-700 mx-auto mb-1" />
              <div className="text-xs font-mono font-bold text-[#0F2744]">3 Qdrant Collections</div>
              <div className="text-[10px] text-[#64748B] font-sans">Isolated dual-pass vector stores</div>
            </div>

            <div className="p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1]">
              <Lock className="w-5 h-5 text-[#D97706] mx-auto mb-1" />
              <div className="text-xs font-mono font-bold text-[#0F2744]">4 Surveillance Roles</div>
              <div className="text-[10px] text-[#64748B] font-sans">Analyst, Compliance, Admin, Auditor</div>
            </div>
          </div>
        </div>
      </section>

      {/* 3. HOW IT WORKS SECTION */}
      <section id="how-it-works" className="py-16 bg-[#F7F8FA] border-b border-[#E8ECF2]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <span className="text-xs font-mono font-bold uppercase tracking-widest text-[#1B3A6B]">
              Surveillance Methodology
            </span>
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-[#0F2744]">
              How MarketVerify Grounding Works
            </h2>
            <p className="text-xs sm:text-sm text-[#475569] font-sans">
              Unlike generic LLM wrappers that guess from hallucinated training memory, MarketVerify executes a structured 4-phase retrieval and verification loop.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
            {/* Step 1 */}
            <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="w-8 h-8 rounded-full bg-[#1B3A6B] text-white flex items-center justify-center font-mono font-bold text-xs">
                  01
                </div>
                <h3 className="font-serif font-bold text-sm text-[#0F2744]">
                  Claim Ingestion & Normalization
                </h3>
                <p className="text-xs text-[#475569] leading-relaxed font-sans">
                  The Normalizer Agent parses the verbatim statement in English or Tamil, extracts the NSE/BSE ticker, and establishes grounding parameters.
                </p>
              </div>
              <div className="text-[10px] font-mono text-[#64748B] pt-2 border-t border-[#E8ECF2]">
                Node: <span className="font-bold text-[#0F2744]">INGEST_01</span>
              </div>
            </div>

            {/* Step 2 */}
            <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="w-8 h-8 rounded-full bg-[#D97706] text-white flex items-center justify-center font-mono font-bold text-xs">
                  02
                </div>
                <h3 className="font-serif font-bold text-sm text-[#0F2744]">
                  Source Credibility Evaluation
                </h3>
                <p className="text-xs text-[#475569] leading-relaxed font-sans">
                  The Trust-Tier Agent calculates a Bayesian Beta prior ($\alpha=2, \beta=2$) from historical leak accuracy to adjust retrieval depth.
                </p>
              </div>
              <div className="text-[10px] font-mono text-[#64748B] pt-2 border-t border-[#E8ECF2]">
                Node: <span className="font-bold text-[#0F2744]">TRUST_02</span>
              </div>
            </div>

            {/* Step 3 */}
            <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="w-8 h-8 rounded-full bg-[#137547] text-white flex items-center justify-center font-mono font-bold text-xs">
                  03
                </div>
                <h3 className="font-serif font-bold text-sm text-[#0F2744]">
                  Dual-Vector Regulatory Search
                </h3>
                <p className="text-xs text-[#475569] leading-relaxed font-sans">
                  The Verification Agent queries official SEBI disclosures via standard ($k=3$) or deep ($k=7$) retrieval with automatic loop-back retry.
                </p>
              </div>
              <div className="text-[10px] font-mono text-[#64748B] pt-2 border-t border-[#E8ECF2]">
                Node: <span className="font-bold text-[#0F2744]">VERIFY_03</span>
              </div>
            </div>

            {/* Step 4 */}
            <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col justify-between space-y-4">
              <div className="space-y-3">
                <div className="w-8 h-8 rounded-full bg-purple-700 text-white flex items-center justify-center font-mono font-bold text-xs">
                  04
                </div>
                <h3 className="font-serif font-bold text-sm text-[#0F2744]">
                  Grounded Verdict & Citations
                </h3>
                <p className="text-xs text-[#475569] leading-relaxed font-sans">
                  The Aggregator Agent issues the final determination with official exchange filing URLs, confidence score, and lead-lag analysis.
                </p>
              </div>
              <div className="text-[10px] font-mono text-[#64748B] pt-2 border-t border-[#E8ECF2]">
                Node: <span className="font-bold text-[#0F2744]">VERDICT_05</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. WHY THIS MATTERS SECTION */}
      <section className="py-14 bg-white border-b border-[#E8ECF2]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-4">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-[#F1F4F9] text-[#1B3A6B] text-[11px] font-mono font-bold uppercase">
            <TrendingUp className="w-3.5 h-3.5 text-[#D97706]" />
            <span>Market Integrity & Investor Protection</span>
          </div>

          <blockquote className="text-xl sm:text-2xl font-serif font-bold text-[#0F2744] leading-snug">
            "Unverified rumors move Indian retail equities 3–5% hours before official exchange clarifications surface. Most market tools measure sentiment — MarketVerify establishes truth."
          </blockquote>

          <p className="text-xs text-[#64748B] font-sans">
            Designed for institutional compliance officers, regulatory surveillance desks, and market intelligence researchers.
          </p>
        </div>
      </section>

      {/* 5. FOOTER CALL-TO-ACTION */}
      <section className="py-14 bg-[#F1F4F9] border-b border-[#D8DEE8]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-5">
          <h2 className="text-2xl font-serif font-bold text-[#0F2744]">
            Ready to inspect the surveillance terminal?
          </h2>
          <p className="text-xs text-[#475569] font-sans max-w-md mx-auto">
            Experience the 1-click demo access for Surveillance Analysts, Compliance Officers, Platform Administrators, and Regulatory Auditors.
          </p>
          <div>
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-3.5 bg-[#1B3A6B] hover:bg-[#0F2744] text-white rounded-portal font-semibold text-sm font-sans tracking-wide transition-all shadow-sm inline-flex items-center gap-2 cursor-pointer"
            >
              <span>Access Surveillance Desk</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
};
