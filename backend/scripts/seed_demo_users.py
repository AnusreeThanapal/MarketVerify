"""
Idempotent seeding script for MarketVerify Demo Accounts & Sample Claims.

DEMO CREDENTIALS NOTICE:
The accounts created by this script are DEMO-ONLY and intended solely for local
evaluation and demonstration. NEVER deploy these default passwords in production.
Rotate or remove demo users before deploying publicly.
"""
import os
import sys
import asyncio
from datetime import datetime, timezone
import uuid

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy import select
from backend.app.core.database import AsyncSessionLocal, engine, Base
from backend.app.models.user import User, UserRole
from backend.app.models.claim import Claim, ClaimStatus
from backend.app.models.verdict import Verdict, VerdictStatus, SentimentLabel
from backend.app.models.agent_run_log import AgentRunLog
from backend.app.core.security import get_password_hash
from backend.app.core.logging import logger

DEMO_USERS_SPEC = [
    {
        "email": "analyst.demo@marketverify.app",
        "full_name": "Surveillance Analyst (Market Intelligence)",
        "role": UserRole.ANALYST,
        "password": "Analyst@Demo123",
        "scope": "Submit claims, inspect live multi-agent traces, view citations and dashboard ledger.",
    },
    {
        "email": "compliance.demo@marketverify.app",
        "full_name": "Chief Compliance Officer (Surveillance Desk)",
        "role": UserRole.COMPLIANCE_OFFICER,
        "password": "Compliance@Demo123",
        "scope": "Analyst capabilities plus source credibility surveillance and compliance review docket.",
    },
    {
        "email": "admin.demo@marketverify.app",
        "full_name": "Platform Administrator (System Ops)",
        "role": UserRole.ADMINISTRATOR,
        "password": "Admin@Demo123",
        "scope": "Full administrative access plus Backend Data Explorer for raw store inspection.",
    },
    {
        "email": "auditor.demo@marketverify.app",
        "full_name": "External Regulatory Auditor (Read-Only Inspection)",
        "role": UserRole.AUDITOR,
        "password": "Auditor@Demo123",
        "scope": "Read-only oversight: inspect verdicts, traces, and Data Explorer (mutation buttons omitted).",
    },
]


