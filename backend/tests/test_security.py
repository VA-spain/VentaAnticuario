import pytest

from app.security import (
    hash_password,
    make_session_value,
    parse_session_value,
    verify_password,
)


def test_password_hash_is_argon2id_and_salted() -> None:
    first = hash_password("la misma contraseña")
    second = hash_password("la misma contraseña")

    assert first.startswith("$argon2id$")
    assert "la misma contraseña" not in first
    # Sal aleatoria: la misma contraseña nunca da dos veces el mismo hash.
    assert first != second


def test_verify_password_accepts_only_the_right_password() -> None:
    stored = hash_password("correcta-123")

    assert verify_password(stored, "correcta-123") is True
    assert verify_password(stored, "Correcta-123") is False
    assert verify_password(stored, "") is False


def test_verify_password_rejects_a_value_that_is_not_a_hash() -> None:
    assert verify_password("texto-plano", "texto-plano") is False


def test_session_values_have_the_requested_shape() -> None:
    assert make_session_value("ana", is_admin=False) == "ana+0987654321"
    assert make_session_value("ana", is_admin=True) == "0987654321+ana"


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ana+0987654321", ("ana", False)),
        ("0987654321+ana", ("ana", True)),
        ("ana", None),
        ("+0987654321", None),
        ("0987654321+", None),
        ("ana+1234", None),
        ("", None),
    ],
)
def test_parse_session_value(value: str, expected: tuple[str, bool] | None) -> None:
    assert parse_session_value(value) == expected


@pytest.mark.parametrize("username", ["ana", "luis.m", "x_y-z"])
@pytest.mark.parametrize("is_admin", [True, False])
def test_session_values_round_trip(username: str, is_admin: bool) -> None:
    value = make_session_value(username, is_admin=is_admin)

    assert parse_session_value(value) == (username, is_admin)
