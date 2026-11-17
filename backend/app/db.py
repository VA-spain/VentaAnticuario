"""Conexión a MySQL y sesión de base de datos por petición."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base de todas las tablas."""


@lru_cache
def get_engine() -> Engine:
    # pool_pre_ping: si MySQL cerró una conexión ociosa, se detecta y se reabre sola.
    return create_engine(get_settings().database_url(), pool_pre_ping=True, pool_recycle=3600)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), expire_on_commit=False)


def get_db() -> Iterator[Session]:
    with get_session_factory()() as session:
        yield session
