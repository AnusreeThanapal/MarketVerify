import React, { useState, useEffect } from 'react';
import { Shield, Database, Cpu, Clock } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const StatusBar: React.FC = () => {
  const { role } = useAuth();
  const [istTime, setIstTime] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const timeStr = now.toLocaleTimeString('en-IN', {
        timeZone: 'Asia/Kolkata',
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
      setIstTime(timeStr);
    };
    updateTime();
    const interval = setInterval(updateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <footer className="h-7 bg-[#0F2744] text-[#94A3B8] border-t border-[#1B3A6B] px-4 flex items-center justify-between text-[11px] font-mono select-none shrink-0 z-40">
      {/* Left: System Status & Protocol */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-white font-bold">
          <span className="w-2 h-2 rounded-full bg-[#0D8253] animate-pulse" />
          <span className="text-[#E2E8F0] tracking-wider uppercase">SURVEILLANCE DESK ACTIVE</span>
        </div>
        <span className="text-[#334155]">|</span>
        <div className="hidden sm:flex items-center gap-1 text-[#CBD5E1]">
          <Shield className="w-3 h-3 text-[#D97706]" />
          <span>SEBI LODR Reg 30 Grounded</span>
        </div>
        <span className="text-[#334155] hidden sm:inline">|</span>
        <div className="hidden md:flex items-center gap-1 text-[#CBD5E1]">
          <Cpu className="w-3 h-3 text-[#38BDF8]" />
          <span>LangGraph: 5 Agents Online</span>
        </div>
      </div>

      {/* Right: Storage & IST Clock */}
      <div className="flex items-center gap-4">
        <div className="hidden lg:flex items-center gap-1 text-[#CBD5E1]">
          <Database className="w-3 h-3 text-[#A855F7]" />
          <span>PostgreSQL + 3 Qdrant Stores</span>
        </div>
        <span className="text-[#334155] hidden lg:inline">|</span>
        <div className="flex items-center gap-1.5 text-[#F8FAFC] font-semibold">
          <Clock className="w-3 h-3 text-[#D97706]" />
          <span>{istTime} IST</span>
        </div>
        <span className="text-[#334155]">|</span>
        <span className="text-[10px] uppercase font-bold text-[#38BDF8]">
          {role?.replace('_', ' ') || 'GUEST'}
        </span>
      </div>
    </footer>
  );
};
