from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class AgentState(TypedDict):
    # Input identifiers
    claim_id: str
    raw_text: str
    source_handle: str
    
    # 1. Ingestion / Normalizer Agent outputs
    language: str
    normalized_text: str
    ticker: Optional[str]
    company_name: Optional[str]
    extracted_entities: List[str]
    
    # 2. Trust-Tier Agent outputs
    trust_score: float
    trust_confidence: str
    trust_rationale: str
    trust_docs: List[Dict[str, Any]]
    
    # Orchestration control flags
    deep_retrieval_flag: bool
    verification_pass_count: int
    loop_back_triggered: bool
    
    # 3. Verification Agent outputs
    verification_status: str  # CORROBORATED / CONTRADICTED / NO_EVIDENCE_FOUND
    verification_confidence: float
    verification_citations: List[Dict[str, Any]]
    verification_docs: List[Dict[str, Any]]
    
    # 4. Sentiment Agent outputs
    sentiment_label: str  # POSITIVE / NEGATIVE / NEUTRAL
    lead_lag_note: str
    sentiment_docs: List[Dict[str, Any]]
    
    # 5. Aggregator / Verdict Agent outputs
    final_verdict: str
    final_confidence: float
    final_explanation: str
    
    # Ordered execution trace accumulated at each node
    trace: List[Dict[str, Any]]
