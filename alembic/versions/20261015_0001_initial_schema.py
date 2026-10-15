"""initial IMKON schema

Revision ID: 20261015_0001
Revises:
Create Date: 2026-10-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20261015_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = sa.Enum("seeker", "employer", "admin", name="user_role")
    employer_kind = sa.Enum("company", "individual", name="employer_kind")
    employer_profile_kind = sa.Enum("company", "individual", name="employer_profile_kind")
    review_status = sa.Enum("pending", "under_review", "approved", "rejected", name="review_status")
    vacancy_status = sa.Enum("draft", "pending", "approved", "rejected", "published", "closed", "expired", name="vacancy_status")
    application_status = sa.Enum("submitted", "viewed", "reviewing", "chatting", "offer", "accepted", "rejected", name="application_status")
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("email", sa.String(320), nullable=False, unique=True), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", user_role, nullable=False, server_default="seeker"), sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_table("email_verification_codes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("code_hash", sa.String(64), nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("used_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_email_verification_codes_user_id", "email_verification_codes", ["user_id"])
    op.create_table("refresh_sessions", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("token_hash", sa.String(64), nullable=False, unique=True), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("revoked_at", sa.DateTime(timezone=True)), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_refresh_sessions_user_id", "refresh_sessions", ["user_id"])
    op.create_table("seeker_profiles", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True), sa.Column("full_name", sa.String(200)), sa.Column("bio", sa.Text()), sa.Column("desired_position", sa.String(200)), sa.Column("schedule_preference", sa.String(100)), sa.Column("contact_preference", sa.String(100)), sa.Column("work_conditions", postgresql.JSONB(), nullable=False), sa.Column("skills", postgresql.JSONB(), nullable=False), sa.Column("languages", postgresql.JSONB(), nullable=False), sa.Column("portfolio_urls", postgresql.JSONB(), nullable=False))
    op.create_table("employer_applications", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True), sa.Column("kind", employer_kind, nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("country", sa.String(100), nullable=False), sa.Column("contact", sa.String(255), nullable=False), sa.Column("website", sa.String(500)), sa.Column("registration_details", sa.Text()), sa.Column("status", review_status, nullable=False, server_default="pending"), sa.Column("review_reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_employer_applications_status", "employer_applications", ["status"])
    op.create_table("employer_profiles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("owner_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True), sa.Column("kind", employer_profile_kind, nullable=False), sa.Column("name", sa.String(200), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("country", sa.String(100), nullable=False), sa.Column("contact", sa.String(255), nullable=False), sa.Column("website", sa.String(500)), sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_table("employer_members", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employer_profiles.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.UniqueConstraint("employer_id", "user_id"))
    op.create_index("ix_employer_members_employer_id", "employer_members", ["employer_id"])
    op.create_index("ix_employer_members_user_id", "employer_members", ["user_id"])
    op.create_table("resumes", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("summary", sa.Text()), sa.Column("experience", postgresql.JSONB(), nullable=False), sa.Column("skills", postgresql.JSONB(), nullable=False), sa.Column("education", postgresql.JSONB(), nullable=False), sa.Column("projects", postgresql.JSONB(), nullable=False), sa.Column("languages", postgresql.JSONB(), nullable=False), sa.Column("links", postgresql.JSONB(), nullable=False), sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("is_visible_to_employers", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("user_id", "is_primary", name="one_primary_resume_per_user"))
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])
    op.create_table("vacancies", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("employer_id", sa.Integer(), sa.ForeignKey("employer_profiles.id"), nullable=False), sa.Column("title", sa.String(250), nullable=False), sa.Column("description", sa.Text(), nullable=False), sa.Column("requirements", sa.Text()), sa.Column("responsibilities", sa.Text()), sa.Column("skills", postgresql.JSONB(), nullable=False), sa.Column("experience_level", sa.String(100)), sa.Column("schedule", sa.String(100)), sa.Column("salary_min", sa.Numeric(12, 2)), sa.Column("salary_max", sa.Numeric(12, 2)), sa.Column("currency", sa.String(3)), sa.Column("salary_negotiable", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("work_conditions", postgresql.JSONB(), nullable=False), sa.Column("work_language", sa.String(50)), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("status", vacancy_status, nullable=False, server_default="draft"), sa.Column("is_demo", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("rejection_reason", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.CheckConstraint("salary_min IS NULL OR salary_min >= 0", name="salary_min_nonnegative"))
    for column in ("employer_id", "title", "experience_level", "schedule", "currency", "work_language", "expires_at", "status"):
        op.create_index(f"ix_vacancies_{column}", "vacancies", [column])
    op.create_table("applications", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("vacancy_id", sa.Integer(), sa.ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("resume_id", sa.Integer(), sa.ForeignKey("resumes.id"), nullable=False), sa.Column("cover_letter", sa.Text()), sa.Column("status", application_status, nullable=False, server_default="submitted"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("vacancy_id", "user_id", name="one_application_per_vacancy_user"))
    for column in ("vacancy_id", "user_id", "status"):
        op.create_index(f"ix_applications_{column}", "applications", [column])


def downgrade() -> None:
    for table in ("applications", "vacancies", "resumes", "employer_members", "employer_profiles", "employer_applications", "seeker_profiles", "refresh_sessions", "email_verification_codes", "users"):
        op.drop_table(table)
    for enum in ("application_status", "vacancy_status", "review_status", "employer_profile_kind", "employer_kind", "user_role"):
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)
