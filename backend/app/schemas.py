"""Formas de los datos que entran y salen por la API."""

from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, StringConstraints


def _utc_iso(value: datetime) -> str:
    """Las fechas se guardan en UTC y sin zona: se envían con la «Z» para que nadie dude."""
    return value.replace(tzinfo=UTC).isoformat().replace("+00:00", "Z")


UtcDateTime = Annotated[datetime, PlainSerializer(_utc_iso, return_type=str, when_used="json")]
OrderStatus = Literal["confirmed", "shipped", "delivered", "cancelled"]


def _trimmed(*, min_length: int = 0, max_length: int) -> StringConstraints:
    return StringConstraints(strip_whitespace=True, min_length=min_length, max_length=max_length)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    category: str
    period: str
    origin: str
    description: str
    price_cents: int
    image_path: str
    image_alt: str
    image_author: str
    image_license: str
    image_source_url: str


# --- Sesión -----------------------------------------------------------------------------------


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1024)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=1024)


class UsernameCheck(BaseModel):
    username: str
    available: bool
    reason: str | None


class MeOut(BaseModel):
    username: str
    # Privilegios de esta sesión: dependen del formato de la cookie.
    is_admin: bool
    first_name: str | None
    last_name: str | None


class SessionOut(BaseModel):
    # Valor que la web guarda tal cual en la cookie de sesión.
    cookie_value: str
    expires_in_seconds: int
    user: MeOut


# --- Usuarios ---------------------------------------------------------------------------------


class ProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    is_admin: bool
    is_active: bool
    first_name: str | None
    last_name: str | None
    email: str | None
    passport_number: str | None
    card_number: str | None
    card_expiry: str | None
    card_cvv: str | None
    created_at: UtcDateTime
    last_login_at: UtcDateTime | None


class ProfileIn(BaseModel):
    """Los siete datos de la página de configuración. Un dato vacío se borra."""

    first_name: Annotated[str | None, _trimmed(max_length=80)] = None
    last_name: Annotated[str | None, _trimmed(max_length=120)] = None
    email: Annotated[str | None, _trimmed(max_length=254)] = None
    passport_number: Annotated[str | None, _trimmed(max_length=40)] = None
    card_number: Annotated[str | None, _trimmed(max_length=32)] = None
    card_expiry: Annotated[str | None, _trimmed(max_length=7)] = None
    card_cvv: Annotated[str | None, _trimmed(max_length=4)] = None


class AdminUserOut(BaseModel):
    username: str
    first_name: str | None
    last_name: str | None
    email: str | None
    is_admin: bool
    is_active: bool
    created_at: UtcDateTime
    last_login_at: UtcDateTime | None
    orders_count: int
    favorites_count: int


# --- Pedidos ----------------------------------------------------------------------------------


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product: ProductOut
    quantity: int
    unit_price_cents: int
    status: str
    created_at: UtcDateTime


class OrderIn(BaseModel):
    product_id: int = Field(gt=0)


class OrderPatch(BaseModel):
    quantity: int | None = Field(default=None, ge=1, le=999)
    unit_price_cents: int | None = Field(default=None, ge=0, le=100_000_000)
    status: OrderStatus | None = None


# --- Contacto ---------------------------------------------------------------------------------


class ContactIn(BaseModel):
    name: Annotated[str, _trimmed(min_length=1, max_length=120)]
    email: Annotated[str, _trimmed(min_length=3, max_length=254)]
    subject: Annotated[str | None, _trimmed(max_length=200)] = None
    message: Annotated[str, _trimmed(min_length=1, max_length=5000)]


class ContactOut(BaseModel):
    id: int
