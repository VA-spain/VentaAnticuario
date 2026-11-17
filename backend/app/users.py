"""Alta de usuarios y cambio de contraseña (lo usan la línea de comandos y la carga inicial)."""

import re

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password

MIN_PASSWORD_LENGTH = 10
_EMAIL_SHAPE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    return email.strip().lower()


def validate_new_credentials(email: str, password: str) -> None:
    if len(email) > 254 or not _EMAIL_SHAPE.fullmatch(email):
        raise ValueError(f"«{email}» no parece un email válido.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres.")


def find_user(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == normalize_email(email)))


def create_user(db: Session, *, email: str, password: str, full_name: str | None = None) -> User:
    email = normalize_email(email)
    validate_new_credentials(email, password)
    if find_user(db, email) is not None:
        raise ValueError(f"Ya existe un usuario con el email {email}.")
    user = User(email=email, full_name=full_name or None, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    return user


def set_password(db: Session, *, email: str, password: str) -> User:
    email = normalize_email(email)
    validate_new_credentials(email, password)
    user = find_user(db, email)
    if user is None:
        raise ValueError(f"No existe ningún usuario con el email {email}.")
    user.password_hash = hash_password(password)
    # Cambiar la contraseña cierra las sesiones abiertas con la anterior.
    user.sessions.clear()
    db.flush()
    return user
