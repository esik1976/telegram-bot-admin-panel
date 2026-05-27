"""add error resolved_at

Revision ID: 20260527_0002
Revises: 20260524_0001
Create Date: 2026-05-27
"""
from alembic import op
import sqlalchemy as sa


revision = "20260527_0002"
down_revision = "20260524_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "error_logs",
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("error_logs", "resolved_at")
