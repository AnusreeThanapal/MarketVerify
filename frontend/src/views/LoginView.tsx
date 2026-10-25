import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Shield,
  Lock,
  Mail,
  ArrowRight,
  AlertCircle,
  CheckCircle2,
  FileCheck2,
  Users,
  Search,
  Scale,
  KeyRound,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types/api';

interface DemoRolePreset {
  role: UserRole;
  title: string;
  desc: string;
  badgeStyle: string;
  icon: React.ComponentType<{ className?: string }>;
}

const DEMO_PRESETS: DemoRolePreset[] = [
  {
    role: 'ANALYST',
    title: 'Surveillance Analyst',
    desc: 'Submit and verify market claims, inspect live agent traces and SEBI citations.',
    badgeStyle: 'bg-blue-100 text-blue-900 border-blue-300',
    icon: Search,
  },
  {
    role: 'COMPLIANCE_OFFICER',
    title: 'Chief Compliance Officer',
    desc: 'Analyst access plus source credibility surveillance and compliance review docket.',
    badgeStyle: 'bg-emerald-100 text-emerald-900 border-emerald-300',
    icon: Scale,
  },
  {
    role: 'ADMINISTRATOR',
    title: 'Platform Administrator',
    desc: 'Full administrative access plus direct Data Explorer for raw Postgres & Qdrant stores.',
    badgeStyle: 'bg-purple-100 text-purple-900 border-purple-300',
    icon: Users,
  },
  {
    role: 'AUDITOR',
    title: 'Regulatory Auditor',
    desc: 'Strict read-only oversight: inspect verdicts, audit agent traces and raw data stores.',
    badgeStyle: 'bg-amber-100 text-amber-950 border-amber-300',
    icon: FileCheck2,
  },
];

