from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ContactMessage


def test_contact_message_is_stored(client: TestClient, db: Session) -> None:
    response = client.post(
        "/api/contact",
        json={
            "name": "  Marta ",
            "email": "marta@example.com",
            "subject": "",
            "message": "¿Hacéis envíos a Portugal?",
        },
    )

    assert response.status_code == 201
    stored = db.scalar(select(ContactMessage))
    assert stored is not None
    assert response.json() == {"id": stored.id}
    assert (stored.name, stored.email, stored.subject, stored.message) == (
        "Marta",
        "marta@example.com",
        None,
        "¿Hacéis envíos a Portugal?",
    )


def test_contact_needs_no_session_but_rejects_empty_fields(client: TestClient) -> None:
    response = client.post(
        "/api/contact", json={"name": "   ", "email": "marta@example.com", "message": "Hola"}
    )

    assert response.status_code == 422
