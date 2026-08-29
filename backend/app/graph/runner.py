import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
import uuid
from datetime import datetime, timezone
from backend.app.agents.state import AgentState
from backend.app.graph.builder import create_marketverify_graph
from backend.app.services.trace_publisher import get_trace_publisher
from backend.app.core.logging import logger

graph_instance = create_marketverify_graph()

def get_marketverify_graph():
    return graph_instance


async def run_marketverify_workflow(
    raw_text: str,
    source_handle: str,
    language: Optional[str] = None,
    ticker: Optional[str] = None,
    claim_id: Optional[str] = None,
    publish_live_steps: bool = True,
) -> Dict[str, Any]:
    """
    Executes the multi-agent graph workflow and streams step events to Redis pub/sub.
    """
    c_id = claim_id or str(uuid.uuid4())
    logger.info(f"Initiating MarketVerify workflow for claim_id={c_id}, source={source_handle}")
    publisher = get_trace_publisher()

    initial_state: AgentState = {
        "claim_id": c_id,
        "raw_text": raw_text,
        "source_handle": source_handle,
        "language": language or "",
        "normalized_text": "",
        "ticker": ticker,
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

    graph = get_marketverify_graph()
    accumulated_state = dict(initial_state)
    last_trace_len = 0

    try:
        # Use astream to intercept intermediate node execution in real-time
        async for chunk in graph.astream(initial_state):
            for node_name, node_update in chunk.items():
                logger.debug(f"[Graph Stream] Node completed: {node_name}")
                if isinstance(node_update, dict):
                    accumulated_state.update(node_update)
                    
                    # Check if new trace entry was added
                    current_trace = accumulated_state.get("trace", [])
                    if len(current_trace) > last_trace_len and publish_live_steps:
                        for step in current_trace[last_trace_len:]:
                            await publisher.publish_step(c_id, step)
                            # Micro delay to allow realistic visual cadence on frontend
                            await asyncio.sleep(0.3)
                        last_trace_len = len(current_trace)

        logger.info(
            f"MarketVerify workflow finished for {c_id}: Verdict={accumulated_state.get('final_verdict')}, Steps={len(accumulated_state.get('trace', []))}"
        )
        return accumulated_state

    except Exception as e:
        logger.error(f"Error during workflow streaming for {c_id}: {e}", exc_info=True)
        fallback_trace = list(accumulated_state.get("trace", []))
        fallback_trace.append({
            "agent": "SystemError",
            "step_index": len(fallback_trace) + 1,
            "input_summary": f"Execution halted: {str(e)}",
            "retrieved_doc_ids": [],
            "retrieved_docs_preview": [],
            "output_summary": "Encountered unhandled execution exception.",
            "metadata": {"error": str(e)},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        accumulated_state["trace"] = fallback_trace
        accumulated_state["final_verdict"] = "NO_EVIDENCE_FOUND"
        accumulated_state["final_explanation"] = f"Workflow halted due to error: {str(e)}"
        
        if publish_live_steps:
            await publisher.publish_step(c_id, fallback_trace[-1])

        return accumulated_state
