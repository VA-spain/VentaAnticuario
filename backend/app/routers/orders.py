"""Compras. Cada clic en «Comprar» crea un pedido; el administrador puede corregirlo o borrarlo."""

from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import AdminDep, DbSession, TargetUser
from app.models import Order, Product
from app.schemas import OrderIn, OrderOut, OrderPatch

router = APIRouter(prefix="/api", tags=["pedidos"])


@router.get("/users/{username}/orders", response_model=list[OrderOut])
def list_orders(target: TargetUser, db: DbSession) -> Sequence[Order]:
    return db.scalars(
        select(Order)
        .where(Order.user_id == target.id)
        .order_by(Order.created_at.desc(), Order.id.desc())
    ).all()


@router.post(
    "/users/{username}/orders", response_model=OrderOut, status_code=status.HTTP_201_CREATED
)
def create_order(payload: OrderIn, target: TargetUser, db: DbSession) -> Order:
    product = db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe esa pieza.")
    # De momento el stock es ilimitado: no se comprueba disponibilidad.
    order = Order(
        user_id=target.id,
        product_id=product.id,
        quantity=1,
        unit_price_cents=product.price_cents,
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


def _get_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No existe ese pedido.")
    return order


@router.patch("/orders/{order_id}", response_model=OrderOut)
def update_order(order_id: int, payload: OrderPatch, _admin: AdminDep, db: DbSession) -> Order:
    order = _get_order(db, order_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(order, field, value)
    db.commit()
    db.refresh(order)
    return order


@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, _admin: AdminDep, db: DbSession) -> Response:
    db.delete(_get_order(db, order_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
