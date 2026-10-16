import os
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select


pytestmark = pytest.mark.skipif(not os.getenv("TEST_DATABASE_URL"), reason="TEST_DATABASE_URL is required")


def _register_and_verify(client: TestClient, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert response.status_code == 201, response.text
    code = response.json()["detail"].rsplit(": ", maxsplit=1)[1]
    response = client.post("/api/v1/auth/verify-email", json={"email": email, "code": code})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_postgresql_employment_flow():
    from app.core.database import SessionLocal
    from app.core.security import hash_password
    from app.main import app
    from app.models import User, UserRole, Vacancy

    suffix = uuid4().hex[:10]
    seeker_email = f"seeker-{suffix}@imkon-audit.com"
    employer_email = f"employer-{suffix}@imkon-audit.com"
    admin_email = f"admin-{suffix}@imkon-audit.com"
    password = "SecureTestPassword!2026"

    with SessionLocal() as db:
        db.add(User(email=admin_email, password_hash=hash_password(password), role=UserRole.admin, is_email_verified=True))
        db.commit()

    client = TestClient(app)
    seeker_headers = _register_and_verify(client, seeker_email, password)
    assert client.patch("/api/v1/users/me/profile", headers=seeker_headers, json={"full_name": "Test Seeker"}).status_code == 200
    resume_response = client.post(
        "/api/v1/resumes",
        headers=seeker_headers,
        json={"title": "Python Developer", "skills": ["Python"]},
    )
    assert resume_response.status_code == 201, resume_response.text
    resume_id = resume_response.json()["id"]

    employer_headers = _register_and_verify(client, employer_email, password)
    employer_application = client.post(
        "/api/v1/employer-applications",
        headers=employer_headers,
        json={
            "kind": "company",
            "name": "Audit Demonstration Company",
            "description": "A non-production company created only for PostgreSQL integration testing.",
            "country": "Tajikistan",
            "contact": employer_email,
        },
    )
    assert employer_application.status_code == 201, employer_application.text

    admin_login = client.post("/api/v1/auth/login", json={"email": admin_email, "password": password})
    assert admin_login.status_code == 200, admin_login.text
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    approval = client.post(f"/api/v1/admin/employer-applications/{employer_application.json()['id']}/approve", headers=admin_headers)
    assert approval.status_code == 200, approval.text

    expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    vacancy_response = client.post(
        "/api/v1/vacancies",
        headers=employer_headers,
        json={"title": "Python Developer", "description": "A permanent remote role used solely for backend integration testing.", "salary_min": 1000, "salary_max": 1500, "currency": "USD", "expires_at": expires_at},
    )
    assert vacancy_response.status_code == 201, vacancy_response.text
    vacancy_id = vacancy_response.json()["id"]
    assert vacancy_response.json()["status"] == "draft"
    with SessionLocal() as db:
        db.get(Vacancy, vacancy_id).is_demo = True
        db.commit()
    assert client.get(f"/api/v1/vacancies/{vacancy_id}").status_code == 404
    assert client.post(f"/api/v1/vacancies/{vacancy_id}/submit", headers=employer_headers).status_code == 200
    assert client.post(f"/api/v1/admin/vacancies/{vacancy_id}/approve", headers=admin_headers).status_code == 200
    assert client.get(f"/api/v1/vacancies/{vacancy_id}").status_code == 200
    assert any(item["id"] == vacancy_id for item in client.get("/api/v1/vacancies").json())

    application = client.post(f"/api/v1/applications/vacancies/{vacancy_id}", headers=seeker_headers, json={"resume_id": resume_id})
    assert application.status_code == 201, application.text
    assert client.post(f"/api/v1/applications/vacancies/{vacancy_id}", headers=seeker_headers, json={"resume_id": resume_id}).status_code == 409
    assert client.patch(f"/api/v1/applications/{application.json()['id']}/status", headers=employer_headers, json={"status": "viewed"}).status_code == 200
    assert client.patch(f"/api/v1/applications/{application.json()['id']}/status", headers=employer_headers, json={"status": "offer"}).status_code == 409

    with SessionLocal() as db:
        assert db.scalar(select(User).where(User.email == employer_email)).role == UserRole.employer
