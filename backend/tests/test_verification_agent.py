import pytest
from unittest.mock import MagicMock
from backend.app.agents.verification import VerificationAgent
from backend.app.agents.state import AgentState


def test_verification_agent_corroboration():
    agent = VerificationAgent()
    mock_docs = [
        {
            "doc_id": "DOC-1",
            "ticker": "RELIANCE",
            "company_name": "Reliance Industries Limited",
            "filing_type": "SEBI Reg 30",
            "filing_date": "2024-06-18",
            "headline": "Reliance Retail executes agreement to acquire 40% stake in Zepto",
            "snippet": "Definitive agreement signed for 40% equity stake...",
            "full_content": "Reliance Retail executes definitive transaction documents for subscribing to 40% equity stake in Zepto.",
            "similarity_score": 0.88,
            "source_url": "https://bse.com/doc1",
        }
    ]

    verif_res = agent.verify_claim(
        claim_text="Reliance acquiring 40% in Zepto",
        ticker="RELIANCE",
        docs=mock_docs,
        is_deep=False,
    )

    assert verif_res["status"] == "CORROBORATED"
    assert verif_res["confidence"] >= 0.85
    assert len(verif_res["citations"]) == 1
    assert "CORROBORATED" in verif_res["rationale"]


def test_verification_agent_contradiction():
    agent = VerificationAgent()
    mock_docs = [
        {
            "doc_id": "DOC-2",
            "ticker": "HDFCBANK",
            "company_name": "HDFC Bank",
            "filing_type": "Exchange Clarification",
            "filing_date": "2024-06-05",
            "headline": "Rebuttal of speculative market rumors regarding CEO resignation",
            "snippet": "Bank strongly refutes malicious rumors regarding CEO resignation...",
            "full_content": "HDFC Bank strongly refutes and denies unsubstantiated rumors claiming CEO resignation.",
            "similarity_score": 0.84,
            "source_url": "https://bse.com/doc2",
        }
    ]

    verif_res = agent.verify_claim(
        claim_text="HDFC Bank CEO resigns",
        ticker="HDFCBANK",
        docs=mock_docs,
        is_deep=False,
    )

    assert verif_res["status"] == "CONTRADICTED"
    assert verif_res["confidence"] >= 0.70
    assert len(verif_res["citations"]) == 1
    assert "CONTRADICTED" in verif_res["rationale"]


def test_verification_agent_no_evidence():
    agent = VerificationAgent()
    verif_res = agent.verify_claim(
        claim_text="Unknown company doing undisclosed acquisition",
        ticker="UNKNOWN",
        docs=[],
        is_deep=False,
    )

    assert verif_res["status"] == "NO_EVIDENCE_FOUND"
    assert verif_res["confidence"] <= 0.40
    assert len(verif_res["citations"]) == 0


def test_verification_query_builder_standard_vs_loopback():
    agent = VerificationAgent()
    q_standard = agent.build_query("Reliance buying Zepto", "RELIANCE", "Reliance Industries", is_loopback=False)
    q_loopback = agent.build_query("Reliance buying Zepto", "RELIANCE", "Reliance Industries", is_loopback=True)

    assert "Reliance Industries" in q_standard
    assert "RELIANCE" in q_standard
    assert "merger acquisition" in q_loopback
    assert "clarification" in q_loopback
