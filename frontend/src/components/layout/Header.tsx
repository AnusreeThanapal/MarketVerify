import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  Shield,
  FileCheck2,
  ListOrdered,
  Activity,
  History,
  Database,
  LogOut,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

interface HeaderProps {
  hasActiveClaim?: boolean;
}

export const Header: React.FC<HeaderProps> = ({ hasActiveClaim = false }) => {
  const { user, role, logout } = useAuth();
  const navigate = useNavigate();

  const isAuditor = role === 'AUDITOR';
  const isAdminOrAuditor = role === 'ADMINISTRATOR' || role === 'AUDITOR';

  const getRoleBadgeStyle = (r?: string) => {
    switch (r) {
      case 'ADMINISTRATOR':
        return 'bg-purple-100 text-purple-900 border-purple-300';
      case 'COMPLIANCE_OFFICER':
        return 'bg-emerald-100 text-emerald-900 border-emerald-300';
      case 'AUDITOR':
        return 'bg-amber-100 text-amber-950 border-amber-300';
      default:
        return 'bg-blue-100 text-blue-900 border-blue-300';
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-[#D8DEE8] shadow-portal-card sticky top-0 z-50 shrink-0 select-none">
      {/* Restrained Tricolor Hairline Accent */}
      <div className="tricolor-accent" />

      {/* Institutional Portal Masthead (Full-Bleed Width) */}
      <div className="w-full px-4 sm:px-6 py-2.5 flex items-center justify-between gap-4 border-b border-[#E8ECF2]">
        
        {/* Brand & Seal */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full border-2 border-[#D97706] bg-[#0F2744] flex items-center justify-center shadow-xs shrink-0">
            <Shield className="w-4 h-4 text-[#D97706]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-serif font-bold text-[#0F2744] tracking-tight">
                MarketVerify
              </span>
              <span className="text-[9px] font-mono font-bold uppercase px-1.5 py-0.2 rounded bg-[#F1F4F9] text-[#1B3A6B] border border-[#CBD5E1]">
                SURVEILLANCE DESK
              </span>
            </div>
            <p className="text-[11px] text-[#64748B] font-sans hidden sm:block">
              National Indian Market Rumor Grounding & Intelligence Workstation
            </p>
          </div>
        </div>

        {/* Authenticated User Profile & Actions */}
        <div className="flex items-center gap-2.5">
          {user && (
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-portal bg-[#F8FAFC] border border-[#CBD5E1] text-xs font-sans">
              <div className="w-5 h-5 rounded-full bg-[#1B3A6B] text-white flex items-center justify-center font-bold text-[10px]">
                {user.full_name.charAt(0)}
              </div>
              <div className="text-left leading-tight hidden sm:block">
                <div className="font-semibold text-[#0F2744] text-[11px]">{user.full_name}</div>
                <div className="text-[10px] text-[#64748B] font-mono">{user.email}</div>
              </div>
              <span className={`text-[9px] font-mono uppercase px-1.5 py-0.5 rounded border font-bold ml-1 ${getRoleBadgeStyle(user.role)}`}>
                {user.role.replace('_', ' ')}
              </span>
            </div>
          )}

          <button
            onClick={handleLogout}
            title="Sign Out"
            className="p-1.5 rounded-portal border border-[#CBD5E1] text-[#64748B] hover:text-[#C53030] hover:bg-[#FDF2F2] transition-colors cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Routed Institutional Navigation Tabs (Full Width) */}
      <div className="w-full px-4 sm:px-6 bg-[#FAFAFA]">
        <nav className="flex space-x-1 py-1 overflow-x-auto" aria-label="Surveillance Tabs">
          
          {/* Verify Claim Tab (Omitted for Auditor role) */}
          {!isAuditor && (
            <NavLink
              to="/verify"
              className={({ isActive }) =>
                `flex items-center gap-2 px-3.5 py-2 text-xs font-sans rounded-t-portal border-b-2 transition-all cursor-pointer ${
                  isActive
                    ? 'border-[#1B3A6B] text-[#0F2744] font-bold bg-white shadow-2xs'
                    : 'border-transparent text-[#475569] hover:text-[#0F2744] hover:bg-slate-100'
                }`
              }
            >
              <FileCheck2 className="w-3.5 h-3.5 text-[#1B3A6B]" />
              <span>Verify Claim</span>
            </NavLink>
          )}

          {/* Claims Register Ledger */}
          <NavLink
            to="/claims"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3.5 py-2 text-xs font-sans rounded-t-portal border-b-2 transition-all cursor-pointer ${
                isActive
                  ? 'border-[#1B3A6B] text-[#0F2744] font-bold bg-white shadow-2xs'
                  : 'border-transparent text-[#475569] hover:text-[#0F2744] hover:bg-slate-100'
              }`
            }
          >
            <ListOrdered className="w-3.5 h-3.5 text-[#1B3A6B]" />
            <span>Claims Register</span>
          </NavLink>

          {/* Live Multi-Agent Trace */}
          <NavLink
            to="/trace"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3.5 py-2 text-xs font-sans rounded-t-portal border-b-2 transition-all cursor-pointer ${
                isActive
                  ? 'border-[#1B3A6B] text-[#0F2744] font-bold bg-white shadow-2xs'
                  : 'border-transparent text-[#475569] hover:text-[#0F2744] hover:bg-slate-100'
              }`
            }
          >
            <Activity className="w-3.5 h-3.5 text-[#1B3A6B]" />
            <span>Multi-Agent Trace</span>
            {hasActiveClaim && (
              <span className="w-2 h-2 rounded-full bg-[#D97706] animate-ping ml-1" />
            )}
          </NavLink>

          {/* Source Credibility Docket */}
          <NavLink
            to="/sources"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3.5 py-2 text-xs font-sans rounded-t-portal border-b-2 transition-all cursor-pointer ${
                isActive
                  ? 'border-[#1B3A6B] text-[#0F2744] font-bold bg-white shadow-2xs'
                  : 'border-transparent text-[#475569] hover:text-[#0F2744] hover:bg-slate-100'
              }`
            }
          >
            <History className="w-3.5 h-3.5 text-[#1B3A6B]" />
            <span>Source Credibility Docket</span>
          </NavLink>

          {/* Backend Data Explorer (Admin & Auditor Only) */}
          {isAdminOrAuditor && (
            <NavLink
              to="/data-explorer"
              className={({ isActive }) =>
                `flex items-center gap-2 px-3.5 py-2 text-xs font-sans rounded-t-portal border-b-2 transition-all cursor-pointer ${
                  isActive
                    ? 'border-purple-700 text-purple-950 font-bold bg-white shadow-2xs'
                    : 'border-transparent text-[#475569] hover:text-[#0F2744] hover:bg-slate-100'
                }`
              }
            >
              <Database className="w-3.5 h-3.5 text-purple-700" />
              <span>Data Explorer (Raw)</span>
              <span className="text-[9px] font-mono px-1 py-0.2 rounded bg-purple-50 text-purple-800 border border-purple-200 font-bold">
                {isAuditor ? 'AUDIT' : 'ADMIN'}
              </span>
            </NavLink>
          )}
        </nav>
      </div>
    </header>
  );
};
