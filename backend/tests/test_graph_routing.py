import pytest
from backend.app.graph.routing import route_after_trust, should_loop_back_verification
from backend.app.graph.builder import create_marketverify_graph
from backend.app.agents.state import AgentState


def test_routing_after_trust_low_score_triggers_deep_retrieval():
    state_low: AgentState = {
        "trust_score": 0.25,
        "trust_confidence": "HIGH",
    }
    decision_low = route_after_trust(state_low)
    assert decision_low["deep_retrieval_flag"] is True

    state_untested: AgentState = {
        "trust_score": 0.50,
        "trust_confidence": "LOW",
    }
    decision_untested = route_after_trust(state_untested)
    assert decision_untested["deep_retrieval_flag"] is True


def test_routing_after_trust_high_score_keeps_standard_retrieval():
    state_high: AgentState = {
        "trust_score": 0.85,
        "trust_confidence": "HIGH",
    }
    decision = route_after_trust(state_high)
    assert decision["deep_retrieval_flag"] is False


def test_routing_after_verification_inconclusive_first_pass_loops_back():
    state: AgentState = {
        "verification_status": "NO_EVIDENCE_FOUND",
        "verification_pass_count": 1,
        "verification_confidence": 0.35,
    }
    next_node = should_loop_back_verification(state)
    assert next_node == "verification"


def test_routing_after_verification_inconclusive_second_pass_proceeds_to_sentiment():
    state: AgentState = {
        "verification_status": "NO_EVIDENCE_FOUND",
        "verification_pass_count": 2,  # Already looped back once
        "verification_confidence": 0.35,
    }
    next_node = should_loop_back_verification(state)
    assert next_node == "sentiment"


def test_routing_after_verification_corroborated_proceeds_to_sentiment():
    state: AgentState = {
        "verification_status": "CORROBORATED",
        "verification_pass_count": 1,
        "verification_confidence": 0.90,
    }
    next_node = should_loop_back_verification(state)
    assert next_node == "sentiment"


@pytest.mark.asyncio
async def test_full_graph_execution_end_to_end():
    graph = create_marketverify_graph()
    
    initial_state: AgentState = {
        "claim_id": "test-e2e",
        "raw_text": "Reliance Retail is acquiring 40% stake in Zepto",
        "source_handle": "@dalalstreetinsider",
        "language": "en",
        "normalized_text": "",
        "ticker": "RELIANCE",
        "company_name": "Reliance Industries Limited",
        "extracted_entities": [],
        "trust_score": 0.5,
        "trust_confidence": "LOW",
        "trust_rationale": "",
        "trust_docs": [],
        "deep_retrieval_flag": False,
        "verification_pass_count": 0,
        "loop_back_triggered": False,
        "verification_status": "NO_EVIDENCE_FOUND",
        "verification_confidence": 0.0,
        "verification_citations": [],
        "verification_docs": [],
        "sentiment_label": "NEUTRAL",
        "lead_lag_note": "",
        "sentiment_docs": [],
        "final_verdict": "",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    final_state = await graph.ainvoke(initial_state)

    assert final_state["final_verdict"] != ""
    assert final_state["final_confidence"] > 0.0
    assert len(final_state["trace"]) >= 5
    agent_names = [t["agent"] for t in final_state["trace"]]
    assert "IngestionNormalizerAgent" in agent_names
    assert "TrustTierAgent" in agent_names
    assert "VerificationAgent" in agent_names
    assert "SentimentAgent" in agent_names
    assert "AggregatorVerdictAgent" in agent_names
