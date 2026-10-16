from datetime import timedelta
from hashlib import sha256
from secrets import randbelow

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.dependencies import CurrentUser, DbSession
from app.core.security import create_token, decode_token, hash_password, token_hash, verify_password
from app.models import EmailVerificationCode, GoogleIdentity, RefreshSession, User, UserRole
from app.schemas import GoogleTokenIn, LoginIn, Message, RefreshIn, RegisterIn, TokenPair, VerifyEmailIn

router = APIRouter(prefix="/auth", tags=["auth"])


def _verify_google_token(id_token: str) -> dict[str, str]:
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google OAuth не настроен")
    if id_token.count(".") != 2:
        raise HTTPException(status_code=401, detail="Google credential имеет неверный формат")
    try:
        from google.auth.transport import requests as google_requests
        from google.oauth2 import id_token as google_id_token
        claims = google_id_token.verify_oauth2_token(id_token, google_requests.Request(), settings.google_client_id)
    except HTTPException:
        raise
    except ImportError as error:
        raise HTTPException(status_code=503, detail="Серверная проверка Google OAuth недоступна") from error
    except Exception as error:
        category = str(error).lower()
        if "audience" in category:
            detail = "Google token audience не совпадает с настроенным Client ID"
        elif "issuer" in category or "iss" in category:
            detail = "Google token issuer не прошёл проверку"
        elif "expired" in category or "exp" in category:
            detail = "Срок действия Google token истёк"
        elif "transport" in category or "certificate" in category or "connection" in category:
            raise HTTPException(status_code=503, detail="Не удалось получить сертификаты Google") from error
        else:
            detail = "Google ID token не прошёл проверку подписи или формата"
        raise HTTPException(status_code=401, detail=detail) from error
    issuer = claims.get("iss")
    if issuer not in {"accounts.google.com", "https://accounts.google.com"} or not claims.get("sub"):
        raise HTTPException(status_code=401, detail="Недействительный Google ID token")
    if claims.get("email_verified") is not True or not claims.get("email"):
        raise HTTPException(status_code=403, detail="Google email должен быть подтверждён")
    return {"sub": str(claims["sub"]), "email": str(claims["email"]).lower()}


def _issue_tokens(db: DbSession, user: User) -> TokenPair:
    settings = get_settings()
    access, _ = create_token(str(user.id), "access", timedelta(minutes=settings.access_token_minutes))
    refresh, expires_at = create_token(str(user.id), "refresh", timedelta(days=settings.refresh_token_days))
    db.add(RefreshSession(user_id=user.id, token_hash=token_hash(refresh), expires_at=expires_at))
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=Message, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, db: DbSession):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован")
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    code = f"{randbelow(1_000_000):06d}"
    from datetime import datetime, timedelta, timezone
    db.add(EmailVerificationCode(user_id=user.id, code_hash=sha256(code.encode()).hexdigest(), expires_at=datetime.now(timezone.utc) + timedelta(minutes=get_settings().email_code_minutes)))
    db.commit()
    # SMTP delivery is intentionally configured in a later stage. Never return this code in production.
    detail = "Код подтверждения создан. Настройте SMTP для доставки email."
    if get_settings().environment == "development":
        detail += f" Development code: {code}"
    return Message(detail=detail)


@router.post("/verify-email", response_model=TokenPair)
def verify_email(payload: VerifyEmailIn, db: DbSession):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user:
        raise HTTPException(status_code=400, detail="Неверный email или код")
    from datetime import datetime, timezone
    record = db.scalar(select(EmailVerificationCode).where(EmailVerificationCode.user_id == user.id, EmailVerificationCode.used_at.is_(None)).order_by(EmailVerificationCode.created_at.desc()))
    if not record or record.expires_at < datetime.now(timezone.utc) or record.code_hash != sha256(payload.code.encode()).hexdigest():
        raise HTTPException(status_code=400, detail="Неверный email или код")
    record.used_at = datetime.now(timezone.utc)
    user.is_email_verified = True
    db.commit()
    return _issue_tokens(db, user)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginIn, db: DbSession):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")
    if not user.is_active or not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Аккаунт не активирован или email не подтверждён")
    return _issue_tokens(db, user)


@router.post("/google", response_model=TokenPair)
def google_login(payload: GoogleTokenIn, db: DbSession):
    claims = _verify_google_token(payload.id_token)
    identity = db.scalar(select(GoogleIdentity).where(GoogleIdentity.subject == claims["sub"]))
    if identity:
        user = db.get(User, identity.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=403, detail="Аккаунт недоступен")
        return _issue_tokens(db, user)
    existing = db.scalar(select(User).where(User.email == claims["email"]))
    if existing:
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован. Войдите по паролю и привяжите Google в настройках.")
    user = User(email=claims["email"], password_hash=hash_password(token_hash(payload.id_token)), role=UserRole.seeker, is_email_verified=True)
    db.add(user)
    db.flush()
    db.add(GoogleIdentity(user_id=user.id, subject=claims["sub"], email=claims["email"]))
    db.commit()
    return _issue_tokens(db, user)


@router.post("/google/link", response_model=Message)
def link_google(payload: GoogleTokenIn, db: DbSession, user: CurrentUser):
    claims = _verify_google_token(payload.id_token)
    linked = db.scalar(select(GoogleIdentity).where(GoogleIdentity.subject == claims["sub"]))
    if linked and linked.user_id != user.id:
        raise HTTPException(status_code=409, detail="Google аккаунт уже привязан к другому пользователю")
    if user.email.lower() != claims["email"] or not user.is_email_verified:
        raise HTTPException(status_code=403, detail="Для привязки нужен подтверждённый email текущего аккаунта")
    if not linked:
        db.add(GoogleIdentity(user_id=user.id, subject=claims["sub"], email=claims["email"]))
        db.commit()
    return Message(detail="Google аккаунт привязан")


@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshIn, db: DbSession):
    try:
        claims = decode_token(payload.refresh_token, "refresh")
    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error)) from error
    from datetime import datetime, timezone
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(payload.refresh_token)))
    if not session or session.revoked_at or session.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token отозван или истёк")
    session.revoked_at = datetime.now(timezone.utc)
    user = db.get(User, int(claims["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Пользователь недоступен")
    db.commit()
    return _issue_tokens(db, user)


@router.post("/logout", response_model=Message)
def logout(payload: RefreshIn, db: DbSession, user: CurrentUser):
    session = db.scalar(select(RefreshSession).where(RefreshSession.token_hash == token_hash(payload.refresh_token)))
    if session and session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Нельзя завершить чужую сессию")
    if session:
        from datetime import datetime, timezone
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
    return Message(detail="Сессия завершена")
