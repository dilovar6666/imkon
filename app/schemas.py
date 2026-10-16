from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from app.models import ApplicationStatus, EmployerKind, ReviewStatus, UserRole, VacancyStatus


class ModelSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Message(ModelSchema):
    detail: str


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class VerifyEmailIn(BaseModel):
    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class LoginIn(RegisterIn):
    pass


class RefreshIn(BaseModel):
    refresh_token: str


class GoogleTokenIn(BaseModel):
    id_token: str = Field(min_length=20, max_length=8192)


class TokenPair(ModelSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=200)
    bio: str | None = Field(default=None, max_length=4000)
    desired_position: str | None = Field(default=None, max_length=200)
    schedule_preference: str | None = Field(default=None, max_length=100)
    contact_preference: str | None = Field(default=None, max_length=100)
    work_conditions: list[str] | None = None
    skills: list[str] | None = None
    languages: list[str] | None = None
    portfolio_urls: list[str] | None = None


class SeekerProfileOut(ModelSchema):
    full_name: str | None
    bio: str | None
    desired_position: str | None
    schedule_preference: str | None
    contact_preference: str | None
    work_conditions: list
    skills: list
    languages: list
    portfolio_urls: list


class UserOut(ModelSchema):
    id: int
    email: str
    role: UserRole
    is_email_verified: bool
    is_active: bool
    created_at: datetime
    profile: SeekerProfileOut | None = None


class EmployerApplicationIn(BaseModel):
    kind: EmployerKind
    name: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=20, max_length=5000)
    country: str = Field(min_length=2, max_length=100)
    contact: str = Field(min_length=3, max_length=255)
    website: HttpUrl | None = None
    registration_details: str | None = Field(default=None, max_length=3000)


class EmployerApplicationOut(ModelSchema):
    id: int
    user_id: int
    kind: EmployerKind
    name: str
    description: str
    country: str
    contact: str
    website: str | None
    status: ReviewStatus
    review_reason: str | None
    created_at: datetime


class ResumeIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    summary: str | None = Field(default=None, max_length=5000)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    links: list[str] = Field(default_factory=list)
    is_visible_to_employers: bool = True


class ResumeOut(ResumeIn, ModelSchema):
    id: int
    user_id: int
    is_primary: bool
    updated_at: datetime


class VacancyIn(BaseModel):
    title: str = Field(min_length=2, max_length=250)
    description: str = Field(min_length=20, max_length=10000)
    requirements: str | None = Field(default=None, max_length=8000)
    responsibilities: str | None = Field(default=None, max_length=8000)
    skills: list[str] = Field(default_factory=list)
    experience_level: str | None = Field(default=None, max_length=100)
    schedule: str | None = Field(default=None, max_length=100)
    salary_min: float | None = Field(default=None, ge=0)
    salary_max: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    salary_negotiable: bool = False
    work_conditions: list[str] = Field(default_factory=list)
    work_language: str | None = Field(default=None, max_length=50)
    expires_at: datetime

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class VacancyOut(VacancyIn, ModelSchema):
    id: int
    employer_id: int
    status: VacancyStatus
    is_demo: bool
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime


class ApplicationIn(BaseModel):
    resume_id: int
    cover_letter: str | None = Field(default=None, max_length=5000)


class ApplicationStatusIn(BaseModel):
    status: ApplicationStatus


class ApplicationOut(ModelSchema):
    id: int
    vacancy_id: int
    user_id: int
    resume_id: int
    cover_letter: str | None
    status: ApplicationStatus
    created_at: datetime
