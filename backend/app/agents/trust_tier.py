from datetime import datetime, timezone
from typing import Dict, Any, List
from qdrant_client import models
from backend.app.agents.state import AgentState
from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.agents.llm_provider import get_embedding_service

settings = get_settings()


class TrustTierAgent:
    """
    Evaluates the historical credibility and trajectory of the rumor's source
    by retrieving past track record data from `trust_tier_store`.
    """

    def __init__(self, qdrant_client=None, embedding_svc=None):
        self.name = "TrustTierAgent"
        self.qdrant_client = qdrant_client
        self.embedding_svc = embedding_svc or get_embedding_service()

    def get_client(self):
        if self.qdrant_client:
            return self.qdrant_client
        return get_qdrant_service().get_sync_client()

    def retrieve_source_trajectory(self, source_handle: str, claim_text: str) -> List[Dict[str, Any]]:
        query_vector = self.embedding_svc.get_embedding(f"Source: {source_handle}. Text: {claim_text}")
        q_svc = get_qdrant_service()
        retrieved_docs = []
        try:
            # 1. First attempt exact or filtered match on source_handle
            filter_condition = models.Filter(
                must=[
                    models.FieldCondition(
                        key="source_handle",
                        match=models.MatchValue(value=source_handle.lower()),
                    )
                ]
            )
            
            search_res = q_svc.search_points(
                collection_name=settings.QDRANT_COLLECTION_TRUST,
                query_vector=query_vector,
                query_filter=filter_condition,
                limit=10,
            )

            # 2. If no direct handle records, perform semantic search across similar source profiles
            if not search_res:
                search_res = q_svc.search_points(
                    collection_name=settings.QDRANT_COLLECTION_TRUST,
                    query_vector=query_vector,
                    limit=5,
                )

            for hit in search_res:
                retrieved_docs.append({
                    "doc_id": hit.payload.get("doc_id", str(hit.id)),
                    "source_handle": hit.payload.get("source_handle"),
                    "source_name": hit.payload.get("source_name"),
                    "past_claim_text": hit.payload.get("past_claim_text"),
                    "was_accurate": hit.payload.get("was_accurate"),
                    "lag_hours": hit.payload.get("lag_hours"),
                    "category": hit.payload.get("category"),
                    "outcome_summary": hit.payload.get("outcome_summary"),
                    "score": getattr(hit, "score", 0.8),
                })
        except Exception as e:
            logger.warning(f"[{self.name}] Error searching Qdrant trust_tier_store: {e}")

        return retrieved_docs

    def calculate_trust(self, source_handle: str, docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Handle matching
        exact_matches = [d for d in docs if d.get("source_handle", "").lower() == source_handle.lower()]
        
        if not exact_matches:
            # Unknown source with no prior trajectory
            return {
                "trust_score": 0.35,  # Low default prior for unknown social handles
                "confidence": "LOW",
                "rationale": f"Source '{source_handle}' has no verified historical trajectory records in the trust repository. Assigned conservative default prior score (0.35).",
                "total_claims": 0,
                "accurate_claims": 0,
            }

        total = len(exact_matches)
        accurate = sum(1 for d in exact_matches if d.get("was_accurate") is True)
        accuracy_rate = accurate / total

        # Weighting: Bayesian adjustment with small Laplace smoothing
        trust_score = round((accurate + 1.0) / (total + 2.0), 3)

        if total >= 3:
            confidence = "HIGH" if trust_score >= 0.75 or trust_score <= 0.3 else "MEDIUM"
        else:
            confidence = "MEDIUM" if total >= 1 else "LOW"

        rationale = (
            f"Source '{source_handle}' historical evaluation: {accurate}/{total} past claims confirmed accurate "
            f"({accuracy_rate * 100:.1f}% raw accuracy). Calibrated Bayesian trust score: {trust_score:.2f} "
            f"with {confidence} confidence level."
        )

        return {
            "trust_score": trust_score,
            "confidence": confidence,
            "rationale": rationale,
            "total_claims": total,
            "accurate_claims": accurate,
        }

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        source_handle = state.get("source_handle", "unknown")
        raw_text = state.get("normalized_text") or state.get("raw_text", "")
        
        retrieved_docs = self.retrieve_source_trajectory(source_handle, raw_text)
        trust_eval = self.calculate_trust(source_handle, retrieved_docs)
        
        doc_ids = [d["doc_id"] for d in retrieved_docs]
        preview = [
            {
                "doc_id": d["doc_id"],
                "past_claim": d["past_claim_text"],
                "accurate": d["was_accurate"],
                "outcome": d["outcome_summary"],
            }
            for d in retrieved_docs[:3]
        ]

        trace_entry = {
            "agent": self.name,
            "step_index": len(state.get("trace", [])) + 1,
            "input_summary": f"Source handle: '{source_handle}' | Claim query: '{raw_text[:60]}...'",
            "retrieved_doc_ids": doc_ids,
            "retrieved_docs_preview": preview,
            "output_summary": f"Trust Score: {trust_eval['trust_score']} ({trust_eval['confidence']}) | Rationale: {trust_eval['rationale']}",
            "metadata": {
                "source_handle": source_handle,
                "trust_score": trust_eval["trust_score"],
                "confidence": trust_eval["confidence"],
                "total_claims_matched": trust_eval["total_claims"],
                "accurate_claims": trust_eval["accurate_claims"],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        trace_list = list(state.get("trace", []))
        trace_list.append(trace_entry)

        logger.info(
            f"[{self.name}] Source: {source_handle} -> Trust Score={trust_eval['trust_score']}, Conf={trust_eval['confidence']}"
        )

        return {
            "trust_score": trust_eval["trust_score"],
            "trust_confidence": trust_eval["confidence"],
            "trust_rationale": trust_eval["rationale"],
            "trust_docs": retrieved_docs,
            "trace": trace_list,
        }
