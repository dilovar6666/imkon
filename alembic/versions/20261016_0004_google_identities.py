"""add Google identities"""

from alembic import op
import sqlalchemy as sa

revision = "20261016_0004"
down_revision = "20261015_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "google_identities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("subject", sa.String(255), nullable=False, unique=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_google_identities_user_id", "google_identities", ["user_id"])
    op.create_index("ix_google_identities_subject", "google_identities", ["subject"])


def downgrade() -> None:
    op.drop_table("google_identities")
