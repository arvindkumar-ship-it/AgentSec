"""Persist agent ownership independently of scan history."""
from alembic import op
import sqlalchemy as sa

revision = "a6d20261010"
down_revision = "45ebedcc8f19"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("agent_ownership",
        sa.Column("agent_id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.UUID(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime()))


def downgrade():
    op.drop_table("agent_ownership")
