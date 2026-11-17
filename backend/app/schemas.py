"""Formas de los datos que entran y salen por la API."""

from pydantic import BaseModel, ConfigDict, Field


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


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=1024)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str
    full_name: str | None


class LoginResponse(BaseModel):
    # El token solo viaja en esta respuesta; en la base de datos queda su hash.
    token: str
    expires_in_seconds: int
    user: UserOut
