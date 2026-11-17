from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.main import app
from app.models import User, UserSession, utcnow
from app.security import hash_token
from tests.conftest import DEMO_EMAIL, DEMO_PASSWORD


def do_login(client: TestClient, email: str = DEMO_EMAIL, password: str = DEMO_PASSWORD):
    return client.post("/api/auth/login", json={"email": email, "password": password})


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_login_returns_a_token_and_the_user(client: TestClient, user: User) -> None:
    response = do_login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["user"] == {"email": DEMO_EMAIL, "full_name": "Clienta"}
    assert body["expires_in_seconds"] == 480 * 60
    assert len(body["token"]) >= 43


def test_database_never_holds_the_password_or_the_token(
    client: TestClient, user: User, db: Session
) -> None:
    token = do_login(client).json()["token"]

    stored_user = db.scalar(select(User).where(User.email == DEMO_EMAIL))
    stored_session = db.scalar(select(UserSession))
    assert stored_user.password_hash.startswith("$argon2id$")
    assert DEMO_PASSWORD not in stored_user.password_hash
    assert stored_session.token_hash == hash_token(token)
    assert stored_session.token_hash != token
    assert stored_user.last_login_at is not None


def test_wrong_password_and_unknown_email_give_the_same_answer(
    client: TestClient, user: User
) -> None:
    wrong_password = do_login(client, password="no-es-esta")
    unknown_email = do_login(client, email="nadie@example.com")

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json() == {"detail": "Email o contraseña incorrectos."}


def test_inactive_user_cannot_sign_in(client: TestClient, user: User, db: Session) -> None:
    user.is_active = False
    db.commit()

    assert do_login(client).status_code == 401


def test_email_ignores_case_and_surrounding_spaces(client: TestClient, user: User) -> None:
    assert do_login(client, email=f"  {DEMO_EMAIL.upper()} ").status_code == 200


def test_empty_fields_are_rejected_before_touching_the_database(client: TestClient) -> None:
    assert do_login(client, password="").status_code == 422
    assert do_login(client, email="").status_code == 422


def test_me_requires_a_valid_token(client: TestClient, user: User) -> None:
    token = do_login(client).json()["token"]

    assert client.get("/api/auth/me", headers=bearer(token)).json() == {
        "email": DEMO_EMAIL,
        "full_name": "Clienta",
    }
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=bearer("inventado")).status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": token}).status_code == 401


def test_expired_session_is_rejected_and_removed(
    client: TestClient, user: User, db: Session
) -> None:
    token = do_login(client).json()["token"]
    session = db.scalar(select(UserSession))
    session.expires_at = utcnow() - timedelta(seconds=1)
    db.commit()

    assert client.get("/api/auth/me", headers=bearer(token)).status_code == 401
    db.expire_all()
    assert db.scalar(select(UserSession)) is None


def test_session_stops_working_when_the_user_is_deactivated(
    client: TestClient, user: User, db: Session
) -> None:
    token = do_login(client).json()["token"]
    user.is_active = False
    db.commit()

    assert client.get("/api/auth/me", headers=bearer(token)).status_code == 401


def test_logout_invalidates_only_that_session(client: TestClient, user: User) -> None:
    first = do_login(client).json()["token"]
    second = do_login(client).json()["token"]

    assert client.post("/api/auth/logout", headers=bearer(first)).status_code == 204
    assert client.get("/api/auth/me", headers=bearer(first)).status_code == 401
    assert client.get("/api/auth/me", headers=bearer(second)).status_code == 200
    assert client.post("/api/auth/logout").status_code == 401


def test_login_clears_expired_sessions(client: TestClient, user: User, db: Session) -> None:
    db.add(
        UserSession(user_id=user.id, token_hash="a" * 64, expires_at=utcnow() - timedelta(days=1))
    )
    db.commit()

    do_login(client)

    db.expire_all()
    assert [s.token_hash for s in db.scalars(select(UserSession))] != ["a" * 64]
    assert len(db.scalars(select(UserSession)).all()) == 1


def test_too_many_failures_block_even_the_right_password(client: TestClient, user: User) -> None:
    for _ in range(5):
        assert do_login(client, password="no-es-esta").status_code == 401

    blocked = do_login(client)

    assert blocked.status_code == 429
    assert int(blocked.headers["Retry-After"]) > 0
    assert "Demasiados intentos" in blocked.json()["detail"]


def test_block_is_per_address_so_the_owner_can_still_sign_in(
    client: TestClient, user: User
) -> None:
    for _ in range(5):
        do_login(client, password="no-es-esta")
    assert do_login(client).status_code == 429

    # Mismas dependencias (misma base y mismo freno), pero la petición llega desde otra dirección.
    with TestClient(app, client=("203.0.113.9", 50000)) as other_address:
        assert do_login(other_address).status_code == 200


def test_successful_login_resets_the_failure_count(client: TestClient, user: User) -> None:
    for _ in range(4):
        do_login(client, password="no-es-esta")
    assert do_login(client).status_code == 200

    for _ in range(4):
        assert do_login(client, password="no-es-esta").status_code == 401
    assert do_login(client).status_code == 200
