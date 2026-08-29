from langgraph.graph import StateGraph, START, END
from backend.app.agents.state import AgentState
from backend.app.agents.normalizer import IngestionNormalizerAgent
from backend.app.agents.trust_tier import TrustTierAgent
from backend.app.agents.verification import VerificationAgent
from backend.app.agents.sentiment import SentimentAgent
from backend.app.agents.aggregator import AggregatorVerdictAgent
from backend.app.graph.routing import route_after_trust, should_loop_back_verification


def create_marketverify_graph(
    normalizer_agent: IngestionNormalizerAgent = None,
    trust_tier_agent: TrustTierAgent = None,
    verification_agent: VerificationAgent = None,
    sentiment_agent: SentimentAgent = None,
    aggregator_agent: AggregatorVerdictAgent = None,
):
    """
    Constructs and compiles the MarketVerify LangGraph workflow.
    """
    # Instantiate agents if not passed (allows injection of mock agents in unit tests)
    normalizer = normalizer_agent or IngestionNormalizerAgent()
    trust_tier = trust_tier_agent or TrustTierAgent()
    verification = verification_agent or VerificationAgent()
    sentiment = sentiment_agent or SentimentAgent()
    aggregator = aggregator_agent or AggregatorVerdictAgent()

    builder = StateGraph(AgentState)

    # 1. Add agent nodes
    builder.add_node("normalizer", normalizer)
    builder.add_node("trust_tier", trust_tier)
    builder.add_node("trust_eval_router", route_after_trust)
    builder.add_node("verification", verification)
    builder.add_node("sentiment", sentiment)
    builder.add_node("aggregator", aggregator)

    # 2. Add sequential and conditional edges
    builder.add_edge(START, "normalizer")
    builder.add_edge("normalizer", "trust_tier")
    builder.add_edge("trust_tier", "trust_eval_router")
    builder.add_edge("trust_eval_router", "verification")

    # Conditional edge after Verification: loop-back or proceed to sentiment
    builder.add_conditional_edges(
        "verification",
        should_loop_back_verification,
        {
            "verification": "verification",
            "sentiment": "sentiment",
        },
    )

    builder.add_edge("sentiment", "aggregator")
    builder.add_edge("aggregator", END)

    compiled_graph = builder.compile()
    return compiled_graph
