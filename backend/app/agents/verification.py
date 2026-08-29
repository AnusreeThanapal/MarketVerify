import re
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from qdrant_client import models
from backend.app.agents.state import AgentState
from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.agents.llm_provider import get_embedding_service

settings = get_settings()


class VerificationAgent:
    """
    Verifies claim veracity against official regulatory disclosures and filings in `filing_store`.
    Implements distinct retrieval modes (standard vs deep) and query expansion on loop-back.
    """

    def __init__(self, qdrant_client=None, embedding_svc=None):
        self.name = "VerificationAgent"
        self.qdrant_client = qdrant_client
        self.embedding_svc = embedding_svc or get_embedding_service()

    def get_client(self):
        if self.qdrant_client:
            return self.qdrant_client
        return get_qdrant_service().get_sync_client()

    def build_query(
        self,
        normalized_text: str,
        ticker: Optional[str],
        company_name: Optional[str],
        is_loopback: bool,
    ) -> str:
        """Constructs or expands the vector search query."""
        if not is_loopback:
            parts = []
            if company_name:
                parts.append(company_name)
            if ticker:
                parts.append(ticker)
            parts.append(normalized_text)
            return " ".join(parts)
        else:
            # Query Expansion on loop-back retry: add synonyms, broader keywords
            expanded_tokens = [normalized_text]
            if ticker:
                expanded_tokens.append(f"{ticker} disclosure announcement BSE NSE")
            if company_name:
                expanded_tokens.append(f"{company_name} corporate filing board meeting clarification")
            expanded_tokens.append("merger acquisition resignation split dividend capex tender")
            return " ".join(expanded_tokens)

    def retrieve_filings(
        self,
        query: str,
        ticker: Optional[str],
        is_deep: bool,
    ) -> List[Dict[str, Any]]:
        q_svc = get_qdrant_service()
        k = settings.DEEP_RETRIEVAL_K if is_deep else settings.DEFAULT_RETRIEVAL_K
        score_threshold = settings.DEEP_SCORE_THRESHOLD if is_deep else settings.DEFAULT_SCORE_THRESHOLD

        query_vector = self.embedding_svc.get_embedding(query)
        retrieved = []

        try:
            # 1. Attempt filtered search on ticker if known
            if ticker:
                filter_cond = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="ticker",
                            match=models.MatchValue(value=ticker.upper()),
                        )
                    ]
                )
                search_res = q_svc.search_points(
                    collection_name=settings.QDRANT_COLLECTION_FILING,
                    query_vector=query_vector,
                    query_filter=filter_cond,
                    limit=k,
                )
                for hit in search_res:
                    score_val = getattr(hit, "score", 0.85)
                    if score_val >= score_threshold or is_deep:
                        retrieved.append(self._format_hit(hit))

            # 2. If filtered search yielded few results, or in deep mode, search across all filings
            if len(retrieved) < (2 if not is_deep else 4):
                unfiltered_res = q_svc.search_points(
                    collection_name=settings.QDRANT_COLLECTION_FILING,
                    query_vector=query_vector,
                    limit=k,
                )
                existing_ids = {r["doc_id"] for r in retrieved}
                for hit in unfiltered_res:
                    doc_id = hit.payload.get("doc_id", str(hit.id))
                    score_val = getattr(hit, "score", 0.85)
                    if doc_id not in existing_ids and (score_val >= score_threshold or is_deep):
                        retrieved.append(self._format_hit(hit))

        except Exception as e:
            logger.warning(f"[{self.name}] Error querying Qdrant filing_store: {e}")

        # Sort by relevance score
        retrieved.sort(key=lambda x: x["similarity_score"], reverse=True)
        return retrieved[:k]

    def _format_hit(self, hit) -> Dict[str, Any]:
        p = hit.payload or {}
        return {
            "doc_id": p.get("doc_id", str(hit.id)),
            "ticker": p.get("ticker", ""),
            "company_name": p.get("company_name", ""),
            "filing_type": p.get("filing_type", "Filing"),
            "filing_date": p.get("filing_date", "2024-01-01"),
            "headline": p.get("headline", ""),
            "snippet": p.get("content_chunk", "")[:250] + "...",
            "full_content": p.get("content_chunk", ""),
            "similarity_score": round(float(hit.score), 4),
            "source_url": p.get("source_url", ""),
        }

    def verify_claim(
        self,
        claim_text: str,
        ticker: Optional[str],
        docs: List[Dict[str, Any]],
        is_deep: bool,
    ) -> Dict[str, Any]:
        if not docs:
            return {
                "status": "NO_EVIDENCE_FOUND",
                "confidence": 0.30,
                "citations": [],
                "rationale": "No relevant official SEBI/exchange filings found matching the target company or claim statement.",
            }

        # Analyze top retrieved documents against the claim
        claim_lower = claim_text.lower()
        
        # Check for contradiction / denial keywords in official filings
        denial_indicators = ["refutes", "denying", "no such proposal", "rebuttal", "false", "categorically confirm", "clarification on rumor", "unsubstantiated"]
        corroboration_indicators = ["approved", "executed", "agreement", "sanctioned", "signed definitive", "informs", "authorized", "awarded"]

        best_doc = docs[0]
        top_content = (best_doc.get("headline", "") + " " + best_doc.get("full_content", "")).lower()

        # Check if filing is an explicit clarification/denial
        has_denial = any(w in top_content for w in denial_indicators)
        has_corroboration = any(w in top_content for w in corroboration_indicators)

        citations = [
            {
                "doc_id": d["doc_id"],
                "filing_type": d["filing_type"],
                "filing_date": d["filing_date"],
                "headline": d["headline"],
                "similarity_score": d["similarity_score"],
                "snippet": d["snippet"],
                "source_url": d.get("source_url"),
            }
            for d in docs[:3]
        ]

        if best_doc["similarity_score"] >= 0.70 or (is_deep and best_doc["similarity_score"] >= 0.50):
            if has_denial:
                return {
                    "status": "CONTRADICTED",
                    "confidence": 0.88 if best_doc["similarity_score"] >= 0.75 else 0.72,
                    "citations": citations,
                    "rationale": f"Claim is directly CONTRADICTED by official disclosure '{best_doc['headline']}' ({best_doc['doc_id']}) dated {best_doc['filing_date']}.",
                }
            elif has_corroboration:
                return {
                    "status": "CORROBORATED",
                    "confidence": 0.92 if best_doc["similarity_score"] >= 0.75 else 0.78,
                    "citations": citations,
                    "rationale": f"Claim is CORROBORATED by official regulatory filing '{best_doc['headline']}' ({best_doc['doc_id']}) dated {best_doc['filing_date']}.",
                }
            else:
                return {
                    "status": "CORROBORATED",
                    "confidence": 0.70,
                    "citations": citations,
                    "rationale": f"Filing evidence '{best_doc['headline']}' provides strong contextual alignment with the submitted claim.",
                }
        else:
            return {
                "status": "NO_EVIDENCE_FOUND",
                "confidence": 0.40,
                "citations": citations,
                "rationale": "Retrieved filings lack sufficient specificity or semantic alignment to decisively confirm or refute the claim.",
            }

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        normalized_text = state.get("normalized_text") or state.get("raw_text", "")
        ticker = state.get("ticker")
        company_name = state.get("company_name")
        is_deep = state.get("deep_retrieval_flag", False)
        pass_count = state.get("verification_pass_count", 0)
        is_loopback = pass_count > 0

        search_query = self.build_query(normalized_text, ticker, company_name, is_loopback)
        retrieved_docs = self.retrieve_filings(search_query, ticker, is_deep)
        verification_res = self.verify_claim(normalized_text, ticker, retrieved_docs, is_deep)

        doc_ids = [d["doc_id"] for d in retrieved_docs]
        preview = [
            {
                "doc_id": d["doc_id"],
                "headline": d["headline"],
                "type": d["filing_type"],
                "date": d["filing_date"],
                "score": d["similarity_score"],
            }
            for d in retrieved_docs[:3]
        ]

        mode_str = "DEEP" if is_deep else "STANDARD"
        pass_str = f"Pass #{pass_count + 1}" + (" (Expanded Loopback)" if is_loopback else "")

        trace_entry = {
            "agent": self.name,
            "step_index": len(state.get("trace", [])) + 1,
            "input_summary": f"Query: '{search_query[:70]}...' | Mode: {mode_str} | {pass_str}",
            "retrieved_doc_ids": doc_ids,
            "retrieved_docs_preview": preview,
            "output_summary": f"Status: {verification_res['status']} | Confidence: {verification_res['confidence']:.2f} | Citations: {len(verification_res['citations'])} | {verification_res['rationale'][:120]}...",
            "metadata": {
                "retrieval_mode": mode_str,
                "pass_number": pass_count + 1,
                "is_loopback": is_loopback,
                "status": verification_res["status"],
                "confidence": verification_res["confidence"],
                "total_docs_retrieved": len(retrieved_docs),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        trace_list = list(state.get("trace", []))
        trace_list.append(trace_entry)

        logger.info(
            f"[{self.name}] {pass_str} -> Status={verification_res['status']}, Conf={verification_res['confidence']:.2f}, Mode={mode_str}"
        )

        return {
            "verification_status": verification_res["status"],
            "verification_confidence": verification_res["confidence"],
            "verification_citations": verification_res["citations"],
            "verification_docs": retrieved_docs,
            "verification_pass_count": pass_count + 1,
            "trace": trace_list,
        }
