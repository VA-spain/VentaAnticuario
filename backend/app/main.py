"""API de Venta Anticuario.

Arranque en local, desde la carpeta backend:  uv run uvicorn app.main:app --reload
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers import auth, contact, favorites, orders, products, users

app = FastAPI(
    title="Venta Anticuario API",
    version="0.2.0",
    description="Catálogo, cuentas de cliente, compras, favoritos, administración y contacto.",
)
app.include_router(products.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(favorites.router)
app.include_router(contact.router)


@app.get("/api/health", tags=["estado"])
def health(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La base de datos no responde.",
        ) from error
    return {"status": "ok"}
