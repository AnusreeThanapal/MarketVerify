from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from qdrant_client import models
from backend.app.agents.state import AgentState
from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.agents.llm_provider import get_embedding_service

settings = get_settings()


class SentimentAgent:
    """
    Grounds tone and price lead-lag dynamics by retrieving labeled English and Tamil
    market sentiment examples from `sentiment_corpus`.
    Does NOT verify the claim — computes market psychological tone and timing signal only.
    """

    def __init__(self, qdrant_client=None, embedding_svc=None):
        self.name = "SentimentAgent"
        self.qdrant_client = qdrant_client
        self.embedding_svc = embedding_svc or get_embedding_service()

    def get_client(self):
        if self.qdrant_client:
            return self.qdrant_client
        return get_qdrant_service().get_sync_client()

    def retrieve_sentiment_samples(self, text: str, language: str) -> List[Dict[str, Any]]:
        query_vector = self.embedding_svc.get_embedding(f"Language: {language}. Text: {text}")
        q_svc = get_qdrant_service()
        retrieved_samples = []
        try:
            filter_cond = None
            if language in ["en", "ta"]:
                filter_cond = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="language",
                            match=models.MatchValue(value=language),
                        )
                    ]
                )

            search_res = q_svc.search_points(
                collection_name=settings.QDRANT_COLLECTION_SENTIMENT,
                query_vector=query_vector,
                query_filter=filter_cond,
                limit=3,
            )

            # Fallback if language specific has no hits
            if not search_res:
                search_res = q_svc.search_points(
                    collection_name=settings.QDRANT_COLLECTION_SENTIMENT,
                    query_vector=query_vector,
                    limit=3,
                )

            for hit in search_res:
                p = hit.payload or {}
                score_val = getattr(hit, "score", 0.8)
                retrieved_samples.append({
                    "doc_id": p.get("doc_id", str(hit.id)),
                    "language": p.get("language", "en"),
                    "text_sample": p.get("text_sample", ""),
                    "sentiment_label": p.get("sentiment_label", "NEUTRAL"),
                    "tone": p.get("tone", "neutral"),
                    "lead_lag_behavior": p.get("lead_lag_behavior", ""),
                    "score": round(float(score_val), 4),
                })
        except Exception as e:
            logger.warning(f"[{self.name}] Error searching Qdrant sentiment_corpus: {e}")

        return retrieved_samples

    def classify_sentiment_and_dynamics(
        self,
        text: str,
        retrieved_samples: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        if not retrieved_samples:
            # Rule-based baseline fallback
            lower = text.lower()
            if any(w in lower for w in ["acquire", "win", "hike", "growth", "approved", "வெற்றி", "அமைக்கிறது"]):
                return {
                    "sentiment_label": "POSITIVE",
                    "lead_lag_note": "Lead signal: Positive expansion/deal rumors tend to generate speculative volume 24-48 hours before official filing.",
                }
            elif any(w in lower for w in ["resign", "embargo", "reject", "loss", "crackdown", "பொய்யானது"]):
                return {
                    "sentiment_label": "NEGATIVE",
                    "lead_lag_note": "Lead signal: Negative leadership/governance rumors trigger immediate sharp discounting with elevated volatility.",
                }
            return {
                "sentiment_label": "NEUTRAL",
                "lead_lag_note": "Coincident signal: Neutral procedural updates are absorbed with minimal speculative drift.",
            }

        top_sample = retrieved_samples[0]
        sentiment_label = top_sample.get("sentiment_label", "NEUTRAL")
        lead_lag_note = top_sample.get(
            "lead_lag_behavior",
            "Coincident market dynamic: Speculative volume aligns closely with disclosure timeline.",
        )

        return {
            "sentiment_label": sentiment_label,
            "lead_lag_note": lead_lag_note,
        }

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        normalized_text = state.get("normalized_text") or state.get("raw_text", "")
        language = state.get("language", "en")

        retrieved_samples = self.retrieve_sentiment_samples(normalized_text, language)
        analysis = self.classify_sentiment_and_dynamics(normalized_text, retrieved_samples)

        doc_ids = [d["doc_id"] for d in retrieved_samples]
        preview = [
            {
                "doc_id": d["doc_id"],
                "sample": d["text_sample"][:60] + "...",
                "sentiment": d["sentiment_label"],
                "tone": d["tone"],
            }
            for d in retrieved_samples
        ]

        trace_entry = {
            "agent": self.name,
            "step_index": len(state.get("trace", [])) + 1,
            "input_summary": f"Text: '{normalized_text[:60]}...' | Language: {language}",
            "retrieved_doc_ids": doc_ids,
            "retrieved_docs_preview": preview,
            "output_summary": f"Sentiment: {analysis['sentiment_label']} | Lead-Lag Dynamic: {analysis['lead_lag_note'][:100]}...",
            "metadata": {
                "sentiment_label": analysis["sentiment_label"],
                "lead_lag_note": analysis["lead_lag_note"],
                "samples_matched": len(retrieved_samples),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        trace_list = list(state.get("trace", []))
        trace_list.append(trace_entry)

        logger.info(
            f"[{self.name}] Sentiment={analysis['sentiment_label']} | LeadLag={analysis['lead_lag_note'][:50]}..."
        )

        return {
            "sentiment_label": analysis["sentiment_label"],
            "lead_lag_note": analysis["lead_lag_note"],
            "sentiment_docs": retrieved_samples,
            "trace": trace_list,
        }
