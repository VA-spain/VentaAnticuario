import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import REPO_ROOT, Settings
from app.models import Product, User
from app.security import verify_password
from app.seed import ProductSeed, ensure_demo_user, load_product_seeds, seed_products

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


def test_demo_user_is_created_with_a_hashed_password(db: Session) -> None:
    settings = Settings(
        _env_file=None,
        demo_user_email="Demo@Example.com",
        demo_user_name="Prueba",
        demo_user_password="una-clave-de-prueba",
    )

    assert ensure_demo_user(db, settings) == "demo@example.com"
    db.commit()

    user = db.scalar(select(User))
    assert user.full_name == "Prueba"
    assert user.password_hash.startswith("$argon2id$")
    assert verify_password(user.password_hash, "una-clave-de-prueba")


def test_demo_user_gets_the_new_password_when_the_env_changes(db: Session) -> None:
    base = {"_env_file": None, "demo_user_email": "demo@example.com"}
    ensure_demo_user(db, Settings(**base, demo_user_password="primera-clave-larga"))
    ensure_demo_user(db, Settings(**base, demo_user_password="segunda-clave-larga"))
    db.commit()

    users = db.scalars(select(User)).all()
    assert len(users) == 1
    assert verify_password(users[0].password_hash, "segunda-clave-larga")
    assert not verify_password(users[0].password_hash, "primera-clave-larga")


def test_no_demo_user_without_a_password(db: Session) -> None:
    settings = Settings(_env_file=None, demo_user_email="demo@example.com", demo_user_password="")

    assert ensure_demo_user(db, settings) is None
    assert db.scalar(select(User)) is None
