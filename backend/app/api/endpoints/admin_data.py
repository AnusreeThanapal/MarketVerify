import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.config import get_settings
from backend.app.core.logging import logger
from backend.app.core.database import get_db
from backend.app.core.qdrant_client import get_qdrant_service
from backend.app.models.user import User, UserRole
from backend.app.models.claim import Claim
from backend.app.models.agent_run_log import AgentRunLog
from backend.app.schemas.user import (
    UserRead,
    RawClaimRecord,
    RawAgentRunRecord,
    RawQdrantDocRecord,
)
from backend.app.api.deps import require_roles

settings = get_settings()

router = APIRouter(
    prefix="/admin/data",
    tags=["Admin Data Explorer"],
    dependencies=[Depends(require_roles([UserRole.ADMINISTRATOR, UserRole.AUDITOR]))],
)


@router.get(
    "/users",
    summary="List Users (Raw Database Inspection)",
    description="Returns paginated users from Postgres. Excludes password hashes.",
)
async def list_raw_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    query = select(User)
    if search:
        s = f"%{search.strip().lower()}%"
        query = query.where(User.email.ilike(s) | User.full_name.ilike(s))

    count_query = select(func.count(User.id))
    if search:
        s = f"%{search.strip().lower()}%"
        count_query = count_query.where(User.email.ilike(s) | User.full_name.ilike(s))

    total_res = await db.execute(count_query)
    total = total_res.scalar_one()

    query = query.order_by(desc(User.created_at)).offset(skip).limit(limit)
    res = await db.execute(query)
    users = res.scalars().all()

    items = [
        UserRead(
            id=u.id,
            email=u.email,
            full_name=u.full_name,
            role=u.role,
            is_active=u.is_active,
            created_at=u.created_at,
        ).model_dump()
        for u in users
    ]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get(
    "/claims",
    summary="List Raw Claims Records",
    description="Returns raw database rows from claims table with pagination and ticker/source filter.",
)
async def list_raw_claims(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    ticker: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    query = select(Claim)
    if ticker:
        query = query.where(Claim.ticker == ticker.upper())
    if search:
        s = f"%{search.strip()}%"
        query = query.where(Claim.raw_text.ilike(s) | Claim.source_handle.ilike(s))

    count_query = select(func.count(Claim.id))
    if ticker:
        count_query = count_query.where(Claim.ticker == ticker.upper())
    if search:
        s = f"%{search.strip()}%"
        count_query = count_query.where(Claim.raw_text.ilike(s) | Claim.source_handle.ilike(s))

    total_res = await db.execute(count_query)
    total = total_res.scalar_one()

    query = query.order_by(desc(Claim.submitted_at)).offset(skip).limit(limit)
    res = await db.execute(query)
    claims = res.scalars().all()

    items = [
        RawClaimRecord(
            id=c.id,
            raw_text=c.raw_text,
            language=c.language,
            normalized_text=c.normalized_text,
            ticker=c.ticker,
            company_name=c.company_name,
            source_handle=c.source_handle,
            submitted_at=c.submitted_at,
            status=c.status.value if hasattr(c.status, "value") else str(c.status),
        ).model_dump()
        for c in claims
    ]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get(
    "/agent-runs",
    summary="List Raw Agent Run Logs",
    description="Returns raw agent execution logs with full step traces and state snapshots.",
)
async def list_raw_agent_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    claim_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    query = select(AgentRunLog)
    if claim_id:
        query = query.where(AgentRunLog.claim_id == claim_id)

    count_query = select(func.count(AgentRunLog.id))
    if claim_id:
        count_query = count_query.where(AgentRunLog.claim_id == claim_id)

    total_res = await db.execute(count_query)
    total = total_res.scalar_one()

    query = query.order_by(desc(AgentRunLog.created_at)).offset(skip).limit(limit)
    res = await db.execute(query)
    runs = res.scalars().all()

    items = [
        RawAgentRunRecord(
            id=r.id,
            claim_id=r.claim_id,
            execution_trace=r.execution_trace or [],
            state_snapshot=r.state_snapshot or {},
            created_at=r.created_at,
        ).model_dump()
        for r in runs
    ]

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


def _fetch_qdrant_points(collection_name: str, limit: int = 50, search: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        client = get_qdrant_service().get_sync_client()
        if hasattr(client, "scroll"):
            records, _ = client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            results = []
            for r in records:
                payload = r.payload or {}
                text = (
                    payload.get("filing_text")
                    or payload.get("past_claim_text")
                    or payload.get("text_sample")
                    or str(payload)
                )
                if search and search.lower() not in text.lower() and search.lower() not in str(payload).lower():
                    continue

                results.append({
                    "id": str(r.id),
                    "collection_name": collection_name,
                    "payload": payload,
                    "text_snippet": text[:300] + ("..." if len(text) > 300 else ""),
                })
            if results:
                return results
    except Exception as e:
        logger.debug(f"Direct Qdrant scroll unavailable ({e}), using seed json fallback.")

    # Fallback to seed json files if Qdrant lock is held by another running process
    import json
    from pathlib import Path
    file_map = {
        settings.QDRANT_COLLECTION_TRUST: "seed_trust_tier.json",
        settings.QDRANT_COLLECTION_FILING: "seed_filings.json",
        settings.QDRANT_COLLECTION_SENTIMENT: "seed_sentiment.json",
    }
    filename = file_map.get(collection_name)
    if filename:
        seed_path = os.path.join(Path(__file__).parent.parent.parent, "data", filename)
        if os.path.exists(seed_path):
            with open(seed_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            results = []
            for item in data[:limit]:
                text = (
                    item.get("filing_text")
                    or item.get("past_claim_text")
                    or item.get("text_sample")
                    or str(item)
                )
                if search and search.lower() not in text.lower() and search.lower() not in str(item).lower():
                    continue
                results.append({
                    "id": str(item.get("id", item.get("doc_id", "doc"))),
                    "collection_name": collection_name,
                    "payload": item,
                    "text_snippet": text[:300] + ("..." if len(text) > 300 else ""),
                })
            return results
    return []


@router.get(
    "/trust-tier-docs",
    summary="List Raw Trust Tier Vector Store Documents",
    description="Inspects source trajectory documents and Bayesian metadata stored in trust_tier_store.",
)
async def list_trust_tier_docs(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
) -> Dict[str, Any]:
    docs = _fetch_qdrant_points(settings.QDRANT_COLLECTION_TRUST, limit=limit, search=search)
    return {
        "collection": settings.QDRANT_COLLECTION_TRUST,
        "total": len(docs),
        "items": docs,
    }


@router.get(
    "/filing-docs",
    summary="List Raw Regulatory Filings Vector Store Documents",
    description="Inspects SEBI/BSE regulatory filings stored in filing_store.",
)
async def list_filing_docs(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
) -> Dict[str, Any]:
    docs = _fetch_qdrant_points(settings.QDRANT_COLLECTION_FILING, limit=limit, search=search)
    return {
        "collection": settings.QDRANT_COLLECTION_FILING,
        "total": len(docs),
        "items": docs,
    }


@router.get(
    "/sentiment-docs",
    summary="List Raw Sentiment Corpus Vector Store Documents",
    description="Inspects multilingual (English/Tamil) market sentiment and lead-lag labeled samples.",
)
async def list_sentiment_docs(
    limit: int = Query(50, ge=1, le=200),
    search: Optional[str] = Query(None),
) -> Dict[str, Any]:
    docs = _fetch_qdrant_points(settings.QDRANT_COLLECTION_SENTIMENT, limit=limit, search=search)
    return {
        "collection": settings.QDRANT_COLLECTION_SENTIMENT,
        "total": len(docs),
        "items": docs,
    }
