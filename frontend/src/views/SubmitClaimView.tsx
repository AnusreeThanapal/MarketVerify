import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ClaimSubmitForm } from '../components/claims/ClaimSubmitForm';
import { ClaimCreatePayload } from '../types/api';
import { startStreamingClaim, submitClaimSync } from '../api/claims';

export const SubmitClaimView: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const handleSubmit = async (payload: ClaimCreatePayload) => {
    setIsLoading(true);
    setErrorMsg(null);
    try {
      // 1. Try streaming endpoint first
      const res = await startStreamingClaim(payload);
      if (res && res.claim_id) {
        navigate(`/trace/${res.claim_id}`);
        return;
      }
    } catch (streamErr: any) {
      console.warn('Streaming start failed, attempting sync fallback:', streamErr);
      try {
        const syncRes = await submitClaimSync(payload);
        if (syncRes && syncRes.id) {
          navigate(`/trace/${syncRes.id}`);
          return;
        }
      } catch (syncErr: any) {
        const detail =
          syncErr?.response?.data?.detail ||
          syncErr?.message ||
          'Failed to execute multi-agent verification. Please ensure backend is running.';
        setErrorMsg(detail);
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb Notice */}
      <div className="p-4 rounded-portal bg-[#F1F4F9] border border-[#CBD5E1] text-xs font-sans text-[#0F2744] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <span className="font-mono font-bold uppercase mr-1.5 text-[#1B3A6B]">Surveillance Protocol:</span>
          All submitted claims are normalized, evaluated against source credibility priors, and verified across official SEBI/BSE disclosures using LangGraph.
        </div>
        <span className="text-[11px] font-mono text-[#64748B] shrink-0">
          Regulatory Standard: SEBI LODR Reg 30
        </span>
      </div>

      <ClaimSubmitForm onSubmit={handleSubmit} isLoading={isLoading} error={errorMsg} />
    </div>
  );
};
