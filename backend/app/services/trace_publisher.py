from typing import Dict, Any
from backend.app.config import get_settings
from backend.app.core.redis_client import get_redis
from backend.app.core.logging import logger

settings = get_settings()


class TracePublisher:
    """
    Publishes real-time agent trace events to Redis Pub/Sub channels
    ready for frontend WebSocket/SSE streaming.
    """

    async def publish_step(self, claim_id: str, trace_entry: Dict[str, Any]):
        redis = await get_redis()
        channel = f"{settings.REDIS_STREAM_CHANNEL}:{claim_id}"
        message = {
            "claim_id": claim_id,
            "event": "trace_step",
            "data": trace_entry,
        }
        await redis.publish(channel, message)
        logger.debug(f"[TracePublisher] Published step for claim {claim_id} to {channel}")

    async def publish_completion(self, claim_id: str, final_verdict: str, confidence: float):
        redis = await get_redis()
        channel = f"{settings.REDIS_STREAM_CHANNEL}:{claim_id}"
        message = {
            "claim_id": claim_id,
            "event": "workflow_completed",
            "data": {
                "verdict": final_verdict,
                "confidence": confidence,
            },
        }
        await redis.publish(channel, message)
        logger.debug(f"[TracePublisher] Published workflow completion for claim {claim_id}")


trace_publisher = TracePublisher()

def get_trace_publisher() -> TracePublisher:
    return trace_publisher