export const LoginView: React.FC = () => {
  const { login, demoLogin, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password) {
      setErrorMsg('Please enter both email address and password.');
      return;
    }

    setErrorMsg(null);
    setIsSubmitting(true);
    try {
      await login({ email: email.trim(), password });
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Authentication failed. Please verify credentials.';
      setErrorMsg(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuickRoleLogin = async (role: UserRole) => {
    setErrorMsg(null);
    setIsSubmitting(true);
    try {
      await demoLogin(role);
    } catch (err: any) {
      const detail = err?.response?.data?.detail || 'Demo authentication failed.';
      setErrorMsg(detail);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F7F8FA] flex flex-col justify-between font-sans text-[#1E293B]">
      {/* Restrained Tricolor Hairline Accent */}
      <div className="tricolor-accent" />

      <div className="flex-1 flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <div className="w-full max-w-5xl bg-white border border-[#D8DEE8] rounded-portal shadow-portal-elevated overflow-hidden grid grid-cols-1 lg:grid-cols-12">
          
          {/* Left Panel: Light Institutional Masthead & Authority Context */}
          <div className="lg:col-span-5 bg-[#F1F4F9] border-b lg:border-b-0 lg:border-r border-[#D8DEE8] p-8 sm:p-10 flex flex-col justify-between">
            <div className="space-y-6">
              
              {/* Emblem seal and platform masthead */}
              <Link to="/" className="flex items-center gap-3.5 group cursor-pointer" title="Return to Welcome Overview">
                <div className="w-12 h-12 rounded-full border-2 border-[#D97706] bg-[#0F2744] flex items-center justify-center shadow-sm shrink-0 group-hover:scale-105 transition-transform">
                  <Shield className="w-6 h-6 text-[#D97706]" />
                </div>
                <div>
                  <span className="text-[10px] font-mono tracking-widest text-[#1B3A6B] uppercase font-bold block">
                    GOVT. / REGULATORY SURVEILLANCE
                  </span>
                  <h1 className="text-2xl font-serif font-bold tracking-tight text-[#0F2744] group-hover:text-[#1B3A6B] transition-colors">
                    MarketVerify
                  </h1>
                </div>
              </Link>

              <div className="border-t border-[#CBD5E1] pt-4 space-y-2.5">
                <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-[#1B3A6B]">
                  Official Verification Platform
                </h2>
                <p className="text-xs text-[#334155] leading-relaxed font-sans">
                  Multi-agent, retrieval-grounded verification system for listed Indian equities (BSE / NSE). Grounding social media rumors and unverified market leaks against official SEBI / BSE disclosures, source accuracy trajectories, and market lead-lag dynamics.
                </p>
              </div>

              {/* Core Features Checklist */}
              <div className="space-y-2.5 pt-2">
                <div className="flex items-start gap-2 text-xs text-[#1E293B]">
                  <CheckCircle2 className="w-4 h-4 text-[#0D8253] shrink-0 mt-0.5" />
                  <span className="font-sans leading-snug">Dual Standard ($k=3$) & Deep ($k=7$) Regulatory Filing Retrieval</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-[#1E293B]">
                  <CheckCircle2 className="w-4 h-4 text-[#0D8253] shrink-0 mt-0.5" />
                  <span className="font-sans leading-snug">Bayesian Beta Source Credibility Scoring ($\alpha=2, \beta=2$)</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-[#1E293B]">
                  <CheckCircle2 className="w-4 h-4 text-[#0D8253] shrink-0 mt-0.5" />
                  <span className="font-sans leading-snug">Multilingual English & Tamil (தமிழ்) Rumor Analysis</span>
                </div>
                <div className="flex items-start gap-2 text-xs text-[#1E293B]">
                  <CheckCircle2 className="w-4 h-4 text-[#0D8253] shrink-0 mt-0.5" />
                  <span className="font-sans leading-snug">Real-Time LangGraph SSE Agent Trace Streaming</span>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-4 border-t border-[#CBD5E1] text-[11px] text-[#64748B] font-mono flex items-center justify-between">
              <span>Secured Terminal • v1.0.0</span>
              <span className="font-bold text-[#0F2744]">SEBI LODR Reg 30</span>
            </div>
          </div>

          {/* Right Panel: High-Contrast Login Form & 1-Click Demo Roles */}
          <div className="lg:col-span-7 p-8 sm:p-10 bg-white flex flex-col justify-between">
            <div>
              {/* Form Title */}
              <div className="mb-6 pb-3 border-b border-[#E2E8F0]">
                <h2 className="text-xl font-serif font-bold text-[#0F2744]">
                  Surveillance Desk Sign In
                </h2>
                <p className="text-xs text-[#475569] mt-1 font-sans">
                  Enter your official compliance credentials or select a 1-click demo role below.
                </p>
              </div>

              {/* Error Message */}
              {errorMsg && (
                <div className="mb-5 p-3 rounded-portal bg-[#FDF2F2] border border-[#F8B4B4] flex items-start gap-2.5 text-[#C53030]">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-[#C53030]" />
                  <div className="text-xs font-sans font-medium leading-snug">{errorMsg}</div>
                </div>
              )}

              {/* Login Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-xs font-sans font-bold uppercase tracking-wider text-[#0F2744] mb-1.5">
                    Official Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#64748B]">
                      <Mail className="w-4 h-4" />
                    </div>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="e.g. analyst.demo@marketverify.app"
                      className="w-full pl-9 pr-3 py-2 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs font-mono text-[#0F2744] placeholder-[#94A3B8] focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B] transition-colors"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-sans font-bold uppercase tracking-wider text-[#0F2744] mb-1.5">
                    Security Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#64748B]">
                      <Lock className="w-4 h-4" />
                    </div>
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••••••"
                      className="w-full pl-9 pr-3 py-2 bg-[#F8FAFC] border border-[#CBD5E1] rounded-portal text-xs font-mono text-[#0F2744] placeholder-[#94A3B8] focus:bg-white focus:border-[#1B3A6B] focus:ring-1 focus:ring-[#1B3A6B] transition-colors"
                    />
                  </div>
                </div>

                <div className="flex items-center justify-between pt-0.5">
                  <label className="flex items-center gap-2 cursor-pointer text-xs text-[#475569] font-medium font-sans">
                    <input
                      type="checkbox"
                      checked={rememberMe}
                      onChange={(e) => setRememberMe(e.target.checked)}
                      className="rounded border-[#CBD5E1] text-[#1B3A6B] focus:ring-[#1B3A6B]"
                    />
                    <span>Remember surveillance station</span>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || isLoading}
                  className="w-full py-2.5 px-4 bg-[#1B3A6B] hover:bg-[#0F2744] text-white rounded-portal font-semibold text-xs font-sans tracking-wide transition-colors flex items-center justify-center gap-2 shadow-sm disabled:opacity-60 cursor-pointer"
                >
                  {isSubmitting || isLoading ? (
                    <span>Authenticating Credentials...</span>
                  ) : (
                    <>
                      <span>Sign In to Surveillance Terminal</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {/* 1-Click Demo Roles Grid (No Plaintext Passwords) */}
              <div className="mt-7 pt-5 border-t border-[#E2E8F0]">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-xs font-mono font-bold uppercase tracking-wider text-[#0F2744] flex items-center gap-1.5">
                    <KeyRound className="w-3.5 h-3.5 text-[#D97706]" />
                    <span>1-Click Demo Role Access</span>
                  </div>
                  <span className="text-[10px] font-mono text-[#64748B]">Authenticates securely via backend JWT</span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {DEMO_PRESETS.map((preset) => {
                    const Icon = preset.icon;
                    return (
                      <button
                        key={preset.role}
                        type="button"
                        onClick={() => handleQuickRoleLogin(preset.role)}
                        disabled={isSubmitting || isLoading}
                        className="text-left p-3 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1] hover:border-[#1B3A6B] hover:bg-[#EEF2F6] transition-all group flex flex-col justify-between cursor-pointer disabled:opacity-60"
                      >
                        <div className="flex items-center justify-between mb-1.5">
                          <div className="flex items-center gap-1.5 font-bold text-xs text-[#0F2744] group-hover:text-[#1B3A6B] font-sans">
                            <Icon className="w-3.5 h-3.5 text-[#1B3A6B] shrink-0" />
                            <span>{preset.title}</span>
                          </div>
                          <span className={`text-[9px] font-mono font-bold px-1.5 py-0.5 rounded border uppercase shrink-0 ${preset.badgeStyle}`}>
                            {preset.role.replace('_', ' ')}
                          </span>
                        </div>
                        <p className="text-[11px] text-[#475569] leading-snug font-sans">
                          {preset.desc}
                        </p>
                      </button>
                    );
                  })}
                </div>
              </div>

            </div>
          </div>
        </div>
      </div>

      {/* Official Portal Footer */}
      <footer className="text-center py-4 border-t border-[#D8DEE8] bg-white text-xs text-[#64748B] font-mono">
        MarketVerify • National Indian Market Rumor Grounding & Intelligence System • Official Compliance Use Only
      </footer>
    </div>
  );
};
