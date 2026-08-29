"""Initial Schema Migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-08-29 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Claims Table
    op.create_table(
        "claims",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=10), nullable=False, server_default="en"),
        sa.Column("normalized_text", sa.Text(), nullable=True),
        sa.Column("ticker", sa.String(length=20), nullable=True),
        sa.Column("company_name", sa.String(length=255), nullable=True),
        sa.Column("source_handle", sa.String(length=100), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_claims_source_handle"), "claims", ["source_handle"], unique=False)
    op.create_index(op.f("ix_claims_ticker"), "claims", ["ticker"], unique=False)

    # 2. Verdicts Table
    op.create_table(
        "verdicts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("claim_id", sa.String(length=36), nullable=False),
        sa.Column("verdict_status", sa.String(length=50), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("trust_score", sa.Float(), nullable=False),
        sa.Column("trust_rationale", sa.Text(), nullable=True),
        sa.Column("verification_status", sa.String(length=50), nullable=False),
        sa.Column("citations", sa.JSON(), nullable=False),
        sa.Column("sentiment", sa.String(length=50), nullable=False),
        sa.Column("lead_lag_note", sa.Text(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("claim_id"),
    )

    # 3. Source Trajectories Table
    op.create_table(
        "source_trajectories",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("source_handle", sa.String(length=100), nullable=False),
        sa.Column("source_name", sa.String(length=255), nullable=True),
        sa.Column("past_claim_text", sa.Text(), nullable=False),
        sa.Column("ticker", sa.String(length=20), nullable=True),
        sa.Column("was_accurate", sa.Boolean(), nullable=False),
        sa.Column("lag_hours", sa.Integer(), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False, server_default="rumor"),
        sa.Column("outcome_summary", sa.Text(), nullable=False),
        sa.Column("outcome_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_source_trajectories_source_handle"), "source_trajectories", ["source_handle"], unique=False)
    op.create_index(op.f("ix_source_trajectories_ticker"), "source_trajectories", ["ticker"], unique=False)

    # 4. Agent Run Logs Table
    op.create_table(
        "agent_run_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("claim_id", sa.String(length=36), nullable=False),
        sa.Column("execution_trace", sa.JSON(), nullable=False),
        sa.Column("state_snapshot", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_agent_run_logs_claim_id"), "agent_run_logs", ["claim_id"], unique=False)


def downgrade() -> None:
    op.drop_table("agent_run_logs")
    op.drop_table("source_trajectories")
    op.drop_table("verdicts")
    op.drop_table("claims")
