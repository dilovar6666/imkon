from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, password_hash_value: str) -> bool:
    return password_hash.verify(password, password_hash_value)


def token_hash(token: str) -> str:
    return sha256(token.encode()).hexdigest()


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> tuple[str, datetime]:
    expires_at = datetime.now(timezone.utc) + expires_delta
    payload = {"sub": subject, "type": token_type, "exp": expires_at, "jti": token_urlsafe(16)}
    return jwt.encode(payload, get_settings().jwt_secret_key, algorithm="HS256"), expires_at


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, get_settings().jwt_secret_key, algorithms=["HS256"])
    except jwt.PyJWTError as error:
        raise ValueError("Недействительный токен") from error
    if payload.get("type") != expected_type or not payload.get("sub"):
        raise ValueError("Недействительный токен")
    return payload
