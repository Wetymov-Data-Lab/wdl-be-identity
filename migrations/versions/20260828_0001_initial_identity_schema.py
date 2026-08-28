"""Create the initial identity schema.

Revision ID: 20260828_0001
Revises:
Create Date: 2026-08-28
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str                       = "20260828_0001"
down_revision: str | None           = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None    = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("subject", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_2fa_enforced", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint("subject IN ('user', 'service')", name="ck_accounts_subject"),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'deactivated', 'suspended')",
            name="ck_accounts_status",
        ),
        sa.CheckConstraint("version >= 1", name="ck_accounts_version_positive"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("locale", sa.Text(), nullable=True),
        sa.Column("time_zone", sa.Text(), nullable=True),
        sa.Column("picture_url", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", name="uq_profiles_account_id"),
    )

    op.create_table(
        "passwords",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("hash", sa.Text(), nullable=False),
        sa.Column("set_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_passwords_version_positive"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", name="uq_passwords_account_id"),
    )

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

    op.create_table(
        "second_factors",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("secret", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_second_factors_account_id", "second_factors", ["account_id"])

    op.create_table(
        "recovery_codes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("hash", sa.Text(), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hash", name="uq_recovery_codes_hash"),
    )
    op.create_index("ix_recovery_codes_account_id", "recovery_codes", ["account_id"])

    op.create_table(
        "password_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("hash", sa.Text(), nullable=False),
        sa.Column("set_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_password_history_version_positive"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("account_id", "version", name="uq_password_history_account_id_version"),
    )
    op.create_index("ix_password_history_account_id", "password_history", ["account_id"])

    op.create_table(
        "identifiers",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=128), nullable=True),
        sa.Column("provider_user_id", sa.Text(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_public_contact", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("receive_notifications", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_identifiers_account_id", "identifiers", ["account_id"])
    op.create_index(
        "uq_identifiers_local_type_value",
        "identifiers",
        ["type", "value"],
        unique=True,
        postgresql_where=sa.text("provider IS NULL"),
    )
    op.create_index(
        "uq_identifiers_provider_user",
        "identifiers",
        ["provider", "provider_user_id"],
        unique=True,
        postgresql_where=sa.text("provider IS NOT NULL AND provider_user_id IS NOT NULL"),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("ip", sa.Text(), nullable=False),
        sa.Column("refresh_token_hash", sa.Text(), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_refreshed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("expires_at > created_at", name="ck_sessions_expiration_after_creation"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_token_hash", name="uq_sessions_refresh_token_hash"),
    )
    op.create_index("ix_sessions_account_id", "sessions", ["account_id"])
    op.create_index("ix_sessions_expires_at", "sessions", ["expires_at"])

def downgrade() -> None:
    op.drop_index("ix_sessions_expires_at", table_name="sessions")
    op.drop_index("ix_sessions_account_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("uq_identifiers_provider_user", table_name="identifiers")
    op.drop_index("uq_identifiers_local_type_value", table_name="identifiers")
    op.drop_index("ix_identifiers_account_id", table_name="identifiers")
    op.drop_table("identifiers")

    op.drop_index("ix_password_history_account_id", table_name="password_history")
    op.drop_table("password_history")

    op.drop_index("ix_recovery_codes_account_id", table_name="recovery_codes")
    op.drop_table("recovery_codes")

    op.drop_index("ix_second_factors_account_id", table_name="second_factors")
    op.drop_table("second_factors")

    op.drop_table("master_codes")
    op.drop_table("passwords")
    op.drop_table("profiles")

    op.drop_table("accounts")
