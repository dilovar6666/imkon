from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.security import create_token, decode_token
from app.models import VacancyStatus
from app.routers.applications import apply
from app.routers.auth import logout
from app.schemas import ApplicationIn, RefreshIn


def test_refresh_token_cannot_be_decoded_as_access_token():
    refresh_token, _ = create_token("1", "refresh", timedelta(minutes=1))

    with pytest.raises(ValueError):
        decode_token(refresh_token, "access")


def test_logout_cannot_revoke_another_users_refresh_session():
    session = SimpleNamespace(user_id=2)
    database = SimpleNamespace(scalar=lambda _: session)

    with pytest.raises(HTTPException) as error:
        logout(RefreshIn(refresh_token="token"), database, SimpleNamespace(id=1))

    assert error.value.status_code == 403


def test_application_rejects_an_expired_published_vacancy():
    expired_vacancy = SimpleNamespace(status=VacancyStatus.published, expires_at=datetime.now(timezone.utc) - timedelta(seconds=1))
    database = SimpleNamespace(get=lambda *_: expired_vacancy)

    with pytest.raises(HTTPException) as error:
        apply(1, ApplicationIn(resume_id=1), SimpleNamespace(id=1), database)

    assert error.value.status_code == 404
