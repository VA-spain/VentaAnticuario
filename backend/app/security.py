"""Contraseñas y tokens de sesión.

En la base de datos no se guarda ningún secreto utilizable:

- Contraseñas: hash Argon2id con sal aleatoria por usuario. No es reversible; para comprobar una
  contraseña se vuelve a calcular el hash y se compara.
- Tokens de sesión: 32 bytes aleatorios. Se guarda solo su SHA-256, de modo que leer la tabla de
  sesiones no permite suplantar a nadie. Aquí basta un hash rápido porque el token ya es aleatorio
  y largo; el hash lento (Argon2id) hace falta para contraseñas, que las elige una persona.
"""

import hashlib
import secrets
from functools import lru_cache

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

# Parámetros por defecto de argon2-cffi: Argon2id, 64 MiB de memoria, 3 pasadas (RFC 9106).
_hasher = PasswordHasher()


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
    """Hash contra el que se verifica cuando el email no existe.

    Así el login tarda lo mismo exista o no la cuenta, y el tiempo de respuesta no delata
    qué emails están registrados.
    """
    return _hasher.hash(secrets.token_urlsafe(16))


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
