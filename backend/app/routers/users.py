"""Usuarios: la lista del administrador y los datos de configuración de cada uno."""

from fastapi import APIRouter
from sqlalchemy import func, select

from app.deps import AdminDep, DbSession, TargetUser
from app.models import Favorite, Order, User
from app.schemas import AdminUserOut, ProfileIn, ProfileOut

router = APIRouter(prefix="/api/users", tags=["usuarios"])


@router.get("", response_model=list[AdminUserOut])
def list_users(_admin: AdminDep, db: DbSession) -> list[AdminUserOut]:
    orders_count = (
        select(func.count(Order.id))
        .where(Order.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    favorites_count = (
        select(func.count(Favorite.id))
        .where(Favorite.user_id == User.id)
        .correlate(User)
        .scalar_subquery()
    )
    rows = db.execute(
        select(User, orders_count, favorites_count).order_by(User.created_at.desc(), User.id.desc())
    ).all()
    return [
        AdminUserOut(
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            orders_count=orders,
            favorites_count=favorites,
        )
        for user, orders, favorites in rows
    ]


@router.get("/{username}", response_model=ProfileOut)
def get_profile(target: TargetUser) -> User:
    return target


@router.put("/{username}", response_model=ProfileOut)
def update_profile(payload: ProfileIn, target: TargetUser, db: DbSession) -> User:
    """Guarda los siete datos de configuración. Un dato vacío se borra."""
    for field, value in payload.model_dump().items():
        setattr(target, field, value or None)
    db.commit()
    return target
