from fastapi import APIRouter
from sqlalchemy import select

from app.core.dependencies import CurrentUser, DbSession
from app.models import SeekerProfile
from app.schemas import ProfileUpdate, UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return user


@router.patch("/me/profile", response_model=UserOut)
def update_profile(payload: ProfileUpdate, user: CurrentUser, db: DbSession):
    profile = db.get(SeekerProfile, user.id)
    if not profile:
        profile = SeekerProfile(user_id=user.id)
        db.add(profile)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)
    db.commit()
    db.refresh(user)
    return user
