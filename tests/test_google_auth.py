from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.models import GoogleIdentity, User
from app.routers import auth
from app.schemas import GoogleTokenIn


class FakeDb:
    def __init__(self, scalar_values=None, user=None):
        self.scalar_values = list(scalar_values or [])
        self.user = user
        self.added = []

    def scalar(self, _query):
        return self.scalar_values.pop(0) if self.scalar_values else None

    def add(self, value):
        self.added.append(value)

    def flush(self):
        for value in self.added:
            if isinstance(value, User) and value.id is None:
                value.id = 1

    def commit(self):
        return None

    def get(self, _model, _user_id):
        return self.user


def test_google_first_login_creates_verified_seeker(monkeypatch):
    monkeypatch.setattr(auth, "_verify_google_token", lambda _token: {"sub": "google-1", "email": "new@example.test"})
    db = FakeDb()

    result = auth.google_login(GoogleTokenIn(id_token="x" * 20), db)

    assert result.access_token
    created_user = next(value for value in db.added if isinstance(value, User))
    identity = next(value for value in db.added if isinstance(value, GoogleIdentity))
    assert created_user.email == "new@example.test"
    assert created_user.is_email_verified is True
    assert created_user.role.value == "seeker"
    assert identity.subject == "google-1"


def test_google_repeat_login_uses_existing_identity(monkeypatch):
    user = SimpleNamespace(id=7, is_active=True)
    identity = SimpleNamespace(user_id=7)
    monkeypatch.setattr(auth, "_verify_google_token", lambda _token: {"sub": "google-1", "email": "same@example.test"})
    result = auth.google_login(GoogleTokenIn(id_token="x" * 20), FakeDb([identity], user=user))
    assert result.access_token


def test_google_cannot_claim_existing_email_without_link(monkeypatch):
    existing = SimpleNamespace(email="existing@example.test")
    monkeypatch.setattr(auth, "_verify_google_token", lambda _token: {"sub": "google-new", "email": "existing@example.test"})
    with pytest.raises(HTTPException) as error:
        auth.google_login(GoogleTokenIn(id_token="x" * 20), FakeDb([None, existing]))
    assert error.value.status_code == 409


def test_google_verification_requires_configuration(monkeypatch):
    settings = SimpleNamespace(google_client_id=None)
    monkeypatch.setattr(auth, "get_settings", lambda: settings)
    with pytest.raises(HTTPException) as error:
        auth._verify_google_token("invalid-token")
    assert error.value.status_code == 503


def test_google_verification_rejects_non_jwt_credential():
    with pytest.raises(HTTPException) as error:
        auth._verify_google_token("not-a-jwt")
    assert error.value.status_code in {401, 503}

