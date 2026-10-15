from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import EmployerApplication, ReviewStatus
from app.schemas import EmployerApplicationIn, EmployerApplicationOut

router = APIRouter(prefix="/employer-applications", tags=["employer applications"])


@router.post("", response_model=EmployerApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(payload: EmployerApplicationIn, user: CurrentUser, db: DbSession):
    if not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Сначала подтвердите email")
    previous = db.scalar(select(EmployerApplication).where(EmployerApplication.user_id == user.id))
    if previous and previous.status in {ReviewStatus.pending, ReviewStatus.under_review, ReviewStatus.approved}:
        raise HTTPException(status_code=409, detail="Заявка уже существует")
    if previous:
        db.delete(previous)
        db.flush()
    application = EmployerApplication(user_id=user.id, **payload.model_dump(mode="json"))
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/me", response_model=EmployerApplicationOut)
def my_application(user: CurrentUser, db: DbSession):
    application = db.scalar(select(EmployerApplication).where(EmployerApplication.user_id == user.id))
    if not application:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    return application
