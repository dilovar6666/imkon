from fastapi import APIRouter, HTTPException, status

from app.core.dependencies import CurrentUser, DbSession
from app.models import Resume
from app.schemas import ResumeIn, ResumeOut

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("/me", response_model=ResumeOut)
def get_my_resume(user: CurrentUser, db: DbSession):
    resume = next((item for item in user.resumes if item.is_primary), None)
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    return resume


@router.post("", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def create_resume(payload: ResumeIn, user: CurrentUser, db: DbSession):
    if any(item.is_primary for item in user.resumes):
        raise HTTPException(status_code=409, detail="Основное резюме уже создано")
    resume = Resume(user_id=user.id, is_primary=True, **payload.model_dump())
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.patch("/me", response_model=ResumeOut)
def update_my_resume(payload: ResumeIn, user: CurrentUser, db: DbSession):
    resume = next((item for item in user.resumes if item.is_primary), None)
    if not resume:
        raise HTTPException(status_code=404, detail="Резюме не найдено")
    for key, value in payload.model_dump().items():
        setattr(resume, key, value)
    db.commit()
    db.refresh(resume)
    return resume
