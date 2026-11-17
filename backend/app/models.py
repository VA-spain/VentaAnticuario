"""Tablas de la base de datos."""

from datetime import UTC, datetime

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects import mysql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

ORDER_STATUSES = ("confirmed", "shipped", "delivered", "cancelled")


def utcnow() -> datetime:
    """Hora actual en UTC y sin zona: las columnas DATETIME de MySQL no guardan zona horaria."""
    return datetime.now(UTC).replace(tzinfo=None)


# El nombre de usuario se compara byte a byte. La colación por defecto de MySQL ignora acentos y
# mayúsculas, así que «ána» encontraría la cuenta «ana».
UsernameColumn = String(30).with_variant(mysql.VARCHAR(30, collation="utf8mb4_bin"), "mysql")


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


class User(Base):
    """Un cliente de la tienda o un administrador."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(UsernameColumn, unique=True)
    # Nunca la contraseña: solo su hash Argon2id (ver app/security.py).
    password_hash: Mapped[str] = mapped_column(String(255))
    is_admin: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=True)

    # Datos de la página de configuración del portal. Todos opcionales.
    first_name: Mapped[str | None] = mapped_column(String(80))
    last_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str | None] = mapped_column(String(254))
    passport_number: Mapped[str | None] = mapped_column(String(40))
    card_number: Mapped[str | None] = mapped_column(String(32))
    card_expiry: Mapped[str | None] = mapped_column(String(7))
    card_cvv: Mapped[str | None] = mapped_column(String(4))

    created_at: Mapped[datetime] = mapped_column(default=utcnow)
    last_login_at: Mapped[datetime | None]

    orders: Mapped[list["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    favorites: Mapped[list["Favorite"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Order(Base):
    """Una compra: un clic en «Comprar» crea una fila."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), index=True)
    quantity: Mapped[int] = mapped_column(default=1)
    # El precio se copia al comprar: si la pieza cambia de precio, el pedido no cambia.
    unit_price_cents: Mapped[int]
    status: Mapped[str] = mapped_column(String(20), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    user: Mapped[User] = relationship(back_populates="orders")
    product: Mapped[Product] = relationship(lazy="joined")


class Favorite(Base):
    """Una pieza marcada como favorita por un usuario."""

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "product_id", name="uq_favorite_user_product"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(default=utcnow)

    user: Mapped[User] = relationship(back_populates="favorites")
    product: Mapped[Product] = relationship(lazy="joined")


class ContactMessage(Base):
    """Un mensaje enviado desde la página de contacto."""

    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(254))
    subject: Mapped[str | None] = mapped_column(String(200))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=utcnow)
