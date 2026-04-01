"""create published_covenant_reports table

Revision ID: 20260401_0001
Revises:
Create Date: 2026-04-01 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260401_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "published_covenant_reports",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("facility", sa.String(length=50), nullable=False),
        sa.Column("calculation_version", sa.String(length=20), nullable=False),
        sa.Column("normalized_payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("normalized_payload_hash", sa.String(length=64), nullable=False),
        sa.Column("effective_rate_percentage", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("threshold_percentage", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("covenant_status", sa.String(length=20), nullable=False),
        sa.Column("total_assets_evaluated", sa.Integer(), nullable=False),
        sa.Column("assets_included_count", sa.Integer(), nullable=False),
        sa.Column("assets_excluded_count", sa.Integer(), nullable=False),
        sa.Column("included_assets", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("excluded_assets", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "facility",
            "calculation_version",
            "normalized_payload_hash",
            name="uq_published_covenant_reports_facility_version_payload_hash",
        ),
    )


def downgrade() -> None:
    op.drop_table("published_covenant_reports")
