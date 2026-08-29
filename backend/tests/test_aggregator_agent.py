import pytest
from backend.app.agents.aggregator import AggregatorVerdictAgent
from backend.app.agents.state import AgentState
from backend.app.models.verdict import VerdictStatus


def test_aggregator_corroborated_verdict():
    agent = AggregatorVerdictAgent()
    state: AgentState = {
        "claim_id": "test-c1",
        "raw_text": "Reliance acquires 40% stake in Zepto",
        "source_handle": "@dalalstreetinsider",
        "language": "en",
        "normalized_text": "Reliance acquires 40% stake in Zepto",
        "ticker": "RELIANCE",
        "company_name": "Reliance Industries Limited",
        "extracted_entities": ["reliance", "zepto"],
        "trust_score": 0.80,
        "trust_confidence": "HIGH",
        "trust_rationale": "High track record",
        "trust_docs": [],
        "deep_retrieval_flag": False,
        "verification_pass_count": 1,
        "loop_back_triggered": False,
        "verification_status": "CORROBORATED",
        "verification_confidence": 0.90,
        "verification_citations": [{"headline": "SEBI Filing", "filing_date": "2024-06-18"}],
        "verification_docs": [],
        "sentiment_label": "POSITIVE",
        "lead_lag_note": "Lead rally anticipated",
        "sentiment_docs": [],
        "final_verdict": "",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    result = agent(state)

    assert result["final_verdict"] == VerdictStatus.CORROBORATED_OFFICIAL.value
    assert result["final_confidence"] >= 0.80
    assert "VERIFIED TRUE" in result["final_explanation"]
    assert len(result["trace"]) == 1


def test_aggregator_contradicted_debunked_verdict():
    agent = AggregatorVerdictAgent()
    state: AgentState = {
        "claim_id": "test-c2",
        "raw_text": "Paytm receives full banking license",
        "source_handle": "@pump_and_dump_scanner",
        "language": "en",
        "normalized_text": "Paytm receives full banking license",
        "ticker": "PAYTM",
        "company_name": "One97 Communications",
        "extracted_entities": ["paytm"],
        "trust_score": 0.20,
        "trust_confidence": "HIGH",
        "trust_rationale": "Poor track record",
        "trust_docs": [],
        "deep_retrieval_flag": True,
        "verification_pass_count": 1,
        "loop_back_triggered": False,
        "verification_status": "CONTRADICTED",
        "verification_confidence": 0.85,
        "verification_citations": [{"headline": "RBI Disciplinary Update", "filing_type": "Directive"}],
        "verification_docs": [],
        "sentiment_label": "NEGATIVE",
        "lead_lag_note": "Immediate lower circuit",
        "sentiment_docs": [],
        "final_verdict": "",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    result = agent(state)

    assert result["final_verdict"] == VerdictStatus.DEBUNKED_FALSEHOOD.value
    assert result["final_confidence"] >= 0.85
    assert "DEBUNKED FALSE" in result["final_explanation"]


def test_aggregator_likely_credible_pending_filing():
    agent = AggregatorVerdictAgent()
    state: AgentState = {
        "claim_id": "test-c3",
        "raw_text": "TCS winning $1B transformation deal",
        "source_handle": "@credible_analyst",
        "language": "en",
        "normalized_text": "TCS winning $1B transformation deal",
        "ticker": "TCS",
        "company_name": "Tata Consultancy Services",
        "extracted_entities": ["tcs"],
        "trust_score": 0.85,
        "trust_confidence": "HIGH",
        "trust_rationale": "Elite track record",
        "trust_docs": [],
        "deep_retrieval_flag": False,
        "verification_pass_count": 2,
        "loop_back_triggered": True,
        "verification_status": "NO_EVIDENCE_FOUND",
        "verification_confidence": 0.35,
        "verification_citations": [],
        "verification_docs": [],
        "sentiment_label": "POSITIVE",
        "lead_lag_note": "Lead signal rally",
        "sentiment_docs": [],
        "final_verdict": "",
        "final_confidence": 0.0,
        "final_explanation": "",
        "trace": [],
    }

    result = agent(state)

    assert result["final_verdict"] == VerdictStatus.LIKELY_CREDIBLE.value
    assert "LIKELY CREDIBLE" in result["final_explanation"]
