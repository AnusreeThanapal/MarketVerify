export type LanguageCode = 'en' | 'ta';

export type UserRole = 'ANALYST' | 'COMPLIANCE_OFFICER' | 'ADMINISTRATOR' | 'AUDITOR';

export interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: UserProfile;
}

export type VerdictStatus =
  | 'CORROBORATED_OFFICIAL'
  | 'CONTRADICTED_BY_FILING'
  | 'UNVERIFIED_RUMOR'
  | 'LIKELY_CREDIBLE'
  | 'DEBUNKED_FALSEHOOD';

export type SentimentLabel =
  | 'STRONGLY_POSITIVE'
  | 'POSITIVE'
  | 'NEUTRAL'
  | 'NEGATIVE'
  | 'STRONGLY_NEGATIVE';

export interface CitationItem {
  doc_id: string;
  filing_type: string;
  filing_date: string;
  headline: string;
  similarity_score: number;
  snippet: string;
  source_url?: string;
}

export interface VerdictResponse {
  id: string;
  verdict_status: VerdictStatus;
  confidence_score: number;
  trust_score: number;
  trust_rationale: string;
  verification_status: string;
  citations: CitationItem[];
  sentiment: SentimentLabel;
  lead_lag_note: string;
  explanation: string;
  created_at: string;
}

export interface ClaimCreatePayload {
  raw_text: string;
  source_handle: string;
  ticker?: string;
  company_name?: string;
}

export interface ClaimResponse {
  id: string;
  raw_text: string;
  language: LanguageCode;
  normalized_text?: string;
  ticker?: string;
  company_name?: string;
  source_handle: string;
  submitted_at: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  verdict?: VerdictResponse;
  agent_run_log?: {
    id: string;
    execution_trace: TraceEntry[];
    state_snapshot: Record<string, any>;
    created_at: string;
  };
}

export interface ClaimSummary {
  id: string;
  raw_text: string;
  ticker?: string;
  source_handle: string;
  status: string;
  submitted_at: string;
  verdict_status?: VerdictStatus;
  confidence_score?: number;
}

export interface TraceEntry {
  agent_name: string;
  step_number: number;
  node_name: string;
  input_summary?: string;
  output_summary?: string;
  latency_ms: number;
  confidence_metric?: number;
  metadata?: Record<string, any>;
  timestamp: string;
}

export interface SSETraceEvent {
  event: 'trace_step' | 'completed' | 'error';
  claim_id: string;
  data: {
    step?: TraceEntry;
    verdict?: VerdictResponse;
    status?: string;
    error?: string;
  };
}

export interface SourceTrajectoryItem {
  id: string;
  past_claim_text: string;
  ticker?: string;
  was_accurate: boolean;
  lag_hours: number;
  category: string;
  outcome_summary: string;
  outcome_date: string;
}

export interface SourceTrustHistory {
  source_handle: string;
  source_name?: string;
  trust_score?: number;
  bayesian_trust_score?: number;
  confidence_level?: 'HIGH' | 'MEDIUM' | 'LOW' | string;
  total_claims_evaluated?: number;
  total_historical_claims?: number;
  accurate_claims_count?: number;
  accurate_claims?: number;
  false_claims?: number;
  accuracy_rate?: number;
  recent_trajectories?: SourceTrajectoryItem[];
  trajectories?: SourceTrajectoryItem[];
  category_breakdown?: Record<string, number>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface AdminDataListResponse<T> {
  total: number;
  skip: number;
  limit: number;
  items: T[];
}

export interface RawClaimRecord {
  id: string;
  raw_text: string;
  language: string;
  normalized_text?: string;
  ticker?: string;
  company_name?: string;
  source_handle: string;
  submitted_at: string;
  status: string;
}

export interface RawAgentRunRecord {
  id: string;
  claim_id: string;
  execution_trace: TraceEntry[];
  state_snapshot: Record<string, any>;
  created_at: string;
}

export interface RawQdrantDocRecord {
  id: string;
  collection_name: string;
  payload: Record<string, any>;
  text_snippet?: string;
}
