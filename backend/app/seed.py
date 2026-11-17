"""Carga inicial: el catálogo de data/products.json y los usuarios de prueba del .env."""

import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, SecretStr, TypeAdapter
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import Settings
from app.models import Product, User
from app.security import hash_password
from app.users import create_user, find_user, validate_password

PRODUCTS_FILE = Path(__file__).resolve().parents[1] / "data" / "products.json"


class ProductSeed(BaseModel):
    """Una pieza tal como está escrita en data/products.json."""

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$", max_length=120)
    name: str = Field(min_length=1, max_length=200)
    category: str = Field(min_length=1, max_length=60)
    period: str = Field(min_length=1, max_length=80)
    origin: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1)
    price_cents: int = Field(gt=0)
    image_path: str = Field(pattern=r"^/products/[a-z0-9-]+\.(jpg|webp)$", max_length=255)
    image_alt: str = Field(min_length=1, max_length=255)
    image_author: str = Field(min_length=1, max_length=255)
    image_license: str = Field(min_length=1, max_length=80)
    image_source_url: str = Field(pattern=r"^https://", max_length=500)


def load_product_seeds(path: Path = PRODUCTS_FILE) -> list[ProductSeed]:
    seeds = TypeAdapter(list[ProductSeed]).validate_python(
        json.loads(path.read_text(encoding="utf-8"))
    )
    slugs = [seed.slug for seed in seeds]
    repeated = sorted({slug for slug in slugs if slugs.count(slug) > 1})
    if repeated:
        raise ValueError(f"Piezas repetidas en {path.name}: {', '.join(repeated)}")
    return seeds


def seed_products(db: Session, seeds: list[ProductSeed]) -> tuple[int, int]:
    """Crea las piezas que falten y actualiza las que ya estén. No borra ninguna.

    El orden del catálogo en la web es el orden del fichero. Devuelve (creadas, actualizadas).
    """
    existing = {product.slug: product for product in db.scalars(select(Product))}
    created = 0
    for order, seed in enumerate(seeds):
        product = existing.get(seed.slug)
        if product is None:
            product = Product(slug=seed.slug)
            db.add(product)
            created += 1
        for field, value in seed.model_dump(exclude={"slug"}).items():
            setattr(product, field, value)
        product.sort_order = order
    db.flush()
    return created, len(seeds) - created


def ensure_user(db: Session, *, username: str, password: str, is_admin: bool) -> User:
    """Crea el usuario o, si ya existe, le pone esa contraseña y ese rol."""
    user = find_user(db, username)
    if user is None:
        return create_user(db, username=username, password=password, is_admin=is_admin)
    validate_password(password)
    user.password_hash = hash_password(password)
    user.is_admin = is_admin
    db.flush()
    return user


def _secret(value: SecretStr | None) -> str:
    return value.get_secret_value() if value else ""


def ensure_seed_users(db: Session, settings: Settings) -> list[str]:
    """Crea el cliente de prueba y el administrador del .env. Devuelve sus nombres.

    Un usuario sin contraseña en el .env no se crea.
    """
    seeded = []
    for username, password, is_admin in (
        (settings.demo_user_username, _secret(settings.demo_user_password), False),
        (settings.admin_username, _secret(settings.admin_password), True),
    ):
        if username and password:
            user = ensure_user(db, username=username, password=password, is_admin=is_admin)
            seeded.append(user.username)
    return seeded
