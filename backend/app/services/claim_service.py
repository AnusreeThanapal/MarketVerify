from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from backend.app.models.claim import Claim, ClaimStatus
from backend.app.models.verdict import Verdict, VerdictStatus, SentimentLabel
from backend.app.models.agent_run_log import AgentRunLog
from backend.app.models.source_trajectory import SourceTrajectory
from backend.app.schemas.claim import ClaimCreate, ClaimResponse, ClaimSummary, VerdictResponse, CitationItem
from backend.app.schemas.trace import TraceEntry
from backend.app.schemas.source import SourceTrustHistory, SourceTrajectoryItem
from backend.app.graph.runner import run_marketverify_workflow
from backend.app.services.trace_publisher import get_trace_publisher
from backend.app.core.logging import logger


class ClaimService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.publisher = get_trace_publisher()

    async def submit_and_verify_claim(self, payload: ClaimCreate) -> ClaimResponse:
        claim_id = str(uuid.uuid4())
        
        # 1. Create preliminary claim record in database
        claim = Claim(
            id=claim_id,
            raw_text=payload.raw_text,
            source_handle=payload.source_handle,
            language=payload.language or "en",
            ticker=payload.ticker.upper() if payload.ticker else None,
            status=ClaimStatus.PROCESSING,
            submitted_at=datetime.now(timezone.utc),
        )
        self.db.add(claim)
        await self.db.commit()
        await self.db.refresh(claim)

        # 2. Execute LangGraph multi-agent workflow
        try:
            workflow_state = await run_marketverify_workflow(
                raw_text=payload.raw_text,
                source_handle=payload.source_handle,
                language=payload.language,
                ticker=payload.ticker,
                claim_id=claim_id,
            )

            # Update Claim attributes extracted by normalizer
            claim.language = workflow_state.get("language", claim.language)
            claim.normalized_text = workflow_state.get("normalized_text", payload.raw_text)
            claim.ticker = workflow_state.get("ticker") or claim.ticker
            claim.company_name = workflow_state.get("company_name")
            claim.status = ClaimStatus.COMPLETED

            # 3. Create Verdict record
            raw_verdict = workflow_state.get("final_verdict", VerdictStatus.NO_EVIDENCE_FOUND.value)
            try:
                v_enum = VerdictStatus(raw_verdict)
            except ValueError:
                v_enum = VerdictStatus.NO_EVIDENCE_FOUND

            raw_sent = workflow_state.get("sentiment_label", SentimentLabel.NEUTRAL.value)
            try:
                s_enum = SentimentLabel(raw_sent)
            except ValueError:
                s_enum = SentimentLabel.NEUTRAL

            verdict = Verdict(
                id=str(uuid.uuid4()),
                claim_id=claim_id,
                verdict_status=v_enum,
                confidence_score=workflow_state.get("final_confidence", 0.5),
                trust_score=workflow_state.get("trust_score", 0.5),
                trust_rationale=workflow_state.get("trust_rationale", ""),
                verification_status=workflow_state.get("verification_status", "NO_EVIDENCE_FOUND"),
                citations=workflow_state.get("verification_citations", []),
                sentiment=s_enum,
                lead_lag_note=workflow_state.get("lead_lag_note", ""),
                explanation=workflow_state.get("final_explanation", "Analysis completed."),
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(verdict)

            # 4. Save Agent Run Execution Trace
            raw_trace = workflow_state.get("trace", [])
            run_log = AgentRunLog(
                id=str(uuid.uuid4()),
                claim_id=claim_id,
                execution_trace=raw_trace,
                state_snapshot={
                    k: v for k, v in workflow_state.items() if k not in ["trace"]
                },
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(run_log)

            await self.db.commit()
            await self.db.refresh(claim)
            await self.db.refresh(verdict)

            # 5. Publish completion event to Redis
            await self.publisher.publish_completion(
                claim_id, verdict.verdict_status.value, verdict.confidence_score
            )

            # Assemble response
            citations_models = [
                CitationItem(
                    doc_id=c.get("doc_id", ""),
                    filing_type=c.get("filing_type", ""),
                    filing_date=c.get("filing_date", ""),
                    headline=c.get("headline", ""),
                    similarity_score=c.get("similarity_score", 0.0),
                    snippet=c.get("snippet", ""),
                    source_url=c.get("source_url"),
                )
                for c in verdict.citations
            ]

            trace_models = [
                TraceEntry(
                    agent=t.get("agent", "Unknown"),
                    step_index=t.get("step_index", idx + 1),
                    input_summary=t.get("input_summary", ""),
                    retrieved_doc_ids=t.get("retrieved_doc_ids", []),
                    retrieved_docs_preview=t.get("retrieved_docs_preview", []),
                    output_summary=t.get("output_summary", ""),
                    metadata=t.get("metadata", {}),
                    timestamp=datetime.fromisoformat(t["timestamp"]) if isinstance(t.get("timestamp"), str) and t.get("timestamp") != "now" else datetime.now(timezone.utc),
                )
                for idx, t in enumerate(raw_trace)
            ]

            verdict_resp = VerdictResponse(
                id=verdict.id,
                claim_id=verdict.claim_id,
                verdict_status=verdict.verdict_status,
                confidence_score=verdict.confidence_score,
                trust_score=verdict.trust_score,
                trust_rationale=verdict.trust_rationale,
                verification_status=verdict.verification_status,
                citations=citations_models,
                sentiment=verdict.sentiment,
                lead_lag_note=verdict.lead_lag_note,
                explanation=verdict.explanation,
                created_at=verdict.created_at,
            )

            s_at = claim.submitted_at
            if s_at and s_at.tzinfo is None:
                s_at = s_at.replace(tzinfo=timezone.utc)

            return ClaimResponse(
                id=claim.id,
                raw_text=claim.raw_text,
                language=claim.language,
                normalized_text=claim.normalized_text,
                ticker=claim.ticker,
                company_name=claim.company_name,
                source_handle=claim.source_handle,
                submitted_at=s_at,
                status=claim.status,
                verdict=verdict_resp,
                trace=trace_models,
            )
        except Exception as e:
            logger.error(f"Error processing claim {claim_id}: {e}", exc_info=True)
            claim.status = ClaimStatus.FAILED
            await self.db.commit()
            raise

    async def start_streaming_claim(self, payload: ClaimCreate) -> Dict[str, Any]:
        claim_id = str(uuid.uuid4())
        
        # Insert initial Claim record
        claim = Claim(
            id=claim_id,
            raw_text=payload.raw_text,
            source_handle=payload.source_handle,
            language=payload.language or "en",
            ticker=payload.ticker.upper() if payload.ticker else None,
            status=ClaimStatus.PROCESSING,
            submitted_at=datetime.now(timezone.utc),
        )
        self.db.add(claim)
        await self.db.commit()
        await self.db.refresh(claim)

        return {
            "claim_id": claim_id,
            "status": "PROCESSING",
            "stream_url": f"/api/v1/claims/{claim_id}/stream",
        }

    async def execute_background_verification(self, claim_id: str, payload: ClaimCreate):
        """Asynchronous worker function that executes graph and persists DB state."""
        try:
            workflow_state = await run_marketverify_workflow(
                raw_text=payload.raw_text,
                source_handle=payload.source_handle,
                language=payload.language,
                ticker=payload.ticker,
                claim_id=claim_id,
                publish_live_steps=True,
            )

            # Query claim in new db session context if needed
            res = await self.db.execute(select(Claim).where(Claim.id == claim_id))
            claim = res.scalar_one_or_none()
            if not claim:
                return

            claim.language = workflow_state.get("language", claim.language)
            claim.normalized_text = workflow_state.get("normalized_text", payload.raw_text)
            claim.ticker = workflow_state.get("ticker") or claim.ticker
            claim.company_name = workflow_state.get("company_name")
            claim.status = ClaimStatus.COMPLETED

            raw_verdict = workflow_state.get("final_verdict", VerdictStatus.NO_EVIDENCE_FOUND.value)
            try:
                v_enum = VerdictStatus(raw_verdict)
            except ValueError:
                v_enum = VerdictStatus.NO_EVIDENCE_FOUND

            raw_sent = workflow_state.get("sentiment_label", SentimentLabel.NEUTRAL.value)
            try:
                s_enum = SentimentLabel(raw_sent)
            except ValueError:
                s_enum = SentimentLabel.NEUTRAL

            verdict = Verdict(
                id=str(uuid.uuid4()),
                claim_id=claim_id,
                verdict_status=v_enum,
                confidence_score=workflow_state.get("final_confidence", 0.5),
                trust_score=workflow_state.get("trust_score", 0.5),
                trust_rationale=workflow_state.get("trust_rationale", ""),
                verification_status=workflow_state.get("verification_status", "NO_EVIDENCE_FOUND"),
                citations=workflow_state.get("verification_citations", []),
                sentiment=s_enum,
                lead_lag_note=workflow_state.get("lead_lag_note", ""),
                explanation=workflow_state.get("final_explanation", "Analysis completed."),
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(verdict)

            raw_trace = workflow_state.get("trace", [])
            run_log = AgentRunLog(
                id=str(uuid.uuid4()),
                claim_id=claim_id,
                execution_trace=raw_trace,
                state_snapshot={
                    k: v for k, v in workflow_state.items() if k not in ["trace"]
                },
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(run_log)

            await self.db.commit()

            # Publish final completion payload with citations for frontend
            await self.publisher.publish_completion(
                claim_id, verdict.verdict_status.value, verdict.confidence_score
            )
        except Exception as e:
            logger.error(f"Error in execute_background_verification for {claim_id}: {e}", exc_info=True)
            res = await self.db.execute(select(Claim).where(Claim.id == claim_id))
            claim = res.scalar_one_or_none()
            if claim:
                claim.status = ClaimStatus.FAILED
                await self.db.commit()

    async def get_claim_by_id(self, claim_id: str) -> Optional[ClaimResponse]:
        query = (
            select(Claim)
            .where(Claim.id == claim_id)
            .options(
                selectinload(Claim.verdict),
                selectinload(Claim.run_logs),
            )
        )
        res = await self.db.execute(query)
        claim = res.scalar_one_or_none()
        if not claim:
            return None

        verdict_resp = None
        if claim.verdict:
            citations_models = [
                CitationItem(
                    doc_id=c.get("doc_id", ""),
                    filing_type=c.get("filing_type", ""),
                    filing_date=c.get("filing_date", ""),
                    headline=c.get("headline", ""),
                    similarity_score=c.get("similarity_score", 0.0),
                    snippet=c.get("snippet", ""),
                    source_url=c.get("source_url"),
                )
                for c in claim.verdict.citations
            ]
            verdict_resp = VerdictResponse(
                id=claim.verdict.id,
                claim_id=claim.verdict.claim_id,
                verdict_status=claim.verdict.verdict_status,
                confidence_score=claim.verdict.confidence_score,
                trust_score=claim.verdict.trust_score,
                trust_rationale=claim.verdict.trust_rationale,
                verification_status=claim.verdict.verification_status,
                citations=citations_models,
                sentiment=claim.verdict.sentiment,
                lead_lag_note=claim.verdict.lead_lag_note,
                explanation=claim.verdict.explanation,
                created_at=claim.verdict.created_at,
            )

        trace_models = []
        if claim.run_logs:
            latest_log = claim.run_logs[-1]
            for idx, t in enumerate(latest_log.execution_trace):
                ts = t.get("timestamp")
                ts_dt = datetime.now(timezone.utc)
                if isinstance(ts, str) and ts != "now":
                    try:
                        ts_dt = datetime.fromisoformat(ts)
                    except Exception:
                        pass
                trace_models.append(
                    TraceEntry(
                        agent=t.get("agent", "Unknown"),
                        step_index=t.get("step_index", idx + 1),
                        input_summary=t.get("input_summary", ""),
                        retrieved_doc_ids=t.get("retrieved_doc_ids", []),
                        retrieved_docs_preview=t.get("retrieved_docs_preview", []),
                        output_summary=t.get("output_summary", ""),
                        metadata=t.get("metadata", {}),
                        timestamp=ts_dt,
                    )
                )

        s_at = claim.submitted_at
        if s_at and s_at.tzinfo is None:
            s_at = s_at.replace(tzinfo=timezone.utc)

        return ClaimResponse(
            id=claim.id,
            raw_text=claim.raw_text,
            language=claim.language,
            normalized_text=claim.normalized_text,
            ticker=claim.ticker,
            company_name=claim.company_name,
            source_handle=claim.source_handle,
            submitted_at=s_at,
            status=claim.status,
            verdict=verdict_resp,
            trace=trace_models,
        )

    async def list_claims(
        self,
        page: int = 1,
        page_size: int = 20,
        ticker: Optional[str] = None,
        source_handle: Optional[str] = None,
    ) -> Tuple[List[ClaimSummary], int]:
        query = select(Claim).options(selectinload(Claim.verdict))
        
        if ticker:
            query = query.where(Claim.ticker == ticker.upper())
        if source_handle:
            query = query.where(Claim.source_handle == source_handle)

        # Count total
        count_query = select(func.count(Claim.id))
        if ticker:
            count_query = count_query.where(Claim.ticker == ticker.upper())
        if source_handle:
            count_query = count_query.where(Claim.source_handle == source_handle)

        total_res = await self.db.execute(count_query)
        total = total_res.scalar_one()

        # Paginate
        offset = (page - 1) * page_size
        query = query.order_by(desc(Claim.submitted_at)).offset(offset).limit(page_size)
        
        results = await self.db.execute(query)
        claims = results.scalars().all()

        items = []
        for c in claims:
            s_at = c.submitted_at
            if s_at and s_at.tzinfo is None:
                s_at = s_at.replace(tzinfo=timezone.utc)
            items.append(
                ClaimSummary(
                    id=c.id,
                    raw_text=c.raw_text,
                    language=c.language,
                    ticker=c.ticker,
                    company_name=c.company_name,
                    source_handle=c.source_handle,
                    submitted_at=s_at,
                    status=c.status,
                    verdict_status=c.verdict.verdict_status if c.verdict else None,
                    confidence_score=c.verdict.confidence_score if c.verdict else None,
                )
            )

        return items, total

    async def get_source_trust_history(self, source_handle: str) -> SourceTrustHistory:
        clean_handle = source_handle.lower()
        query = (
            select(SourceTrajectory)
            .where(func.lower(SourceTrajectory.source_handle) == clean_handle)
            .order_by(desc(SourceTrajectory.outcome_date))
        )
        res = await self.db.execute(query)
        trajectories = res.scalars().all()

        total = len(trajectories)
        accurate = sum(1 for t in trajectories if t.was_accurate)
        rate = (accurate / total) if total > 0 else 0.0
        
        # Bayesian trust calculation with prior
        trust_score = round((accurate + 1.0) / (total + 2.0), 3) if total > 0 else 0.35
        
        if total >= 3:
            conf = "HIGH" if trust_score >= 0.70 or trust_score <= 0.35 else "MEDIUM"
        elif total >= 1:
            conf = "MEDIUM"
        else:
            conf = "LOW"

        category_counts: Dict[str, int] = {}
        for t in trajectories:
            cat = t.category or "rumor"
            category_counts[cat] = category_counts.get(cat, 0) + 1

        items = [
            SourceTrajectoryItem(
                id=t.id,
                source_handle=t.source_handle,
                source_name=t.source_name,
                past_claim_text=t.past_claim_text,
                ticker=t.ticker,
                was_accurate=t.was_accurate,
                lag_hours=t.lag_hours,
                category=t.category,
                outcome_summary=t.outcome_summary,
                outcome_date=t.outcome_date,
                recorded_at=t.recorded_at,
            )
            for t in trajectories
        ]

        return SourceTrustHistory(
            source_handle=source_handle,
            total_claims_evaluated=total,
            accurate_claims_count=accurate,
            accuracy_rate=round(rate, 3),
            trust_score=trust_score,
            confidence_level=conf,
            category_breakdown=category_counts,
            recent_trajectories=items,
        )
