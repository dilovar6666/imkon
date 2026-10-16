from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select

from app.core.dependencies import CurrentUser, DbSession
from app.models import EmployerMember, EmployerProfile, Vacancy, VacancyStatus
from app.schemas import VacancyIn, VacancyOut

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


def user_employer(db: DbSession, user_id: int) -> EmployerProfile | None:
    member = db.scalar(select(EmployerMember).where(EmployerMember.user_id == user_id))
    return db.get(EmployerProfile, member.employer_id) if member else None


def assert_employer_member(db: DbSession, user_id: int, employer_id: int) -> None:
    if not db.scalar(select(EmployerMember).where(EmployerMember.user_id == user_id, EmployerMember.employer_id == employer_id)):
        raise HTTPException(status_code=403, detail="Нет доступа к вакансии этой организации")


@router.get("", response_model=list[VacancyOut])
def list_vacancies(
    db: DbSession,
    query: str | None = None,
    salary_min: float | None = Query(default=None, ge=0),
    currency: str | None = None,
    schedule: str | None = None,
    experience_level: str | None = None,
    work_language: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    stmt = select(Vacancy).where(Vacancy.status == VacancyStatus.published, Vacancy.expires_at > datetime.now(timezone.utc))
    if query:
        like = f"%{query.strip()}%"
        stmt = stmt.where(or_(Vacancy.title.ilike(like), Vacancy.description.ilike(like)))
    if salary_min is not None:
        stmt = stmt.where(Vacancy.salary_max >= salary_min)
    for column, value in ((Vacancy.currency, currency), (Vacancy.schedule, schedule), (Vacancy.experience_level, experience_level), (Vacancy.work_language, work_language)):
        if value:
            stmt = stmt.where(column == value)
    return list(db.scalars(stmt.order_by(Vacancy.created_at.desc()).offset(skip).limit(limit)))


@router.get("/{vacancy_id}", response_model=VacancyOut)
def get_vacancy(vacancy_id: int, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy or vacancy.status != VacancyStatus.published or vacancy.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=404, detail="Активная вакансия не найдена")
    return vacancy


@router.post("", response_model=VacancyOut, status_code=status.HTTP_201_CREATED)
def create_vacancy(payload: VacancyIn, user: CurrentUser, db: DbSession):
    employer = user_employer(db, user.id)
    if not employer or not employer.is_verified:
        raise HTTPException(status_code=403, detail="Требуется подтверждённый статус работодателя")
    if payload.salary_max is not None and payload.salary_min is not None and payload.salary_max < payload.salary_min:
        raise HTTPException(status_code=422, detail="Максимальная зарплата не может быть меньше минимальной")
    vacancy = Vacancy(employer_id=employer.id, status=VacancyStatus.draft, **payload.model_dump())
    db.add(vacancy)
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.patch("/{vacancy_id}", response_model=VacancyOut)
def update_vacancy(vacancy_id: int, payload: VacancyIn, user: CurrentUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    assert_employer_member(db, user.id, vacancy.employer_id)
    if vacancy.status in {VacancyStatus.closed, VacancyStatus.expired}:
        raise HTTPException(status_code=409, detail="Закрытую вакансию нельзя редактировать")
    if payload.salary_max is not None and payload.salary_min is not None and payload.salary_max < payload.salary_min:
        raise HTTPException(status_code=422, detail="Максимальная зарплата не может быть меньше минимальной")
    for key, value in payload.model_dump().items():
        setattr(vacancy, key, value)
    if vacancy.status == VacancyStatus.published:
        vacancy.status = VacancyStatus.pending
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.post("/{vacancy_id}/submit", response_model=VacancyOut)
def submit_vacancy(vacancy_id: int, user: CurrentUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    assert_employer_member(db, user.id, vacancy.employer_id)
    if vacancy.status not in {VacancyStatus.draft, VacancyStatus.rejected}:
        raise HTTPException(status_code=409, detail="Вакансия уже направлена или неактивна")
    vacancy.status, vacancy.rejection_reason = VacancyStatus.pending, None
    db.commit()
    db.refresh(vacancy)
    return vacancy
