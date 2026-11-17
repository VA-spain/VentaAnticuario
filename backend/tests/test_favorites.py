from fastapi.testclient import TestClient

from app.models import Product, User
from tests.conftest import as_admin, as_user


def favorite(client: TestClient, method: str, product_id: int, headers: dict, username: str = "me"):
    return client.request(method, f"/api/users/{username}/favorites/{product_id}", headers=headers)


def favorite_slugs(client: TestClient, headers: dict, username: str = "me") -> list[str]:
    response = client.get(f"/api/users/{username}/favorites", headers=headers)
    return sorted(product["slug"] for product in response.json())


def test_favorites_can_be_added_listed_and_removed(
    client: TestClient, clienta: User, products: list[Product]
) -> None:
    reloj, plato = products
    me = as_user("clienta")

    assert favorite(client, "PUT", reloj.id, me).status_code == 204
    assert favorite(client, "PUT", reloj.id, me).status_code == 204  # dos veces no duplica
    assert favorite(client, "PUT", plato.id, me).status_code == 204
    assert favorite_slugs(client, me) == ["plato", "reloj"]

    assert favorite(client, "DELETE", reloj.id, me).status_code == 204
    assert favorite(client, "DELETE", reloj.id, me).status_code == 204  # quitar dos veces no falla
    assert favorite_slugs(client, me) == ["plato"]


def test_favorite_of_an_unknown_product_fails(client: TestClient, clienta: User) -> None:
    assert favorite(client, "PUT", 999, as_user("clienta")).status_code == 404


def test_favorites_need_a_session(client: TestClient, products: list[Product]) -> None:
    assert favorite(client, "PUT", products[0].id, {}).status_code == 401


def test_favorites_are_private_but_an_admin_can_edit_them(
    client: TestClient,
    clienta: User,
    cliente: User,
    gestora: User,
    products: list[Product],
) -> None:
    reloj, plato = products
    favorite(client, "PUT", reloj.id, as_user("clienta"))

    assert client.get("/api/users/clienta/favorites", headers=as_user("cliente")).status_code == 403
    denied = favorite(client, "DELETE", reloj.id, as_user("cliente"), username="clienta")
    assert denied.status_code == 403

    admin = as_admin("gestora")
    assert favorite(client, "PUT", plato.id, admin, username="clienta").status_code == 204
    assert favorite(client, "DELETE", reloj.id, admin, username="clienta").status_code == 204
    assert favorite_slugs(client, as_user("clienta")) == ["plato"]
