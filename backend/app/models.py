"""Tablas de la base de datos."""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    """Hora actual en UTC y sin zona: las columnas DATETIME de MySQL no guardan zona horaria."""
    return datetime.now(UTC).replace(tzinfo=None)


# El email se compara byte a byte. La colación por defecto de MySQL ignora acentos y mayúsculas,
# así que «démo@…» encontraría la cuenta «demo@…»: con eso, cada variante con acentos sería una
# vía distinta de probar contraseñas contra la misma cuenta, esquivando el freno de intentos.
EmailColumn = String(254).with_variant(mysql.VARCHAR(254, collation="utf8mb4_bin"), "mysql")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(EmailColumn, unique=True)
    full_name: Mapped[str | None] = mapped_column(String(120))
    # Nunca la contraseña: solo su hash Argon2id (ver app/security.py).
    password_hash: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    last_login_at: Mapped[datetime | None]

    sessions: Mapped[list["UserSession"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class UserSession(Base):
    """Sesión iniciada. Se guarda el hash del token, no el token."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    expires_at: Mapped[datetime] = mapped_column(index=True)

    user: Mapped[User] = relationship(back_populates="sessions")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(60))
    period: Mapped[str] = mapped_column(String(80))
    origin: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(Text)
    price_cents: Mapped[int]
    # Ruta de la foto dentro de la web (frontend/public) y sus créditos de licencia.
    image_path: Mapped[str] = mapped_column(String(255))
    image_alt: Mapped[str] = mapped_column(String(255))
    image_author: Mapped[str] = mapped_column(String(255))
    image_license: Mapped[str] = mapped_column(String(80))
    image_source_url: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(default=0, index=True)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
