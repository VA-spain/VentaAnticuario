from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Product, User
from tests.conftest import as_admin, as_user


def buy(client: TestClient, product_id: int, headers: dict, username: str = "me"):
    return client.post(
        f"/api/users/{username}/orders", json={"product_id": product_id}, headers=headers
    )


def my_orders(client: TestClient, headers: dict, username: str = "me") -> list[dict]:
    return client.get(f"/api/users/{username}/orders", headers=headers).json()


def test_buying_creates_an_order_at_the_current_price(
    client: TestClient, clienta: User, products: list[Product], db: Session
) -> None:
    reloj = products[0]

    response = buy(client, reloj.id, as_user("clienta"))

    assert response.status_code == 201
    order = response.json()
    assert order["product"]["slug"] == "reloj"
    assert order["quantity"] == 1
    assert order["unit_price_cents"] == 240_000
    assert order["status"] == "confirmed"
    assert order["created_at"].endswith("Z")

    # El precio queda copiado en el pedido aunque la pieza cambie después.
    reloj.price_cents = 1
    db.commit()
    assert [o["unit_price_cents"] for o in my_orders(client, as_user("clienta"))] == [240_000]


def test_stock_is_unlimited(client: TestClient, clienta: User, products: list[Product]) -> None:
    for _ in range(3):
        assert buy(client, products[0].id, as_user("clienta")).status_code == 201

    assert len(my_orders(client, as_user("clienta"))) == 3


def test_buying_needs_a_session(client: TestClient, products: list[Product]) -> None:
    assert buy(client, products[0].id, {}).status_code == 401


def test_buying_an_unknown_product_fails(client: TestClient, clienta: User) -> None:
    assert buy(client, 999, as_user("clienta")).status_code == 404


def test_orders_are_private(
    client: TestClient, clienta: User, cliente: User, products: list[Product]
) -> None:
    buy(client, products[0].id, as_user("clienta"))

    assert client.get("/api/users/clienta/orders", headers=as_user("cliente")).status_code == 403
    assert my_orders(client, as_user("cliente")) == []


def test_admin_sees_edits_and_deletes_any_order(
    client: TestClient, clienta: User, gestora: User, products: list[Product]
) -> None:
    order_id = buy(client, products[0].id, as_user("clienta")).json()["id"]
    assert len(my_orders(client, as_admin("gestora"), username="clienta")) == 1

    patched = client.patch(
        f"/api/orders/{order_id}",
        json={"status": "shipped", "quantity": 2, "unit_price_cents": 200_000},
        headers=as_admin("gestora"),
    )

    assert patched.status_code == 200
    assert (
        patched.json()["status"],
        patched.json()["quantity"],
        patched.json()["unit_price_cents"],
    ) == ("shipped", 2, 200_000)
    assert my_orders(client, as_user("clienta"))[0]["status"] == "shipped"

    assert client.delete(f"/api/orders/{order_id}", headers=as_admin("gestora")).status_code == 204
    assert my_orders(client, as_user("clienta")) == []


def test_only_admins_edit_orders(
    client: TestClient, clienta: User, gestora: User, products: list[Product]
) -> None:
    order_id = buy(client, products[0].id, as_user("clienta")).json()["id"]
    url = f"/api/orders/{order_id}"

    assert (
        client.patch(url, json={"status": "cancelled"}, headers=as_user("clienta")).status_code
        == 403
    )
    assert client.delete(url, headers=as_user("clienta")).status_code == 403
    # Una administradora con la cookie normal tampoco.
    assert (
        client.patch(url, json={"status": "cancelled"}, headers=as_user("gestora")).status_code
        == 403
    )


def test_order_changes_are_validated(
    client: TestClient, clienta: User, gestora: User, products: list[Product]
) -> None:
    order_id = buy(client, products[0].id, as_user("clienta")).json()["id"]

    for bad in ({"status": "perdido"}, {"quantity": 0}, {"unit_price_cents": -1}):
        response = client.patch(f"/api/orders/{order_id}", json=bad, headers=as_admin("gestora"))
        assert response.status_code == 422
    missing = client.patch(
        "/api/orders/999", json={"status": "shipped"}, headers=as_admin("gestora")
    )
    assert missing.status_code == 404
