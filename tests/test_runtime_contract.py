from fastapi.testclient import TestClient

from app.main import app
from app.schemas import UserOut


def test_health_and_documentation_are_available_without_a_database_connection():
    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/docs").status_code == 200
    assert client.get("/api/v1/openapi.json").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_root_openapi_alias_returns_the_versioned_schema():
    client = TestClient(app)

    assert client.get("/openapi.json").json() == client.get("/api/v1/openapi.json").json()


def test_existing_user_with_legacy_email_can_be_serialized():
    from datetime import datetime, timezone
    from types import SimpleNamespace

    user = SimpleNamespace(
        id=1,
        email="legacy@example.test",
        role="seeker",
        is_email_verified=True,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        profile=None,
    )

    assert UserOut.model_validate(user).email == "legacy@example.test"
