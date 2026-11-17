from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.factories import make_product


def test_catalog_is_empty_without_products(client: TestClient) -> None:
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.json() == []


def test_catalog_follows_sort_order_and_needs_no_session(client: TestClient, db: Session) -> None:
    db.add_all([make_product("segunda", 1), make_product("primera", 0)])
    db.commit()

    body = client.get("/api/products").json()

    assert [product["slug"] for product in body] == ["primera", "segunda"]
    assert body[0] == {
        "id": body[0]["id"],
        "slug": "primera",
        "name": "Pieza primera",
        "category": "Relojes",
        "period": "c. 1900",
        "origin": "Selva Negra",
        "description": "Descripción de prueba.",
        "price_cents": 120_000,
        "image_path": "/products/primera.jpg",
        "image_alt": "Foto de prueba",
        "image_author": "Autora de prueba",
        "image_license": "CC0 1.0",
        "image_source_url": "https://commons.wikimedia.org/wiki/File:Prueba.jpg",
    }


def test_health_reports_ok_when_the_database_answers(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
