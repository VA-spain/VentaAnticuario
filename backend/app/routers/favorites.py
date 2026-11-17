"""Piezas favoritas de cada usuario. Añadir y quitar son idempotentes."""

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.deps import DbSession, TargetUser
from app.models import Favorite, Product
from app.schemas import ProductOut

router = APIRouter(prefix="/api/users", tags=["favoritos"])


@router.get("/{username}/favorites", response_model=list[ProductOut])
def list_favorites(target: TargetUser, db: DbSession) -> list[Product]:
    favorites = db.scalars(
        select(Favorite)
        .where(Favorite.user_id == target.id)
        .order_by(Favorite.created_at.desc(), Favorite.id.desc())
    ).all()
    return [favorite.product for favorite in favorites]


@router.put("/{username}/favorites/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def add_favorite(product_id: int, target: TargetUser, db: DbSession) -> Response:
    if db.get(Product, product_id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe esa pieza.")
    already = db.scalar(
        select(Favorite.id).where(Favorite.user_id == target.id, Favorite.product_id == product_id)
    )
    if already is None:
        db.add(Favorite(user_id=target.id, product_id=product_id))
        try:
            db.commit()
        except IntegrityError:
            # Un doble clic llegó antes: la pieza ya está en favoritos.
            db.rollback()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{username}/favorites/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_favorite(product_id: int, target: TargetUser, db: DbSession) -> Response:
    db.execute(
        delete(Favorite).where(Favorite.user_id == target.id, Favorite.product_id == product_id)
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
