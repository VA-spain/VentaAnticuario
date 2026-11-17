"""API de Venta Anticuario.

Arranque en local, desde la carpeta backend:  uv run uvicorn app.main:app --reload
"""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.routers import auth, products

app = FastAPI(
    title="Venta Anticuario API",
    version="0.1.0",
    description="Catálogo de piezas e inicio de sesión de Venta Anticuario.",
)
app.include_router(products.router)
app.include_router(auth.router)


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
