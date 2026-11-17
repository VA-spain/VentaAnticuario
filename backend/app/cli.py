"""Tareas de mantenimiento. Desde la carpeta backend:

uv run python -m app.cli init-db                crea las tablas que falten, el catálogo y los
                                                usuarios de prueba del .env
uv run python -m app.cli reset-db --yes         BORRA todas las tablas y vuelve a crearlas
uv run python -m app.cli create-user NOMBRE     crea un cliente (pide la contraseña sin mostrarla)
uv run python -m app.cli create-user NOMBRE --admin    crea un administrador
uv run python -m app.cli set-password NOMBRE    cambia la contraseña de un usuario
"""

import argparse
import getpass
import sys

from sqlalchemy import MetaData

from app.config import get_settings
from app.db import Base, get_engine, get_session_factory
from app.seed import ensure_seed_users, load_product_seeds, seed_products
from app.users import create_user, set_password


def init_db() -> None:
    Base.metadata.create_all(get_engine())
    with get_session_factory()() as db:
        created, updated = seed_products(db, load_product_seeds())
        seeded = ensure_seed_users(db, get_settings())
        db.commit()
    print(f"Tablas listas. Catálogo: {created} piezas nuevas, {updated} actualizadas.")
    if seeded:
        print(f"Usuarios de prueba: {', '.join(seeded)} (contraseñas en el .env).")
    else:
        print("Sin usuarios de prueba: no hay contraseñas para ellos en el .env.")


def reset_db() -> None:
    """Borra TODAS las tablas de la base de datos (también las que ya no usa el código)."""
    engine = get_engine()
    existing = MetaData()
    existing.reflect(bind=engine)
    existing.drop_all(bind=engine)
    print(f"Borradas {len(existing.tables)} tablas: {', '.join(sorted(existing.tables))}.")
    init_db()


def ask_password() -> str:
    password = getpass.getpass("Contraseña: ")
    if password != getpass.getpass("Repite la contraseña: "):
        raise ValueError("Las contraseñas no coinciden.")
    return password


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="Venta Anticuario")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("init-db", help="crea las tablas, el catálogo y los usuarios de prueba")
    reset = commands.add_parser("reset-db", help="borra todas las tablas y las vuelve a crear")
    reset.add_argument("--yes", action="store_true", help="confirma que quieres borrarlo todo")
    new_user = commands.add_parser("create-user", help="crea un usuario")
    new_user.add_argument("username")
    new_user.add_argument("--admin", action="store_true", help="con permisos de administrador")
    change = commands.add_parser("set-password", help="cambia la contraseña de un usuario")
    change.add_argument("username")
    args = parser.parse_args(argv)

    try:
        if args.command == "init-db":
            init_db()
            return 0
        if args.command == "reset-db":
            if not args.yes:
                print("reset-db borra todos los datos. Repite la orden con --yes.", file=sys.stderr)
                return 1
            reset_db()
            return 0
        password = ask_password()
        with get_session_factory()() as db:
            if args.command == "create-user":
                user = create_user(
                    db, username=args.username, password=password, is_admin=args.admin
                )
                done = "creado como administrador" if args.admin else "creado"
            else:
                user = set_password(db, username=args.username, password=password)
                done = "actualizado"
            db.commit()
        print(f"Usuario {user.username} {done}.")
        return 0
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
