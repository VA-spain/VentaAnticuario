"""Los tests corren contra SQLite en memoria: no necesitan Docker ni tocan la base real."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.db import Base, get_db
from app.main import app
from app.models import Product, User
from app.rate_limit import LoginThrottle, get_login_throttle
from app.security import hash_password
from tests.factories import make_product

PASSWORD = "una-clave-de-prueba"


def as_user(username: str) -> dict[str, str]:
    """Cabecera con la cookie de un cliente, tal como la reenvía la web."""
    return {"Authorization": f"Bearer {username}+0987654321"}


def as_admin(username: str) -> dict[str, str]:
    """Cabecera con la cookie de administrador."""
    return {"Authorization": f"Bearer 0987654321+{username}"}


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def db(session_factory: sessionmaker[Session]) -> Iterator[Session]:
    with session_factory() as session:
        yield session


def _add_user(db: Session, username: str, *, is_admin: bool = False) -> User:
    user = User(username=username, password_hash=hash_password(PASSWORD), is_admin=is_admin)
    db.add(user)
    db.commit()
    return user


@pytest.fixture
def clienta(db: Session) -> User:
    return _add_user(db, "clienta")


@pytest.fixture
def cliente(db: Session) -> User:
    return _add_user(db, "cliente")


@pytest.fixture
def gestora(db: Session) -> User:
    """Una administradora."""
    return _add_user(db, "gestora", is_admin=True)


@pytest.fixture
def products(db: Session) -> list[Product]:
    items = [make_product("reloj", 0, price_cents=240_000), make_product("plato", 1)]
    db.add_all(items)
    db.commit()
    return items


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Iterator[TestClient]:
    def override_db() -> Iterator[Session]:
        with session_factory() as session:
            yield session

    throttle = LoginThrottle()
    # _env_file=None: los tests no leen el .env real del repositorio.
    settings = Settings(_env_file=None)
    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_login_throttle] = lambda: throttle
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
