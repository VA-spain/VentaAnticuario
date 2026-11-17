"""Quién hace la petición y a qué datos puede acceder."""

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import User
from app.security import parse_session_value

bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[Session, Depends(get_db)]


@dataclass(frozen=True)
class Actor:
    """La persona que hace la petición. `is_admin` sale del formato de su cookie."""

    user: User
    is_admin: bool


def get_actor(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    db: DbSession,
) -> Actor:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión no válida o caducada.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    parsed = parse_session_value(credentials.credentials) if credentials else None
    if parsed is None:
        raise unauthorized
    username, claims_admin = parsed
    user = db.scalar(select(User).where(User.username == username))
    # La cookie de administrador solo vale para quien lo es en la base de datos.
    if user is None or not user.is_active or (claims_admin and not user.is_admin):
        raise unauthorized
    return Actor(user=user, is_admin=claims_admin)


ActorDep = Annotated[Actor, Depends(get_actor)]


def require_admin(actor: ActorDep) -> Actor:
    if not actor.is_admin:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Solo para administradores.")
    return actor


AdminDep = Annotated[Actor, Depends(require_admin)]


def get_target_user(username: str, actor: ActorDep, db: DbSession) -> User:
    """El usuario cuyos datos se piden.

    Cada uno accede a los suyos («me» o su propio nombre); un administrador, a los de cualquiera.
    """
    if username in ("me", actor.user.username):
        return actor.user
    if not actor.is_admin:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "No puedes acceder a los datos de otro usuario."
        )
    user = db.scalar(select(User).where(User.username == username))
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe ese usuario.")
    return user


TargetUser = Annotated[User, Depends(get_target_user)]
