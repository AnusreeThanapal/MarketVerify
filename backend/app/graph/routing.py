from typing import Literal, Dict, Any
from backend.app.agents.state import AgentState
from backend.app.config import get_settings
from backend.app.core.logging import logger

settings = get_settings()


def route_after_trust(state: AgentState) -> Dict[str, Any]:
    """
    Evaluates trust result to determine if Verification requires a DEEP retrieval pass.
    If trust score is low (< 0.40) or confidence is LOW, flag deep retrieval.
    """
    trust_score = state.get("trust_score", 0.5)
    trust_conf = state.get("trust_confidence", "LOW")
    
    is_low_trust = (trust_score <= settings.TRUST_LOW_CONFIDENCE_THRESHOLD) or (trust_conf == "LOW")
    
    logger.info(
        f"[Routing] After Trust-Tier: TrustScore={trust_score:.2f} ({trust_conf}) -> DeepRetrievalFlag={is_low_trust}"
    )
    
    return {
        "deep_retrieval_flag": is_low_trust,
    }


def should_loop_back_verification(state: AgentState) -> Literal["verification", "sentiment"]:
    """
    Conditional edge after Verification:
    If verification status is NO_EVIDENCE_FOUND and we have not yet looped back (pass_count < 2),
    loop back to Verification Agent for an expanded query pass.
    Otherwise proceed to Sentiment Agent.
    """
    pass_count = state.get("verification_pass_count", 0)
    verif_status = state.get("verification_status", "NO_EVIDENCE_FOUND")
    verif_conf = state.get("verification_confidence", 0.0)

    # Condition for loopback: inconclusive evidence and pass count is 1 (meaning first pass finished)
    if verif_status == "NO_EVIDENCE_FOUND" and pass_count < 2:
        logger.info(
            f"[Routing] Verification inconclusive (Status={verif_status}, Conf={verif_conf:.2f}). Triggering Loop-back retry (Pass #{pass_count + 1})."
        )
        return "verification"
    
    logger.info(f"[Routing] Verification complete (Status={verif_status}). Proceeding to Sentiment.")
    return "sentiment"
