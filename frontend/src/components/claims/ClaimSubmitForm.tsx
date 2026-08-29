import React, { useState } from 'react';
import {
  User,
  Hash,
  ArrowRight,
  ShieldAlert,
  Zap,
  Languages,
  Sparkles,
  Loader2,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Radio,
} from 'lucide-react';
import { ClaimCreatePayload } from '../../types/api';

interface ClaimSubmitFormProps {
  onSubmit: (payload: ClaimCreatePayload) => Promise<void> | void;
  isLoading: boolean;
  error?: string | null;
}

const DEMO_PRESETS = [
  {
    title: 'Reliance Zepto 40% Stake Buyout',
    ticker: 'RELIANCE',
    source: '@dalalstreetinsider',
    text: 'Reliance Retail Ventures executes agreement to acquire 40% strategic stake in quick-commerce platform Zepto for Rs 4,200 Cr.',
    expected: 'CORROBORATED BY SEBI FILING',
    badgeColor: 'bg-emerald-50 text-[#0D8253] border-emerald-300',
  },
  {
    title: 'HDFC Bank CEO Resignation Rumor',
    ticker: 'HDFCBANK',
    source: '@dalalstreetinsider',
    text: 'HDFC Bank MD and CEO Sashidhar Jagdishan to unexpectedly resign ahead of Q2 results due to board discord.',
    expected: 'CONTRADICTED BY FILING',
    badgeColor: 'bg-red-50 text-[#C53030] border-red-300',
  },
  {
    title: 'டாடா ஸ்டீல் 1:10 பங்கு பிரிப்பு (Tamil)',
    ticker: 'TATASTEEL',
    source: '@tamil_market_guru',
    text: 'டாடா ஸ்டீல் காலாண்டு முடிவுகளில் 1:10 பங்கு பிரிப்பு (Stock Split) அறிவிக்க உள்ளதாக தகவல்.',
    expected: 'TAMIL RUMOR REFUTED',
    badgeColor: 'bg-amber-50 text-[#B45309] border-amber-300',
  },
  {
    title: 'Paytm Full Banking License Rumor',
    ticker: 'PAYTM',
    source: '@fin_leaks_raw',
    text: 'Paytm Payments Bank receives in-principle RBI nod to restore full operational banking services next month.',
    expected: 'LOW-TRUST DEEP RETRIEVAL',
    badgeColor: 'bg-amber-50 text-[#B45309] border-amber-300',
  },
];

const TOP_TICKERS = ['RELIANCE', 'HDFCBANK', 'TATASTEEL', 'INFY', 'ZOMATO'];
const MORE_TICKERS = ['PAYTM', 'ADANIENT', 'ITC', 'TCS', 'ICICIBANK', 'SBIN'];

