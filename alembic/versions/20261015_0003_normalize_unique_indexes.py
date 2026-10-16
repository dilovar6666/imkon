"""normalize unique indexes to match SQLAlchemy metadata

Revision ID: 20261015_0003
Revises: 20261015_0002
Create Date: 2026-10-15
"""

from alembic import op
import sqlalchemy as sa

revision = "20261015_0003"
down_revision = "20261015_0002"
branch_labels = None
depends_on = None


def _normalize_unique_index(table: str, column: str, constraint: str, index: str) -> None:
    inspector = sa.inspect(op.get_bind())
    indexes = {item["name"]: item for item in inspector.get_indexes(table)}
    constraints = {item["name"] for item in inspector.get_unique_constraints(table)}
    existing_index = indexes.get(index)

    if constraint in constraints:
        if existing_index:
            op.drop_index(index, table_name=table)
        op.drop_constraint(constraint, table, type_="unique")
        existing_index = None

    if not existing_index or not existing_index.get("unique"):
        if existing_index:
            op.drop_index(index, table_name=table)
        op.create_index(index, table, [column], unique=True)


def upgrade() -> None:
    _normalize_unique_index("users", "email", "uq_users_email", "ix_users_email")
    _normalize_unique_index(
        "employer_applications",
        "user_id",
        "uq_employer_applications_user_id",
        "ix_employer_applications_user_id",
    )
    _normalize_unique_index(
        "employer_profiles",
        "owner_user_id",
        "uq_employer_profiles_owner_user_id",
        "ix_employer_profiles_owner_user_id",
    )


def downgrade() -> None:
    # Downgrade keeps unique indexes because they enforce the same database invariant.
    pass
