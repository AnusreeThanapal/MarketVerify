import pytest
from unittest.mock import MagicMock
from backend.app.agents.trust_tier import TrustTierAgent
from backend.app.agents.state import AgentState


def test_trust_tier_calculation_known_high_trust_source():
    # Mock trajectory records
    mock_docs = [
        {"doc_id": "1", "source_handle": "@dalalstreetinsider", "was_accurate": True, "past_claim_text": "Claim 1", "outcome_summary": "Confirmed"},
        {"doc_id": "2", "source_handle": "@dalalstreetinsider", "was_accurate": True, "past_claim_text": "Claim 2", "outcome_summary": "Confirmed"},
        {"doc_id": "3", "source_handle": "@dalalstreetinsider", "was_accurate": True, "past_claim_text": "Claim 3", "outcome_summary": "Confirmed"},
        {"doc_id": "4", "source_handle": "@dalalstreetinsider", "was_accurate": False, "past_claim_text": "Claim 4", "outcome_summary": "Denied"},
    ]

    agent = TrustTierAgent()
    eval_res = agent.calculate_trust("@dalalstreetinsider", mock_docs)

    assert eval_res["total_claims"] == 4
    assert eval_res["accurate_claims"] == 3
    assert eval_res["trust_score"] > 0.65
    assert eval_res["confidence"] in ["HIGH", "MEDIUM"]
    assert "historical evaluation" in eval_res["rationale"]


def test_trust_tier_calculation_unknown_source():
    agent = TrustTierAgent()
    eval_res = agent.calculate_trust("@completely_unknown_bot", [])

    assert eval_res["total_claims"] == 0
    assert eval_res["trust_score"] == 0.35
    assert eval_res["confidence"] == "LOW"
    assert "no verified historical trajectory" in eval_res["rationale"]


def test_trust_tier_agent_node_execution():
    agent = TrustTierAgent()
    agent.retrieve_source_trajectory = MagicMock(return_value=[
        {"doc_id": "1", "source_handle": "@test_guru", "was_accurate": True, "past_claim_text": "Claim 1", "outcome_summary": "Ok"}
    ])

    state: AgentState = {
        "claim_id": "test-3",
        "raw_text": "Infosys acquiring tech firm",
        "source_handle": "@test_guru",
        "language": "en",
        "normalized_text": "Infosys acquiring tech firm",
        "ticker": "INFY",
        "company_name": "Infosys Limited",
        "extracted_entities": ["infosys"],
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
        "final_verdict": "NO_EVIDENCE_FOUND",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    result = agent(state)
    assert result["trust_score"] > 0.0
    assert len(result["trace"]) == 1
    assert result["trace"][0]["agent"] == "TrustTierAgent"
