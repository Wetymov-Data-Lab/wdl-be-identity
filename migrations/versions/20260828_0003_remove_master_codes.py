"""Remove master codes.

Revision ID: 20260828_0003
Revises: 20260828_0002
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str                       = "20260828_0003"
down_revision: str | None           = "20260828_0002"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None    = None


def upgrade() -> None:
    op.drop_table("master_codes")


def downgrade() -> None:
    op.create_table(
        "master_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", name="uq_master_codes_account_id"),
    )
