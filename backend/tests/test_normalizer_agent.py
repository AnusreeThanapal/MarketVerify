import pytest
from backend.app.agents.normalizer import IngestionNormalizerAgent
from backend.app.agents.state import AgentState


def test_normalizer_english_entity_extraction():
    agent = IngestionNormalizerAgent()
    state: AgentState = {
        "claim_id": "test-1",
        "raw_text": "Reliance Retail is buying 40% in Zepto fast delivery",
        "source_handle": "@test_source",
        "language": "",
        "normalized_text": "",
        "ticker": None,
        "company_name": None,
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
        "final_verdict": "NO_EVIDENCE_FOUND",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    result = agent(state)

    assert result["language"] == "en"
    assert result["ticker"] == "RELIANCE"
    assert "Reliance Industries Limited" in result["company_name"]
    assert len(result["trace"]) == 1
    assert result["trace"][0]["agent"] == "IngestionNormalizerAgent"


def test_normalizer_tamil_entity_extraction():
    agent = IngestionNormalizerAgent()
    state: AgentState = {
        "claim_id": "test-2",
        "raw_text": "ரிலையன்ஸ் ஜியோ புதிய AI டேட்டா சென்டரை சென்னையில் திறக்கிறது",
        "source_handle": "@tamil_guru",
        "language": "",
        "normalized_text": "",
        "ticker": None,
        "company_name": None,
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
        "final_verdict": "NO_EVIDENCE_FOUND",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    result = agent(state)

    assert result["language"] == "ta"
    assert result["ticker"] == "RELIANCE"
    assert len(result["trace"]) == 1
