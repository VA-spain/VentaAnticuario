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
from app.models import User
from app.rate_limit import LoginThrottle, get_login_throttle
from app.security import hash_password

DEMO_EMAIL = "clienta@example.com"
DEMO_PASSWORD = "una-clave-larga-de-prueba"


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


@pytest.fixture
def user(db: Session) -> User:
    user = User(email=DEMO_EMAIL, full_name="Clienta", password_hash=hash_password(DEMO_PASSWORD))
    db.add(user)
    db.commit()
    return user


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
