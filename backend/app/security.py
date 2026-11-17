"""Contraseñas y valor de la cookie de sesión.

Contraseñas: en la base de datos solo se guarda el hash Argon2id con una sal aleatoria por
usuario. No es reversible; para comprobar una contraseña se vuelve a calcular el hash y se compara.

Cookie de sesión, tal como se pidió:

- usuario normal: ``nombre+0987654321``
- administrador:  ``0987654321+nombre``

OJO: no lleva firma ni ningún secreto, así que cualquiera que conozca un nombre de usuario puede
fabricar su cookie (y la de un administrador, si conoce su nombre). Es una decisión consciente para
ir rápido; hay que sustituirla por una sesión firmada antes de tener clientes reales.
"""

import secrets
from functools import lru_cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

# Parámetros por defecto de argon2-cffi: Argon2id, 64 MiB de memoria, 3 pasadas (RFC 9106).
_hasher = PasswordHasher()

SESSION_MARK = "0987654321"


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def needs_rehash(password_hash: str) -> bool:
    """True si el hash se calculó con parámetros más débiles que los actuales."""
    return _hasher.check_needs_rehash(password_hash)


@lru_cache
def dummy_password_hash() -> str:
    """Hash contra el que se verifica cuando el usuario no existe.

    Así el login tarda lo mismo exista o no la cuenta.
    """
    return _hasher.hash(secrets.token_urlsafe(16))


def make_session_value(username: str, *, is_admin: bool) -> str:
    return f"{SESSION_MARK}+{username}" if is_admin else f"{username}+{SESSION_MARK}"


def parse_session_value(value: str) -> tuple[str, bool] | None:
    """Devuelve (nombre de usuario, es_admin) o None si el valor no tiene ninguna de las dos formas.

    Los nombres de usuario empiezan por una letra y no llevan «+», así que las dos formas no
    pueden confundirse.
    """
    if value.startswith(f"{SESSION_MARK}+"):
        username, is_admin = value.removeprefix(f"{SESSION_MARK}+"), True
    elif value.endswith(f"+{SESSION_MARK}"):
        username, is_admin = value.removesuffix(f"+{SESSION_MARK}"), False
    else:
        return None
    return (username, is_admin) if username else None
