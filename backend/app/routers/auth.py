"""Registro, inicio de sesión y sesión actual."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.exc import IntegrityError

from app.config import Settings, get_settings
from app.deps import ActorDep, DbSession
from app.models import User, utcnow
from app.rate_limit import LoginThrottle, get_login_throttle
from app.schemas import LoginRequest, MeOut, RegisterRequest, SessionOut, UsernameCheck
from app.security import (
    dummy_password_hash,
    hash_password,
    make_session_value,
    needs_rehash,
    verify_password,
)
from app.users import (
    UsernameTakenError,
    create_user,
    find_user,
    normalize_username,
    validate_username,
)

router = APIRouter(prefix="/api/auth", tags=["sesión"])

SettingsDep = Annotated[Settings, Depends(get_settings)]

USERNAME_TAKEN = "Ese nombre de usuario ya existe."


def me_out(user: User, *, is_admin: bool) -> MeOut:
    return MeOut(
        username=user.username,
        is_admin=is_admin,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def session_out(user: User, settings: Settings) -> SessionOut:
    """La cookie de un administrador es la de administrador; la de los demás, la normal."""
    ttl = timedelta(minutes=settings.session_ttl_minutes)
    return SessionOut(
        cookie_value=make_session_value(user.username, is_admin=user.is_admin),
        expires_in_seconds=int(ttl.total_seconds()),
        user=me_out(user, is_admin=user.is_admin),
    )


@router.get("/username-available", response_model=UsernameCheck)
def username_available(
    username: Annotated[str, Query(max_length=100)], db: DbSession
) -> UsernameCheck:
    normalized = normalize_username(username)
    try:
        validate_username(normalized)
    except ValueError as error:
        return UsernameCheck(username=normalized, available=False, reason=str(error))
    if find_user(db, normalized) is not None:
        return UsernameCheck(username=normalized, available=False, reason=USERNAME_TAKEN)
    return UsernameCheck(username=normalized, available=True, reason=None)


@router.post("/register", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession, settings: SettingsDep) -> SessionOut:
    """Crea la cuenta (y con ella su portal) y deja la sesión iniciada."""
    try:
        user = create_user(db, username=payload.username, password=payload.password)
        user.last_login_at = utcnow()
        db.commit()
    except (UsernameTakenError, IntegrityError) as error:
        # IntegrityError: otra petición registró el mismo nombre un instante antes.
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, USERNAME_TAKEN) from error
    except ValueError as error:
        db.rollback()
        raise HTTPException(422, str(error)) from error
    return session_out(user, settings)


@router.post("/login", response_model=SessionOut)
def login(
    payload: LoginRequest,
    request: Request,
    db: DbSession,
    settings: SettingsDep,
    throttle: Annotated[LoginThrottle, Depends(get_login_throttle)],
) -> SessionOut:
    username = normalize_username(payload.username)
    client_ip = request.client.host if request.client else "desconocida"

    wait_seconds = throttle.retry_after(username, client_ip)
    if wait_seconds:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Espera unos minutos y vuelve a probar.",
            headers={"Retry-After": str(wait_seconds)},
        )

    user = find_user(db, username)
    # Se verifica siempre, exista o no la cuenta, para que el tiempo de respuesta no la delate.
    password_ok = verify_password(
        user.password_hash if user else dummy_password_hash(), payload.password
    )
    if user is None or not user.is_active or not password_ok:
        throttle.register_failure(username, client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos.",
        )

    if needs_rehash(user.password_hash):
        user.password_hash = hash_password(payload.password)
    user.last_login_at = utcnow()
    db.commit()
    throttle.register_success(username, client_ip)
    return session_out(user, settings)


@router.get("/me", response_model=MeOut)
def me(actor: ActorDep) -> MeOut:
    return me_out(actor.user, is_admin=actor.is_admin)
