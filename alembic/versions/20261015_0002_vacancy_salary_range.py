"""enforce valid vacancy salary ranges

Revision ID: 20261015_0002
Revises: 20261015_0001
Create Date: 2026-10-15
"""

from alembic import op

revision = "20261015_0002"
down_revision = "20261015_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_check_constraint(
        "salary_range_valid",
        "vacancies",
        "salary_min IS NULL OR salary_max IS NULL OR salary_max >= salary_min",
    )


def downgrade() -> None:
    op.drop_constraint("ck_vacancies_salary_range_valid", "vacancies", type_="check")
