from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.schemas.source import SourceTrustHistory
from backend.app.services.claim_service import ClaimService
from backend.app.api.deps import get_claim_service
from backend.app.core.logging import logger

router = APIRouter(prefix="/sources", tags=["Sources & Trust History"])


@router.get(
    "/{source_handle}/trust-history",
    response_model=SourceTrustHistory,
    summary="Get Source Trust History",
    description="Retrieves the historical trajectory, accuracy rate, and calibrated trust score for an author/channel handle.",
)
async def get_source_trust_history(
    source_handle: str,
    service: ClaimService = Depends(get_claim_service),
) -> SourceTrustHistory:
    try:
        history = await service.get_source_trust_history(source_handle)
        return history
    except Exception as e:
        logger.error(f"Error fetching trust history for {source_handle}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not retrieve trust history for source '{source_handle}': {str(e)}",
        )
