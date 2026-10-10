"""Bound active scan/eval work across API workers."""
from alembic import op
import sqlalchemy as sa

revision = "a6d20261011"
down_revision = "a6d20261010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("work_reservations",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("org_id", sa.UUID(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("field", sa.String(), nullable=False),
        sa.Column("date", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False))
    op.create_index("ix_work_reservations_org_id", "work_reservations", ["org_id"])


def downgrade():
    op.drop_table("work_reservations")
