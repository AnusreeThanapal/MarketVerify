import pytest
from backend.app.agents.sentiment import SentimentAgent
from backend.app.agents.state import AgentState


def test_sentiment_agent_english_classification():
    agent = SentimentAgent()
    mock_samples = [
        {
            "doc_id": "s1",
            "language": "en",
            "text_sample": "Reliance acquires 40% stake in Zepto",
            "sentiment_label": "POSITIVE",
            "tone": "expansionary_bullish",
            "lead_lag_behavior": "Lead signal: M&A rumors prompt pre-announcement rally.",
            "score": 0.82,
        }
    ]

    analysis = agent.classify_sentiment_and_dynamics("Reliance acquires Zepto stake", mock_samples)

    assert analysis["sentiment_label"] == "POSITIVE"
    assert "Lead signal" in analysis["lead_lag_note"]


def test_sentiment_agent_tamil_classification():
    agent = SentimentAgent()
    mock_samples = [
        {
            "doc_id": "s2",
            "language": "ta",
            "text_sample": "டாடா ஸ்டீல் பங்கு பிரிப்பு வதந்தி மறுப்பு",
            "sentiment_label": "NEUTRAL",
            "tone": "rebuttal_neutral",
            "lead_lag_behavior": "Lead signal: sharp correction immediately upon denial.",
            "score": 0.79,
        }
    ]

    analysis = agent.classify_sentiment_and_dynamics("டாடா ஸ்டீல் பங்கு பிரிப்பு வதந்தி", mock_samples)

    assert analysis["sentiment_label"] == "NEUTRAL"
    assert "sharp correction" in analysis["lead_lag_note"]
