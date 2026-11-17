from app.security import hash_password, hash_token, new_session_token, verify_password


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


def test_session_token_is_stored_as_sha256() -> None:
    token = new_session_token()

    assert len(token) >= 43  # 32 bytes aleatorios en base64 url
    assert new_session_token() != token
    assert len(hash_token(token)) == 64
    assert token not in hash_token(token)
    assert hash_token(token) == hash_token(token)
