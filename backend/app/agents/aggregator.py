from datetime import datetime, timezone
from typing import Dict, Any
from backend.app.agents.state import AgentState
from backend.app.models.verdict import VerdictStatus
from backend.app.core.logging import logger


class AggregatorVerdictAgent:
    """
    Synthesizes Trust Score, Verification Evidence, and Sentiment/Market Dynamics
    into a final definitive Verdict and Confidence Score. Performs no retrieval of its own.
    """

    def __init__(self):
        self.name = "AggregatorVerdictAgent"

    def synthesize(self, state: AgentState) -> Dict[str, Any]:
        trust_score = state.get("trust_score", 0.5)
        trust_conf = state.get("trust_confidence", "LOW")
        verification_status = state.get("verification_status", "NO_EVIDENCE_FOUND")
        verification_conf = state.get("verification_confidence", 0.4)
        citations = state.get("verification_citations", [])
        sentiment_label = state.get("sentiment_label", "NEUTRAL")
        lead_lag_note = state.get("lead_lag_note", "")
        source_handle = state.get("source_handle", "Unknown")
        ticker = state.get("ticker", "Target Company")

        # Decision matrix
        if verification_status == "CORROBORATED":
            verdict = VerdictStatus.CORROBORATED_OFFICIAL
            # High confidence since backed by official SEBI/exchange filing
            final_conf = min(0.98, max(0.80, 0.6 * verification_conf + 0.4 * trust_score))
            explanation = (
                f"VERIFIED TRUE: The claim regarding {ticker} is corroborated by official regulatory filings. "
                f"Citations include {citations[0]['headline']} (dated {citations[0]['filing_date']}). "
                f"Source '{source_handle}' provided accurate intelligence (Trust Score: {trust_score:.2f}). "
                f"Sentiment is {sentiment_label}. Market dynamic: {lead_lag_note}"
            )

        elif verification_status == "CONTRADICTED":
            if trust_score < 0.35:
                verdict = VerdictStatus.DEBUNKED_FALSEHOOD
                final_conf = min(0.96, max(0.85, 0.7 * verification_conf + 0.3 * (1.0 - trust_score)))
                explanation = (
                    f"DEBUNKED FALSE: The claim regarding {ticker} is explicitly refuted by official company disclosures. "
                    f"Source '{source_handle}' has poor historical reliability (Trust Score: {trust_score:.2f}). "
                    f"Refuting filing: {citations[0]['headline']} ({citations[0]['filing_type']})."
                )
            else:
                verdict = VerdictStatus.CONTRADICTED_BY_FILING
                final_conf = min(0.92, max(0.78, 0.75 * verification_conf + 0.25 * (1.0 - trust_score)))
                explanation = (
                    f"CONTRADICTED: Official regulatory clarification refutes this statement ({citations[0]['headline']}), "
                    f"contradicting source '{source_handle}' (Trust Score: {trust_score:.2f})."
                )

        else:  # NO_EVIDENCE_FOUND
            if trust_score >= 0.70 and trust_conf == "HIGH":
                verdict = VerdictStatus.LIKELY_CREDIBLE
                final_conf = round(0.60 * trust_score + 0.20, 2)
                explanation = (
                    f"LIKELY CREDIBLE (PENDING FILING): While no formal regulatory disclosure has been registered yet for {ticker}, "
                    f"source '{source_handle}' carries an exceptional historical track record (Trust Score: {trust_score:.2f}). "
                    f"Sentiment: {sentiment_label}. Expected market lead: {lead_lag_note}"
                )
            elif trust_score < 0.40:
                verdict = VerdictStatus.UNVERIFIED_RUMOR
                final_conf = round(0.50 + (1.0 - trust_score) * 0.25, 2)
                explanation = (
                    f"UNVERIFIED RUMOR / SPECULATION: No regulatory filings corroborate this claim for {ticker}, "
                    f"and source '{source_handle}' exhibits low or untested credibility (Trust Score: {trust_score:.2f}). "
                    f"Investors are cautioned against trading on this unconfirmed speculation."
                )
            else:
                verdict = VerdictStatus.NO_EVIDENCE_FOUND
                final_conf = 0.50
                explanation = (
                    f"INSUFFICIENT EVIDENCE: No official filings found for {ticker}, and source '{source_handle}' "
                    f"has an intermediate credibility history (Trust Score: {trust_score:.2f})."
                )

        return {
            "final_verdict": verdict.value,
            "final_confidence": round(float(final_conf), 2),
            "final_explanation": explanation,
        }

    def __call__(self, state: AgentState) -> Dict[str, Any]:
        result = self.synthesize(state)

        trace_entry = {
            "agent": self.name,
            "step_index": len(state.get("trace", [])) + 1,
            "input_summary": (
                f"TrustScore: {state.get('trust_score', 0):.2f} | "
                f"Verification: {state.get('verification_status')} (Conf: {state.get('verification_confidence', 0):.2f}) | "
                f"Sentiment: {state.get('sentiment_label')}"
            ),
            "retrieved_doc_ids": [],
            "retrieved_docs_preview": [],
            "output_summary": f"Verdict: {result['final_verdict']} | Confidence: {result['final_confidence']} | {result['final_explanation'][:120]}...",
            "metadata": {
                "final_verdict": result["final_verdict"],
                "final_confidence": result["final_confidence"],
                "final_explanation": result["final_explanation"],
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        trace_list = list(state.get("trace", []))
        trace_list.append(trace_entry)

        logger.info(
            f"[{self.name}] Final Verdict: {result['final_verdict']} (Confidence: {result['final_confidence']})"
        )

        return {
            "final_verdict": result["final_verdict"],
            "final_confidence": result["final_confidence"],
            "final_explanation": result["final_explanation"],
            "trace": trace_list,
        }