def write_local_credentials_file():
    """Writes DEMO_CREDENTIALS.local.md at repository root."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cred_file_path = os.path.join(repo_root, "DEMO_CREDENTIALS.local.md")

    content = [
        "# MarketVerify — Local Demo Credentials",
        "",
        "> [!IMPORTANT]",
        "> **SECURITY NOTICE**: These accounts are generated strictly for local evaluation and demonstration.",
        "> They are backed by real bcrypt password hashes in PostgreSQL/SQLite.",
        "> **NEVER COMMIT THIS FILE OR DEPLOY THESE DEFAULT CREDENTIALS IN PRODUCTION.**",
        "",
        "| Surveillance Role | Official Email | Password | Oversight Scope |",
        "| :--- | :--- | :--- | :--- |",
    ]

    for u in DEMO_USERS_SPEC:
        content.append(
            f"| **{u['role'].value.replace('_', ' ')}** | `{u['email']}` | `{u['password']}` | {u['scope']} |"
        )

    content.extend([
        "",
        "## Usage",
        "- **Sign In**: Navigate to `http://localhost:3005`.",
        "- **1-Click Demo Login**: Click any demo role button on the sign-in page to authenticate instantly.",
        "- **Manual Login**: Enter the email and password from the table above.",
        "",
        f"*Generated automatically on: {datetime.now(timezone.utc).isoformat()}*",
    ])

    with open(cred_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))

    logger.info(f"Wrote local credentials reference to {cred_file_path}")


async def seed_demo_users_and_claims():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Seed Users idempotently
        created_count = 0
        for spec in DEMO_USERS_SPEC:
            res = await session.execute(select(User).where(User.email == spec["email"]))
            existing = res.scalar_one_or_none()
            if not existing:
                user = User(
                    id=str(uuid.uuid4()),
                    email=spec["email"],
                    full_name=spec["full_name"],
                    role=spec["role"],
                    hashed_password=get_password_hash(spec["password"]),
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(user)
                created_count += 1
            else:
                # Update role and password if needed to guarantee sync
                existing.role = spec["role"]
                existing.full_name = spec["full_name"]
                existing.hashed_password = get_password_hash(spec["password"])

        await session.commit()
        logger.info(f"Demo Users Seeding: {created_count} new accounts created, all 4 accounts active.")

        # 2. Write local credentials file
        try:
            write_local_credentials_file()
        except Exception as e:
            logger.warning(f"Could not write DEMO_CREDENTIALS.local.md: {e}")

        # 3. Seed Initial Demonstration Claims if none exist
        claim_check = await session.execute(select(Claim))
        existing_claims = claim_check.scalars().all()
        if len(existing_claims) == 0:
            logger.info("Seeding initial demonstration claims...")
            # Claim 1: Corroborated Reliance Zepto
            c1_id = str(uuid.uuid4())
            claim1 = Claim(
                id=c1_id,
                raw_text="Reliance Retail Ventures executes agreement to acquire 40% strategic stake in quick-commerce platform Zepto for Rs 4,200 Cr.",
                language="en",
                normalized_text="Reliance Retail Ventures executes agreement to acquire 40% strategic stake in quick-commerce platform Zepto for Rs 4,200 Cr.",
                ticker="RELIANCE",
                company_name="Reliance Industries Limited",
                source_handle="@dalalstreetinsider",
                status=ClaimStatus.COMPLETED,
                submitted_at=datetime.now(timezone.utc),
            )
            v1 = Verdict(
                id=str(uuid.uuid4()),
                claim_id=c1_id,
                verdict_status=VerdictStatus.CORROBORATED_OFFICIAL,
                confidence_score=0.92,
                trust_score=0.80,
                trust_rationale="Source '@dalalstreetinsider' historical evaluation: 3/4 past claims confirmed accurate (75.0% raw accuracy). Calibrated Bayesian trust score: 0.80 with HIGH confidence level.",
                verification_status="CORROBORATED",
                citations=[
                    {
                        "doc_id": "SEBI-REL-2024-001",
                        "filing_type": "SEBI Reg 30 Disclosure - Corporate Action",
                        "filing_date": "2024-06-18",
                        "headline": "Reliance Retail Ventures executes agreement to acquire 40% strategic stake in Zepto quick-commerce",
                        "similarity_score": 0.94,
                        "snippet": "Pursuant to Regulation 30 of SEBI (LODR) Regulations 2015, Reliance Retail Ventures Limited (RRVL) has executed definitive transaction documents for subscribing to compulsory convertible preference shares representing 40% equity stake in Kiranakart Technologies Private Limited (Zepto).",
                        "source_url": "https://www.bseindia.com/xml-data/corpfiling/AttachLive/SEBI-REL-2024-001.pdf"
                    }
                ],
                sentiment=SentimentLabel.POSITIVE,
                lead_lag_note="Lead signal: M&A rumors in high-growth quick-commerce typically prompt 2-4% pre-announcement rally followed by consolidation upon deal pricing clarity.",
                explanation="VERIFIED TRUE: The claim regarding RELIANCE is corroborated by official regulatory filings. Citations include Reliance Retail Ventures executes agreement to acquire 40% strategic stake in Zepto quick-commerce (dated 2024-06-18). Source '@dalalstreetinsider' provided accurate intelligence (Trust Score: 0.80). Sentiment is POSITIVE.",
                created_at=datetime.now(timezone.utc),
            )
            session.add(claim1)
            session.add(v1)

            # Claim 2: Contradicted HDFC Bank CEO Resignation
            c2_id = str(uuid.uuid4())
            claim2 = Claim(
                id=c2_id,
                raw_text="HDFC Bank MD and CEO Sashidhar Jagdishan to unexpectedly resign ahead of Q2 results due to board discord.",
                language="en",
                normalized_text="HDFC Bank MD and CEO Sashidhar Jagdishan to unexpectedly resign ahead of Q2 results due to board discord.",
                ticker="HDFCBANK",
                company_name="HDFC Bank Limited",
                source_handle="@dalalstreetinsider",
                status=ClaimStatus.COMPLETED,
                submitted_at=datetime.now(timezone.utc),
            )
            v2 = Verdict(
                id=str(uuid.uuid4()),
                claim_id=c2_id,
                verdict_status=VerdictStatus.CONTRADICTED_BY_FILING,
                confidence_score=0.88,
                trust_score=0.80,
                trust_rationale="Source '@dalalstreetinsider' historical evaluation: 3/4 past claims confirmed accurate.",
                verification_status="CONTRADICTED",
                citations=[
                    {
                        "doc_id": "SEBI-HDFC-2024-001",
                        "filing_type": "Exchange Clarification - Key Managerial Personnel",
                        "filing_date": "2024-06-05",
                        "headline": "Rebuttal of speculative market rumors regarding Managing Director & CEO resignation",
                        "similarity_score": 0.89,
                        "snippet": "HDFC Bank strongly refutes malicious and unsubstantiated rumors circulating on messaging apps regarding the purported resignation of our Managing Director & CEO, Mr. Sashidhar Jagdishan.",
                        "source_url": "https://www.bseindia.com/xml-data/corpfiling/AttachLive/HDFC-CLAR-001.pdf"
                    }
                ],
                sentiment=SentimentLabel.NEGATIVE,
                lead_lag_note="Lead signal: Sudden management exit rumors trigger immediate 3-5% price drop; historically rebounds swiftly if debunked within 24 hours.",
                explanation="CONTRADICTED: Official regulatory clarification refutes this statement (Rebuttal of speculative market rumors regarding Managing Director & CEO resignation), contradicting source '@dalalstreetinsider'.",
                created_at=datetime.now(timezone.utc),
            )
            session.add(claim2)
            session.add(v2)

            await session.commit()
            logger.info("Seeded initial demonstration claims with full citations and verdicts.")


if __name__ == "__main__":
    asyncio.run(seed_demo_users_and_claims())
