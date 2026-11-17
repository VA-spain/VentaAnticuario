"""Mensajes de la página de contacto.

La validación de verdad la hace la web antes de enviar; aquí solo se recortan espacios y se
comprueban longitudes para que nada rompa la base de datos.
"""

from fastapi import APIRouter, status

from app.deps import DbSession
from app.models import ContactMessage
from app.schemas import ContactIn, ContactOut

router = APIRouter(prefix="/api/contact", tags=["contacto"])


@router.post("", response_model=ContactOut, status_code=status.HTTP_201_CREATED)
def send_message(payload: ContactIn, db: DbSession) -> ContactOut:
    message = ContactMessage(
        name=payload.name,
        email=payload.email,
        subject=payload.subject or None,
        message=payload.message,
    )
    db.add(message)
    db.commit()
    return ContactOut(id=message.id)
