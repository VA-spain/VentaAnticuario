"""Catálogo de piezas."""

from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Product
from app.schemas import ProductOut

router = APIRouter(prefix="/api/products", tags=["catálogo"])


@router.get("", response_model=list[ProductOut])
def list_products(db: Annotated[Session, Depends(get_db)]) -> Sequence[Product]:
    return db.scalars(select(Product).order_by(Product.sort_order, Product.id)).all()
