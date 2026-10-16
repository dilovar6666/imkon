import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserRole(str, enum.Enum):
    seeker = "seeker"
    employer = "employer"
    admin = "admin"


class EmployerKind(str, enum.Enum):
    company = "company"
    individual = "individual"


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    under_review = "under_review"
    approved = "approved"
    rejected = "rejected"


class VacancyStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    published = "published"
    closed = "closed"
    expired = "expired"


class ApplicationStatus(str, enum.Enum):
    submitted = "submitted"
    viewed = "viewed"
    reviewing = "reviewing"
    chatting = "chatting"
    offer = "offer"
    accepted = "accepted"
    rejected = "rejected"


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), default=UserRole.seeker)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    profile: Mapped["SeekerProfile | None"] = relationship(back_populates="user", cascade="all, delete-orphan", uselist=False)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class GoogleIdentity(Base):
    __tablename__ = "google_identities"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True)
    subject: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EmailVerificationCode(Base):
    __tablename__ = "email_verification_codes"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class RefreshSession(Base):
    __tablename__ = "refresh_sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SeekerProfile(Base):
    __tablename__ = "seeker_profiles"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    full_name: Mapped[str | None] = mapped_column(String(200))
    bio: Mapped[str | None] = mapped_column(Text)
    desired_position: Mapped[str | None] = mapped_column(String(200))
    schedule_preference: Mapped[str | None] = mapped_column(String(100))
    contact_preference: Mapped[str | None] = mapped_column(String(100))
    work_conditions: Mapped[list] = mapped_column(JSONB, default=list)
    skills: Mapped[list] = mapped_column(JSONB, default=list)
    languages: Mapped[list] = mapped_column(JSONB, default=list)
    portfolio_urls: Mapped[list] = mapped_column(JSONB, default=list)
    user: Mapped[User] = relationship(back_populates="profile")


class EmployerApplication(Base):
    __tablename__ = "employer_applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    kind: Mapped[EmployerKind] = mapped_column(Enum(EmployerKind, name="employer_kind"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    country: Mapped[str] = mapped_column(String(100))
    contact: Mapped[str] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(500))
    registration_details: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus, name="review_status"), default=ReviewStatus.pending, index=True)
    review_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class EmployerProfile(Base):
    __tablename__ = "employer_profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    kind: Mapped[EmployerKind] = mapped_column(Enum(EmployerKind, name="employer_profile_kind"))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    country: Mapped[str] = mapped_column(String(100))
    contact: Mapped[str] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(500))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    members: Mapped[list["EmployerMember"]] = relationship(back_populates="employer", cascade="all, delete-orphan")


class EmployerMember(Base):
    __tablename__ = "employer_members"
    __table_args__ = (UniqueConstraint("employer_id", "user_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("employer_profiles.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # owner or hr_manager
    employer: Mapped[EmployerProfile] = relationship(back_populates="members")


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (UniqueConstraint("user_id", "is_primary", name="one_primary_resume_per_user"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str | None] = mapped_column(Text)
    experience: Mapped[list] = mapped_column(JSONB, default=list)
    skills: Mapped[list] = mapped_column(JSONB, default=list)
    education: Mapped[list] = mapped_column(JSONB, default=list)
    projects: Mapped[list] = mapped_column(JSONB, default=list)
    languages: Mapped[list] = mapped_column(JSONB, default=list)
    links: Mapped[list] = mapped_column(JSONB, default=list)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)
    is_visible_to_employers: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    user: Mapped[User] = relationship(back_populates="resumes")


class Vacancy(Base):
    __tablename__ = "vacancies"
    __table_args__ = (
        CheckConstraint("salary_min IS NULL OR salary_min >= 0", name="salary_min_nonnegative"),
        CheckConstraint("salary_min IS NULL OR salary_max IS NULL OR salary_max >= salary_min", name="salary_range_valid"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("employer_profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(250), index=True)
    description: Mapped[str] = mapped_column(Text)
    requirements: Mapped[str | None] = mapped_column(Text)
    responsibilities: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[list] = mapped_column(JSONB, default=list)
    experience_level: Mapped[str | None] = mapped_column(String(100), index=True)
    schedule: Mapped[str | None] = mapped_column(String(100), index=True)
    salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str | None] = mapped_column(String(3), index=True)
    salary_negotiable: Mapped[bool] = mapped_column(Boolean, default=False)
    work_conditions: Mapped[list] = mapped_column(JSONB, default=list)
    work_language: Mapped[str | None] = mapped_column(String(50), index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[VacancyStatus] = mapped_column(Enum(VacancyStatus, name="vacancy_status"), default=VacancyStatus.draft, index=True)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("vacancy_id", "user_id", name="one_application_per_vacancy_user"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancies.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    cover_letter: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ApplicationStatus] = mapped_column(Enum(ApplicationStatus, name="application_status"), default=ApplicationStatus.submitted, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
