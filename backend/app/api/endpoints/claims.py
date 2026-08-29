import asyncio
import json
from typing import Optional, AsyncGenerator
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from backend.app.schemas.claim import ClaimCreate, ClaimResponse, ClaimSummary
from backend.app.schemas.common import PaginatedResponse
from backend.app.services.claim_service import ClaimService
from backend.app.api.deps import get_claim_service
from backend.app.core.redis_client import get_redis
from backend.app.config import get_settings
from backend.app.core.logging import logger

router = APIRouter(prefix="/claims", tags=["Claims & Rumors"])
settings = get_settings()


@router.post(
    "",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit and Verify a Market Claim (Synchronous)",
    description="Submits a claim and returns the full verdict + execution trace upon completion.",
)
async def submit_claim(
    payload: ClaimCreate,
    service: ClaimService = Depends(get_claim_service),
) -> ClaimResponse:
    try:
        logger.info(f"Received synchronous claim submission from '{payload.source_handle}'")
        result = await service.submit_and_verify_claim(payload)
        return result
    except Exception as e:
        logger.error(f"Failed to process claim synchronously: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while verifying the claim: {str(e)}",
        )


@router.post(
    "/stream",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit Claim for Live SSE Streaming",
    description="Initializes claim in background and returns claim_id and stream_url for live SSE subscription.",
)
async def submit_claim_streaming(
    payload: ClaimCreate,
    background_tasks: BackgroundTasks,
    service: ClaimService = Depends(get_claim_service),
):
    init_res = await service.start_streaming_claim(payload)
    claim_id = init_res["claim_id"]

    # Launch LangGraph execution in background
    background_tasks.add_task(service.execute_background_verification, claim_id, payload)

    return init_res


@router.get(
    "/{claim_id}/stream",
    summary="Live SSE Stream for Agent Trace",
    description="Server-Sent Events endpoint streaming real-time trace steps as each agent completes.",
)
async def stream_claim_trace(
    claim_id: str,
    service: ClaimService = Depends(get_claim_service),
):
    # Verify claim exists
    claim = await service.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    async def sse_event_generator() -> AsyncGenerator[str, None]:
        redis_svc = await get_redis()
        channel_name = f"{settings.REDIS_STREAM_CHANNEL}:{claim_id}"

        # If claim is already completed, replay its trace immediately
        if claim.status.value == "COMPLETED" and claim.trace:
            for step in claim.trace:
                yield f"event: trace_step\ndata: {json.dumps(step.model_dump(mode='json'))}\n\n"
                await asyncio.sleep(0.05)
            if claim.verdict:
                yield f"event: completed\ndata: {json.dumps(claim.verdict.model_dump(mode='json'))}\n\n"
            return

        # If Redis is active, subscribe to pub/sub channel
        if redis_svc.client:
            pubsub = redis_svc.client.pubsub()
            await pubsub.subscribe(channel_name)
            try:
                # Set 45-second timeout for streaming graph completion
                for _ in range(90):
                    message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=0.5)
                    if message and message.get("data"):
                        data_str = message["data"]
                        try:
                            parsed = json.loads(data_str) if isinstance(data_str, str) else data_str
                            event_type = parsed.get("event", "trace_step")
                            payload_data = parsed.get("data", parsed)
                            yield f"event: {event_type}\ndata: {json.dumps(payload_data)}\n\n"
                            if event_type == "workflow_completed":
                                break
                        except Exception:
                            yield f"event: trace_step\ndata: {data_str}\n\n"
                    await asyncio.sleep(0.1)
            finally:
                await pubsub.unsubscribe(channel_name)
                await pubsub.close()
        else:
            # Redis offline fallback: poll claim from DB until completed
            for _ in range(30):
                updated_claim = await service.get_claim_by_id(claim_id)
                if updated_claim and updated_claim.status.value == "COMPLETED":
                    if updated_claim.trace:
                        for step in updated_claim.trace:
                            yield f"event: trace_step\ndata: {json.dumps(step.model_dump(mode='json'))}\n\n"
                    if updated_claim.verdict:
                        yield f"event: completed\ndata: {json.dumps(updated_claim.verdict.model_dump(mode='json'))}\n\n"
                    break
                await asyncio.sleep(0.5)

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/{claim_id}",
    response_model=ClaimResponse,
    summary="Get Claim by ID",
)
async def get_claim(
    claim_id: str,
    service: ClaimService = Depends(get_claim_service),
) -> ClaimResponse:
    claim = await service.get_claim_by_id(claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Claim with ID '{claim_id}' not found.",
        )
    return claim


@router.get(
    "",
    response_model=PaginatedResponse[ClaimSummary],
    summary="List Recent Claims",
)
async def list_claims(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ticker: Optional[str] = Query(None),
    source_handle: Optional[str] = Query(None),
    service: ClaimService = Depends(get_claim_service),
) -> PaginatedResponse[ClaimSummary]:
    items, total = await service.list_claims(
        page=page,
        page_size=page_size,
        ticker=ticker,
        source_handle=source_handle,
    )
    pages = (total + page_size - 1) // page_size if total > 0 else 0
    return PaginatedResponse[ClaimSummary](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )
