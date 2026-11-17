"""Inicio de sesión, sesión actual y cierre de sesión."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.db import get_db
from app.models import User, UserSession, utcnow
from app.rate_limit import LoginThrottle, get_login_throttle
from app.schemas import LoginRequest, LoginResponse, UserOut
from app.security import (
    dummy_password_hash,
    hash_password,
    hash_token,
    needs_rehash,
    new_session_token,
    verify_password,
)
from app.users import normalize_email

router = APIRouter(prefix="/api/auth", tags=["sesión"])
bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


def current_session(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: DbSession,
) -> UserSession:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión no válida o caducada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None:
        raise unauthorized
    session = db.scalar(
        select(UserSession).where(UserSession.token_hash == hash_token(credentials.credentials))
    )
    if session is None:
        raise unauthorized
    if session.expires_at <= utcnow() or not session.user.is_active:
        db.delete(session)
        db.commit()
        raise unauthorized
    return session


CurrentSession = Annotated[UserSession, Depends(current_session)]


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    request: Request,
    db: DbSession,
    settings: Annotated[Settings, Depends(get_settings)],
    throttle: Annotated[LoginThrottle, Depends(get_login_throttle)],
) -> LoginResponse:
    email = normalize_email(payload.email)
    client_ip = request.client.host if request.client else "desconocida"

    wait_seconds = throttle.retry_after(email, client_ip)
    if wait_seconds:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Espera unos minutos y vuelve a probar.",
            headers={"Retry-After": str(wait_seconds)},
        )

    user = db.scalar(select(User).where(User.email == email))
    # Se verifica siempre, exista o no la cuenta, para que el tiempo de respuesta no la delate.
    password_ok = verify_password(
        user.password_hash if user else dummy_password_hash(), payload.password
    )
    if user is None or not user.is_active or not password_ok:
        throttle.register_failure(email, client_ip)
        # Mismo mensaje para email desconocido y contraseña errónea: no revela qué cuentas existen.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos.",
        )

    now = utcnow()
    db.execute(delete(UserSession).where(UserSession.expires_at <= now))
    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
    token = new_session_token()
    ttl = timedelta(minutes=settings.session_ttl_minutes)
    db.add(
        UserSession(
            user_id=user.id, token_hash=hash_token(token), created_at=now, expires_at=now + ttl
        )
    )
    user.last_login_at = now
    db.commit()
    throttle.register_success(email, client_ip)

    return LoginResponse(
        token=token,
        expires_in_seconds=int(ttl.total_seconds()),
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut)
def me(session: CurrentSession) -> User:
    return session.user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(session: CurrentSession, db: DbSession) -> None:
    db.delete(session)
    db.commit()
