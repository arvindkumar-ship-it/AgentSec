"""Bind captured payments to server-issued, single-use orders."""
from alembic import op
import sqlalchemy as sa
revision = "a6d20261012"
down_revision = "a6d20261011"
branch_labels = depends_on = None

def upgrade():
    op.create_table("billing_orders",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("org_id", sa.UUID(), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("plan_name", sa.String(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("currency", sa.String(), nullable=False),
        sa.Column("payment_id", sa.String(), unique=True, nullable=True),
        sa.Column("paid_at", sa.DateTime(), nullable=True))

def downgrade():
    op.drop_table("billing_orders")
