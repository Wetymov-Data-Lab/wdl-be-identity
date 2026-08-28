"""Expand identity profiles.

Revision ID: 20260828_0002
Revises: 20260828_0001
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str                       = "20260828_0002"
down_revision: str | None           = "20260828_0001"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None    = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("given_name", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("family_name", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("bio", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("job_title", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("organization", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("website_url", sa.Text(), nullable=True))
    op.add_column(
        "profiles",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )
    op.alter_column("profiles", "created_at", server_default=None)


def downgrade() -> None:
    op.drop_column("profiles", "created_at")
    op.drop_column("profiles", "website_url")
    op.drop_column("profiles", "organization")
    op.drop_column("profiles", "job_title")
    op.drop_column("profiles", "bio")
    op.drop_column("profiles", "family_name")
    op.drop_column("profiles", "given_name")
