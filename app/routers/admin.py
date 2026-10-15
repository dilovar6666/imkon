from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.core.dependencies import AdminUser, DbSession
from app.models import EmployerApplication, EmployerMember, EmployerProfile, ReviewStatus, User, UserRole, Vacancy, VacancyStatus
from app.schemas import EmployerApplicationOut, Message, UserOut, VacancyOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=list[UserOut])
def list_users(_: AdminUser, db: DbSession, skip: int = 0, limit: int = 50):
    return list(db.scalars(select(User).order_by(User.created_at.desc()).offset(skip).limit(min(limit, 100))))


@router.patch("/users/{user_id}/block", response_model=Message)
def block_user(user_id: int, _: AdminUser, db: DbSession):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    if user.role == UserRole.admin:
        raise HTTPException(status_code=409, detail="Администратора нельзя заблокировать через этот endpoint")
    user.is_active = False
    db.commit()
    return Message(detail="Пользователь заблокирован")


@router.patch("/users/{user_id}/unblock", response_model=Message)
def unblock_user(user_id: int, _: AdminUser, db: DbSession):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.is_active = True
    db.commit()
    return Message(detail="Пользователь разблокирован")


@router.get("/employer-applications", response_model=list[EmployerApplicationOut])
def employer_applications(_: AdminUser, db: DbSession, review_status: ReviewStatus | None = None):
    stmt = select(EmployerApplication).order_by(EmployerApplication.created_at)
    if review_status:
        stmt = stmt.where(EmployerApplication.status == review_status)
    return list(db.scalars(stmt))


@router.post("/employer-applications/{application_id}/approve", response_model=EmployerApplicationOut)
def approve_employer(application_id: int, _: AdminUser, db: DbSession):
    application = db.get(EmployerApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if application.status == ReviewStatus.approved:
        raise HTTPException(status_code=409, detail="Заявка уже одобрена")
    employer = EmployerProfile(
        owner_user_id=application.user_id, kind=application.kind, name=application.name,
        description=application.description, country=application.country, contact=application.contact,
        website=application.website, is_verified=True,
    )
    db.add(employer)
    db.flush()
    db.add(EmployerMember(employer_id=employer.id, user_id=application.user_id, role="owner"))
    user = db.get(User, application.user_id)
    user.role = UserRole.employer
    application.status, application.review_reason = ReviewStatus.approved, None
    db.commit()
    db.refresh(application)
    return application


@router.post("/employer-applications/{application_id}/reject", response_model=EmployerApplicationOut)
def reject_employer(application_id: int, reason: str, _: AdminUser, db: DbSession):
    application = db.get(EmployerApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    if not reason.strip():
        raise HTTPException(status_code=422, detail="Укажите причину отклонения")
    application.status, application.review_reason = ReviewStatus.rejected, reason.strip()
    db.commit()
    db.refresh(application)
    return application


@router.get("/vacancies/pending", response_model=list[VacancyOut])
def pending_vacancies(_: AdminUser, db: DbSession):
    return list(db.scalars(select(Vacancy).where(Vacancy.status == VacancyStatus.pending).order_by(Vacancy.created_at)))


@router.post("/vacancies/{vacancy_id}/approve", response_model=VacancyOut)
def approve_vacancy(vacancy_id: int, _: AdminUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    if vacancy.status != VacancyStatus.pending:
        raise HTTPException(status_code=409, detail="На модерации должна быть только pending-вакансия")
    vacancy.status, vacancy.rejection_reason = VacancyStatus.published, None
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.post("/vacancies/{vacancy_id}/reject", response_model=VacancyOut)
def reject_vacancy(vacancy_id: int, reason: str, _: AdminUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    if vacancy.status != VacancyStatus.pending or not reason.strip():
        raise HTTPException(status_code=409, detail="Можно отклонить только pending-вакансию с причиной")
    vacancy.status, vacancy.rejection_reason = VacancyStatus.rejected, reason.strip()
    db.commit()
    db.refresh(vacancy)
    return vacancy


@router.post("/vacancies/{vacancy_id}/close", response_model=VacancyOut)
def close_vacancy(vacancy_id: int, _: AdminUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    vacancy.status = VacancyStatus.closed
    db.commit()
    db.refresh(vacancy)
    return vacancy
