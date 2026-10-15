from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models import EmployerMember, EmployerProfile, EmployerKind, Resume, User, UserRole, Vacancy, VacancyStatus


def main() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == "demo.seeker@imkon.example")):
            print("Demo data already exists")
            return
        seeker = User(email="demo.seeker@imkon.example", password_hash=hash_password("DemoPassword!2026"), is_email_verified=True)
        employer_user = User(email="demo.employer@imkon.example", password_hash=hash_password("DemoPassword!2026"), role=UserRole.employer, is_email_verified=True)
        db.add_all([seeker, employer_user])
        db.flush()
        employer = EmployerProfile(owner_user_id=employer_user.id, kind=EmployerKind.company, name="Northstar Demo Studio", description="Demonstration-only remote product studio.", country="Tajikistan", contact="demo.employer@imkon.example")
        db.add(employer)
        db.flush()
        db.add(EmployerMember(employer_id=employer.id, user_id=employer_user.id, role="owner"))
        resume = Resume(user_id=seeker.id, title="Junior Python Developer", summary="Учебное демонстрационное резюме.", skills=["Python", "FastAPI"], is_primary=True)
        vacancy = Vacancy(employer_id=employer.id, title="Python Developer", description="Демонстрационная вакансия удалённой постоянной работы.", skills=["Python", "SQL"], schedule="full-time", salary_min=800, salary_max=1200, currency="USD", expires_at=datetime.now(timezone.utc) + timedelta(days=30), status=VacancyStatus.published, is_demo=True)
        db.add_all([resume, vacancy])
        db.commit()
    print("Demo data loaded. Credentials are development-only and must not be used in production.")


if __name__ == "__main__":
    main()
