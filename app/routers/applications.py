from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import CurrentUser, DbSession
from app.models import Application, ApplicationStatus, Resume, Vacancy, VacancyStatus
from app.routers.vacancies import assert_employer_member
from app.schemas import ApplicationIn, ApplicationOut, ApplicationStatusIn

router = APIRouter(prefix="/applications", tags=["applications"])

EMPLOYER_TRANSITIONS = {
    ApplicationStatus.submitted: {ApplicationStatus.viewed, ApplicationStatus.reviewing, ApplicationStatus.rejected},
    ApplicationStatus.viewed: {ApplicationStatus.reviewing, ApplicationStatus.chatting, ApplicationStatus.rejected},
    ApplicationStatus.reviewing: {ApplicationStatus.chatting, ApplicationStatus.offer, ApplicationStatus.rejected},
    ApplicationStatus.chatting: {ApplicationStatus.offer, ApplicationStatus.rejected},
    ApplicationStatus.offer: {ApplicationStatus.accepted, ApplicationStatus.rejected},
}


@router.post("/vacancies/{vacancy_id}", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def apply(vacancy_id: int, payload: ApplicationIn, user: CurrentUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy or vacancy.status != VacancyStatus.published:
        raise HTTPException(status_code=404, detail="Активная вакансия не найдена")
    resume = db.get(Resume, payload.resume_id)
    if not resume or resume.user_id != user.id:
        raise HTTPException(status_code=403, detail="Можно использовать только своё резюме")
    item = Application(vacancy_id=vacancy_id, user_id=user.id, **payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Отклик на эту вакансию уже отправлен")
    db.refresh(item)
    return item


@router.get("/me", response_model=list[ApplicationOut])
def my_applications(user: CurrentUser, db: DbSession):
    return list(db.scalars(select(Application).where(Application.user_id == user.id).order_by(Application.created_at.desc())))


@router.get("/vacancies/{vacancy_id}", response_model=list[ApplicationOut])
def vacancy_applications(vacancy_id: int, user: CurrentUser, db: DbSession):
    vacancy = db.get(Vacancy, vacancy_id)
    if not vacancy:
        raise HTTPException(status_code=404, detail="Вакансия не найдена")
    assert_employer_member(db, user.id, vacancy.employer_id)
    return list(db.scalars(select(Application).where(Application.vacancy_id == vacancy_id)))


@router.patch("/{application_id}/status", response_model=ApplicationOut)
def update_application_status(application_id: int, payload: ApplicationStatusIn, user: CurrentUser, db: DbSession):
    item = db.get(Application, application_id)
    if not item:
        raise HTTPException(status_code=404, detail="Отклик не найден")
    vacancy = db.get(Vacancy, item.vacancy_id)
    assert_employer_member(db, user.id, vacancy.employer_id)
    if payload.status not in EMPLOYER_TRANSITIONS.get(item.status, set()):
        raise HTTPException(status_code=409, detail="Недопустимый переход статуса")
    item.status = payload.status
    db.commit()
    db.refresh(item)
    return item