export const ClaimSubmitForm: React.FC<ClaimSubmitFormProps> = ({
  onSubmit,
  isLoading,
  error = null,
}) => {
  const [claimText, setClaimText] = useState('');
  const [sourceHandle, setSourceHandle] = useState('@dalalstreetinsider');
  const [ticker, setTicker] = useState('RELIANCE');
  const [languageMode, setLanguageMode] = useState<'en' | 'ta'>('en');
  const [showMoreTickers, setShowMoreTickers] = useState(false);
  const [formValidationErr, setFormValidationErr] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!claimText.trim()) {
      setFormValidationErr('Please enter a rumor or claim statement to verify.');
      return;
    }

    setFormValidationErr(null);
    onSubmit({
      raw_text: claimText.trim(),
      source_handle: sourceHandle.trim().startsWith('@')
        ? sourceHandle.trim()
        : `@${sourceHandle.trim()}`,
      ticker: ticker.trim().toUpperCase() || undefined,
    });
  };

  const applyPreset = (preset: (typeof DEMO_PRESETS)[0]) => {
    setClaimText(preset.text);
    setSourceHandle(preset.source);
    setTicker(preset.ticker);
    setFormValidationErr(null);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 h-full">
      
      {/* Left Workstation Pane: Scenarios & Surveillance Intelligence */}
      <div className="lg:col-span-5 flex flex-col gap-4">
        <div className="bg-white p-5 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col justify-between flex-1">
          <div>
            <div className="flex items-center justify-between mb-3 border-b border-[#E8ECF2] pb-2.5">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-[#D97706]" />
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-[#0F2744]">
                  Surveillance Test Scenarios
                </h3>
              </div>
              <span className="text-[11px] font-mono text-[#64748B]">1-Click Load</span>
            </div>

            <div className="space-y-2.5">
              {DEMO_PRESETS.map((preset, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => applyPreset(preset)}
                  className="w-full text-left p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1] hover:border-[#1B3A6B] hover:bg-[#EEF2F6] transition-all group flex flex-col justify-between cursor-pointer"
                >
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <span className="font-bold text-xs text-[#0F2744] group-hover:text-[#1B3A6B] font-sans">
                      {preset.title}
                    </span>
                    <span className="text-[10px] font-mono font-bold px-1.5 py-0.2 rounded bg-white text-[#0F2744] border border-[#CBD5E1]">
                      ${preset.ticker}
                    </span>
                  </div>
                  <p className="text-[11px] text-[#475569] line-clamp-2 mb-2 font-sans leading-snug">
                    "{preset.text}"
                  </p>
                  <div className="flex items-center justify-between pt-1.5 border-t border-[#E2E8F0] text-[10px] font-mono">
                    <span className="text-[#64748B]">{preset.source}</span>
                    <span className={`px-1.5 py-0.2 rounded border font-bold ${preset.badgeColor}`}>
                      {preset.expected}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-[#E8ECF2] text-[11px] text-[#64748B] font-mono flex items-center justify-between">
            <span className="flex items-center gap-1">
              <Radio className="w-3 h-3 text-[#0D8253] animate-pulse" />
              <span>Multi-Source Feed</span>
            </span>
            <span className="text-[#0F2744] font-bold">SEBI LODR Reg 30</span>
          </div>
        </div>
      </div>

      {/* Right Workstation Pane: Main Submission Docket */}
      <div className="lg:col-span-7">
        <form
          onSubmit={handleSubmit}
          className="bg-white p-6 rounded-portal border border-[#D8DEE8] shadow-portal-card flex flex-col justify-between h-full space-y-5"
        >
          <div className="space-y-4">
            {/* Header & Language Mode Selector */}
            <div className="flex items-center justify-between border-b border-[#E8ECF2] pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-4 h-4 text-[#1B3A6B]" />
                <h2 className="text-sm font-serif font-bold text-[#0F2744]">
                  Market Claim Verification Docket
                </h2>
              </div>

              <div className="flex items-center gap-1 bg-[#F1F4F9] p-0.5 rounded-portal border border-[#CBD5E1] text-xs font-mono">
                <Languages className="w-3 h-3 text-[#64748B] ml-1" />
                <button
                  type="button"
                  onClick={() => setLanguageMode('en')}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors cursor-pointer ${
                    languageMode === 'en'
                      ? 'bg-white text-[#0F2744] font-bold shadow-xs'
                      : 'text-[#64748B] hover:text-[#0F2744]'
                  }`}
                >
                  English
                </button>
                <button
                  type="button"
                  onClick={() => setLanguageMode('ta')}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors cursor-pointer ${
                    languageMode === 'ta'
                      ? 'bg-white text-[#0F2744] font-bold shadow-xs'
                      : 'text-[#64748B] hover:text-[#0F2744]'
                  }`}
                >
                  தமிழ் (Tamil)
                </button>
              </div>
            </div>

            {/* Error Message */}
            {(formValidationErr || error) && (
              <div className="p-3 rounded-portal bg-[#FDF2F2] border border-[#F8B4B4] flex items-start gap-2 text-[#C53030] text-xs font-sans">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <div className="font-medium">{formValidationErr || error}</div>
              </div>
            )}

            {/* Claim Statement Input */}
            <div>
              <label className="block text-xs font-sans font-bold uppercase tracking-wider text-[#0F2744] mb-1.5">
                Market Rumor / Social Media Claim Statement
              </label>
              <textarea
                rows={4}
                required
                value={claimText}
                onChange={(e) => {
                  setClaimText(e.target.value);
                  setFormValidationErr(null);
                }}
                placeholder={
                  languageMode === 'ta'
                    ? 'எடுத்துக்காட்டு: டாடா ஸ்டீல் நிறுவனம் 1:10 பங்கு பிரிப்பு அறிவிக்க உள்ளதாக தகவல்...'
                    : 'e.g. Reliance Retail Ventures executes agreement to acquire 40% strategic stake in quick-commerce platform Zepto for Rs 4,200 Cr.'
                }
                className="w-full p-3 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs sm:text-sm text-[#1E293B] placeholder-[#94A3B8] font-sans focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B] transition-colors"
              />
              <div className="flex justify-between items-center mt-1 text-[11px] text-[#64748B] font-mono">
                <span>Supports verbatim English leaks & Tamil market commentary</span>
                <span>{claimText.length} chars</span>
              </div>
            </div>

            {/* Metadata Inputs Row (Source & Ticker) */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div>
                <label className="block text-xs font-sans font-bold uppercase tracking-wider text-[#0F2744] mb-1.5 flex items-center gap-1.5">
                  <User className="w-3.5 h-3.5 text-[#64748B]" />
                  <span>Source Handle</span>
                </label>
                <input
                  type="text"
                  required
                  value={sourceHandle}
                  onChange={(e) => setSourceHandle(e.target.value)}
                  placeholder="@dalalstreetinsider"
                  className="w-full px-3 py-2 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs font-mono text-[#0F2744] focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B]"
                />
                <span className="text-[10px] text-[#64748B] mt-1 block font-sans">
                  Bayesian prior evaluated via Trust-Tier Agent
                </span>
              </div>

              <div>
                <label className="block text-xs font-sans font-bold uppercase tracking-wider text-[#0F2744] mb-1.5 flex items-center gap-1.5">
                  <Hash className="w-3.5 h-3.5 text-[#64748B]" />
                  <span>Equity Ticker</span>
                </label>
                <input
                  type="text"
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value.toUpperCase())}
                  placeholder="RELIANCE"
                  className="w-full px-3 py-2 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs font-mono font-bold text-[#1B3A6B] focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B]"
                />
                
                {/* Ticker Chips */}
                <div className="flex items-center gap-1 mt-1.5 flex-wrap text-xs">
                  <span className="text-[10px] text-[#64748B] font-mono">Quick:</span>
                  {TOP_TICKERS.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setTicker(t)}
                      className={`text-[10px] font-mono px-1.5 py-0.2 rounded border transition-colors cursor-pointer ${
                        ticker === t
                          ? 'bg-[#1B3A6B] text-white font-bold border-[#1B3A6B]'
                          : 'bg-[#F1F4F9] text-[#0F2744] hover:bg-[#E2E8F0] border-[#CBD5E1]'
                      }`}
                    >
                      ${t}
                    </button>
                  ))}
                  <button
                    type="button"
                    onClick={() => setShowMoreTickers(!showMoreTickers)}
                    className="text-[10px] font-mono text-[#1B3A6B] hover:underline flex items-center gap-0.5 ml-0.5 cursor-pointer"
                  >
                    <span>{showMoreTickers ? 'Less' : '+ More'}</span>
                    {showMoreTickers ? <ChevronUp className="w-2.5 h-2.5" /> : <ChevronDown className="w-2.5 h-2.5" />}
                  </button>
                </div>

                {showMoreTickers && (
                  <div className="flex items-center gap-1 mt-1 flex-wrap">
                    {MORE_TICKERS.map((t) => (
                      <button
                        key={t}
                        type="button"
                        onClick={() => setTicker(t)}
                        className={`text-[10px] font-mono px-1.5 py-0.2 rounded border transition-colors cursor-pointer ${
                          ticker === t
                            ? 'bg-[#1B3A6B] text-white font-bold border-[#1B3A6B]'
                            : 'bg-[#F1F4F9] text-[#0F2744] hover:bg-[#E2E8F0] border-[#CBD5E1]'
                        }`}
                      >
                        ${t}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Primary Action Button */}
          <div className="pt-4 border-t border-[#E8ECF2] flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="text-[11px] text-[#64748B] font-sans">
              Triggers 5 LangGraph agents with dual-vector retrieval and live SSE trace streaming.
            </div>

            <button
              type="submit"
              disabled={isLoading || !claimText.trim()}
              className="w-full sm:w-auto px-6 py-2.5 bg-[#1B3A6B] hover:bg-[#0F2744] text-white rounded-portal font-semibold text-xs font-sans tracking-wide transition-all flex items-center justify-center gap-2 shadow-sm disabled:opacity-60 cursor-pointer shrink-0"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin text-[#D97706]" />
                  <span>Submitting to LangGraph...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-3.5 h-3.5 text-[#D97706]" />
                  <span>Run Verification</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </form>
      </div>

    </div>
  );
};
