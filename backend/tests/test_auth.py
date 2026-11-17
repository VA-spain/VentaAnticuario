import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.models import User
from tests.conftest import PASSWORD, as_admin, as_user


def register(client: TestClient, username: str, password: str = "clave-larga-1"):
    return client.post("/api/auth/register", json={"username": username, "password": password})


def login(client: TestClient, username: str, password: str = PASSWORD):
    return client.post("/api/auth/login", json={"username": username, "password": password})


# --- Registro ---------------------------------------------------------------------------------


def test_register_creates_the_user_and_signs_in(client: TestClient, db: Session) -> None:
    response = register(client, "  Ana.Maria ")

    assert response.status_code == 201
    body = response.json()
    assert body["cookie_value"] == "ana.maria+0987654321"
    assert body["expires_in_seconds"] == 480 * 60
    assert body["user"] == {
        "username": "ana.maria",
        "is_admin": False,
        "first_name": None,
        "last_name": None,
    }
    stored = db.scalar(select(User).where(User.username == "ana.maria"))
    assert stored is not None
    assert stored.password_hash.startswith("$argon2id$")
    assert "clave-larga-1" not in stored.password_hash
    assert stored.is_admin is False


def test_register_rejects_a_taken_username_ignoring_case(client: TestClient, clienta: User) -> None:
    response = register(client, "CLIENTA")

    assert response.status_code == 409
    assert response.json() == {"detail": "Ese nombre de usuario ya existe."}


@pytest.mark.parametrize(
    "username",
    ["ab", "1ana", "ana maria", "ana+0987654321", "0987654321", "ñandú", "a" * 31, "me"],
)
def test_register_rejects_invalid_usernames(client: TestClient, username: str) -> None:
    response = register(client, username)

    assert response.status_code == 422
    assert "nombre de usuario" in response.json()["detail"]


def test_register_rejects_a_short_password(client: TestClient) -> None:
    response = register(client, "ana", password="corta")

    assert response.status_code == 422
    assert "al menos 8" in response.json()["detail"]


def test_username_availability(client: TestClient, clienta: User) -> None:
    def check(username: str) -> dict:
        return client.get("/api/auth/username-available", params={"username": username}).json()

    assert check("nueva") == {"username": "nueva", "available": True, "reason": None}
    assert check(" Clienta ") == {
        "username": "clienta",
        "available": False,
        "reason": "Ese nombre de usuario ya existe.",
    }
    invalid = check("1x")
    assert invalid["available"] is False
    assert "nombre de usuario" in invalid["reason"]


# --- Inicio de sesión -------------------------------------------------------------------------


def test_login_gives_the_user_cookie(client: TestClient, clienta: User, db: Session) -> None:
    response = login(client, "clienta")

    assert response.status_code == 200
    assert response.json()["cookie_value"] == "clienta+0987654321"
    assert response.json()["user"]["is_admin"] is False
    db.expire_all()
    assert db.scalar(select(User).where(User.username == "clienta")).last_login_at is not None


def test_login_gives_the_admin_cookie_to_an_admin(client: TestClient, gestora: User) -> None:
    body = login(client, "gestora").json()

    assert body["cookie_value"] == "0987654321+gestora"
    assert body["user"]["is_admin"] is True


def test_login_ignores_case_and_spaces(client: TestClient, clienta: User) -> None:
    assert login(client, "  CLIENTA ").status_code == 200


def test_wrong_password_and_unknown_user_give_the_same_answer(
    client: TestClient, clienta: User
) -> None:
    wrong_password = login(client, "clienta", password="no-es-esta")
    unknown_user = login(client, "nadie")

    assert wrong_password.status_code == unknown_user.status_code == 401
    assert wrong_password.json() == unknown_user.json()
    assert wrong_password.json() == {"detail": "Nombre de usuario o contraseña incorrectos."}


def test_inactive_user_cannot_sign_in(client: TestClient, clienta: User, db: Session) -> None:
    clienta.is_active = False
    db.commit()

    assert login(client, "clienta").status_code == 401


def test_empty_fields_are_rejected(client: TestClient) -> None:
    assert login(client, "clienta", password="").status_code == 422
    assert login(client, "").status_code == 422


# --- La cookie --------------------------------------------------------------------------------


def test_me_reflects_the_cookie(client: TestClient, clienta: User, gestora: User) -> None:
    assert client.get("/api/auth/me", headers=as_user("clienta")).json() == {
        "username": "clienta",
        "is_admin": False,
        "first_name": None,
        "last_name": None,
    }
    assert client.get("/api/auth/me", headers=as_admin("gestora")).json()["is_admin"] is True
    # Una administradora con la cookie normal navega como cliente.
    assert client.get("/api/auth/me", headers=as_user("gestora")).json()["is_admin"] is False


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Bearer clienta"},
        {"Authorization": "Bearer clienta+1234"},
        {"Authorization": "clienta+0987654321"},
        as_user("nadie"),
        as_user("CLIENTA"),
        # Cookie de administrador para quien no lo es.
        as_admin("clienta"),
    ],
)
def test_me_rejects_invalid_cookies(client: TestClient, clienta: User, headers: dict) -> None:
    assert client.get("/api/auth/me", headers=headers).status_code == 401


def test_cookie_stops_working_when_the_user_is_deactivated(
    client: TestClient, clienta: User, db: Session
) -> None:
    clienta.is_active = False
    db.commit()

    assert client.get("/api/auth/me", headers=as_user("clienta")).status_code == 401


# --- Freno de intentos ------------------------------------------------------------------------


def test_too_many_failures_block_even_the_right_password(client: TestClient, clienta: User) -> None:
    for _ in range(5):
        assert login(client, "clienta", password="no-es-esta").status_code == 401

    blocked = login(client, "clienta")

    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0
    assert "Demasiados intentos" in blocked.json()["detail"]


def test_block_is_per_address_so_the_owner_can_still_sign_in(
    client: TestClient, clienta: User
) -> None:
    for _ in range(5):
        login(client, "clienta", password="no-es-esta")
    assert login(client, "clienta").status_code == 429

    # Mismas dependencias (misma base y mismo freno), pero desde otra dirección.
    with TestClient(app, client=("203.0.113.9", 50000)) as other_address:
        assert login(other_address, "clienta").status_code == 200


def test_successful_login_resets_the_failure_count(client: TestClient, clienta: User) -> None:
    for _ in range(4):
        login(client, "clienta", password="no-es-esta")
    assert login(client, "clienta").status_code == 200

    for _ in range(4):
        assert login(client, "clienta", password="no-es-esta").status_code == 401
    assert login(client, "clienta").status_code == 200
