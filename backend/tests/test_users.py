from fastapi.testclient import TestClient

from app.models import Product, User
from tests.conftest import as_admin, as_user

# Valores de prueba: la tarjeta es el número de prueba que publica Stripe.
PROFILE = {
    "first_name": "Clara",
    "last_name": "Ruiz Gómez",
    "email": "clara@example.com",
    "passport_number": "TEST0001",
    "card_number": "4242424242424242",
    "card_expiry": "12/30",
    "card_cvv": "123",
}


def test_user_reads_and_updates_own_profile(client: TestClient, clienta: User) -> None:
    me = as_user("clienta")

    empty = client.get("/api/users/me", headers=me).json()
    assert empty["username"] == "clienta"
    assert all(empty[field] is None for field in PROFILE)
    assert empty["created_at"].endswith("Z")

    saved = client.put("/api/users/me", json=PROFILE, headers=me)
    assert saved.status_code == 200
    assert {field: saved.json()[field] for field in PROFILE} == PROFILE

    cleared = client.put(
        "/api/users/me", json=PROFILE | {"passport_number": "  ", "email": ""}, headers=me
    ).json()
    assert cleared["passport_number"] is None
    assert cleared["email"] is None
    assert cleared["first_name"] == "Clara"


def test_profile_fields_have_length_limits(client: TestClient, clienta: User) -> None:
    response = client.put("/api/users/me", json={"card_cvv": "12345"}, headers=as_user("clienta"))

    assert response.status_code == 422


def test_users_cannot_see_or_change_each_other(
    client: TestClient, clienta: User, cliente: User
) -> None:
    assert client.get("/api/users/cliente", headers=as_user("clienta")).status_code == 403
    response = client.put("/api/users/cliente", json=PROFILE, headers=as_user("clienta"))
    assert response.status_code == 403


def test_admin_reads_and_edits_any_profile(
    client: TestClient, clienta: User, gestora: User
) -> None:
    assert (
        client.put("/api/users/clienta", json=PROFILE, headers=as_admin("gestora")).status_code
        == 200
    )
    assert client.get("/api/users/me", headers=as_user("clienta")).json()["first_name"] == "Clara"
    assert client.get("/api/users/nadie", headers=as_admin("gestora")).status_code == 404


def test_admin_lists_all_users_with_their_counts(
    client: TestClient, clienta: User, gestora: User, products: list[Product]
) -> None:
    me = as_user("clienta")
    client.post("/api/users/me/orders", json={"product_id": products[0].id}, headers=me)
    client.put(f"/api/users/me/favorites/{products[1].id}", headers=me)

    response = client.get("/api/users", headers=as_admin("gestora"))

    assert response.status_code == 200
    rows = {row["username"]: row for row in response.json()}
    assert set(rows) == {"clienta", "gestora"}
    assert (rows["clienta"]["orders_count"], rows["clienta"]["favorites_count"]) == (1, 1)
    assert rows["clienta"]["is_admin"] is False
    assert rows["gestora"]["is_admin"] is True


def test_only_admins_list_users(client: TestClient, clienta: User, gestora: User) -> None:
    assert client.get("/api/users", headers=as_user("clienta")).status_code == 403
    assert client.get("/api/users", headers=as_user("gestora")).status_code == 403
    assert client.get("/api/users").status_code == 401
