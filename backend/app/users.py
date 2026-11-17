"""Alta de usuarios y cambio de contraseña (lo usan el registro, la línea de comandos y la carga
inicial)."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password

# Empieza por una letra y no lleva «+»: así la cookie de sesión no puede ser ambigua.
USERNAME_PATTERN = re.compile(r"[a-z][a-z0-9._-]{2,29}")
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class UsernameTakenError(ValueError):
    """Ya existe un usuario con ese nombre."""


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "El nombre de usuario debe tener de 3 a 30 caracteres, empezar por una letra y usar "
            "solo letras, números, punto, guion o guion bajo."
        )


def validate_password(password: str) -> None:
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña no puede pasar de {MAX_PASSWORD_LENGTH} caracteres.")


def find_user(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == normalize_username(username)))


def create_user(db: Session, *, username: str, password: str, is_admin: bool = False) -> User:
    username = normalize_username(username)
    validate_username(username)
    validate_password(password)
    if find_user(db, username) is not None:
        raise UsernameTakenError(f"Ya existe un usuario llamado {username}.")
    user = User(username=username, password_hash=hash_password(password), is_admin=is_admin)
    db.add(user)
    db.flush()
    return user


def set_password(db: Session, *, username: str, password: str) -> User:
    validate_password(password)
    user = find_user(db, username)
    if user is None:
        raise ValueError(f"No existe ningún usuario llamado {normalize_username(username)}.")
    user.password_hash = hash_password(password)
    db.flush()
    return user
