import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import REPO_ROOT, Settings
from app.models import Product, User
from app.security import verify_password
from app.seed import ProductSeed, ensure_seed_users, load_product_seeds, seed_products

PUBLIC_DIR = REPO_ROOT / "frontend" / "public"


def seed(slug: str, **changes: object) -> ProductSeed:
    data = {
        "slug": slug,
        "name": f"Pieza {slug}",
        "category": "Relojes",
        "period": "c. 1900",
        "origin": "Selva Negra",
        "description": "Descripción.",
        "price_cents": 50_000,
        "image_path": f"/products/{slug}.jpg",
        "image_alt": "Foto",
        "image_author": "Autora",
        "image_license": "CC0 1.0",
        "image_source_url": "https://commons.wikimedia.org/wiki/File:X.jpg",
    }
    return ProductSeed.model_validate(data | changes)


def test_real_catalog_file_is_valid_and_every_photo_exists() -> None:
    seeds = load_product_seeds()

    assert len(seeds) >= 6
    missing = [s.image_path for s in seeds if not (PUBLIC_DIR / s.image_path.lstrip("/")).is_file()]
    assert missing == []


def test_seeding_twice_updates_instead_of_duplicating(db: Session) -> None:
    assert seed_products(db, [seed("uno"), seed("dos")]) == (2, 0)
    db.commit()

    result = seed_products(db, [seed("dos", price_cents=75_000), seed("uno"), seed("tres")])
    db.commit()

    assert result == (1, 2)
    products = db.scalars(select(Product).order_by(Product.sort_order)).all()
    assert [p.slug for p in products] == ["dos", "uno", "tres"]
    assert products[0].price_cents == 75_000


def test_catalog_file_with_a_repeated_slug_is_rejected(tmp_path: Path) -> None:
    path = tmp_path / "products.json"
    path.write_text(json.dumps([seed("uno").model_dump(), seed("uno").model_dump()]))

    with pytest.raises(ValueError, match="repetidas"):
        load_product_seeds(path)


def test_catalog_entry_with_an_unknown_field_is_rejected() -> None:
    with pytest.raises(ValidationError):
        seed("uno", precio=10)


def seed_settings(**values: str) -> Settings:
    return Settings(_env_file=None, **values)


def test_seed_users_are_created_with_their_roles_and_hashed_passwords(db: Session) -> None:
    settings = seed_settings(
        demo_user_username="Cliente",
        demo_user_password="clave-de-prueba-1",
        admin_username="admin",
        admin_password="clave-de-prueba-2",
    )

    assert ensure_seed_users(db, settings) == ["cliente", "admin"]
    db.commit()

    users = {user.username: user for user in db.scalars(select(User))}
    assert users["cliente"].is_admin is False
    assert users["admin"].is_admin is True
    assert users["admin"].password_hash.startswith("$argon2id$")
    assert verify_password(users["admin"].password_hash, "clave-de-prueba-2")


def test_seed_users_get_the_new_password_when_the_env_changes(db: Session) -> None:
    ensure_seed_users(db, seed_settings(admin_username="admin", admin_password="primera-clave"))
    ensure_seed_users(db, seed_settings(admin_username="admin", admin_password="segunda-clave"))
    db.commit()

    users = db.scalars(select(User)).all()
    assert len(users) == 1
    assert verify_password(users[0].password_hash, "segunda-clave")
    assert not verify_password(users[0].password_hash, "primera-clave")


def test_no_seed_users_without_passwords(db: Session) -> None:
    settings = seed_settings(demo_user_username="cliente", admin_username="admin")

    assert ensure_seed_users(db, settings) == []
    assert db.scalar(select(User)) is None
