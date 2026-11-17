"""Tareas de mantenimiento. Desde la carpeta backend:

uv run python -m app.cli init-db              crea las tablas, el catálogo y el usuario de prueba
uv run python -m app.cli create-user EMAIL    crea un usuario (pide la contraseña sin mostrarla)
uv run python -m app.cli set-password EMAIL   cambia la contraseña de un usuario
"""

import argparse
import getpass
import sys

from app.config import get_settings
from app.db import Base, get_engine, get_session_factory
from app.seed import ensure_demo_user, load_product_seeds, seed_products
from app.users import create_user, set_password


def init_db() -> None:
    Base.metadata.create_all(get_engine())
    with get_session_factory()() as db:
        created, updated = seed_products(db, load_product_seeds())
        demo_email = ensure_demo_user(db, get_settings())
        db.commit()
    print(f"Tablas listas. Catálogo: {created} piezas nuevas, {updated} actualizadas.")
    if demo_email:
        print(f"Usuario de prueba: {demo_email} (contraseña: DEMO_USER_PASSWORD del .env).")
    else:
        print("Sin usuario de prueba: DEMO_USER_PASSWORD está vacío en el .env.")


def ask_password() -> str:
    password = getpass.getpass("Contraseña: ")
    if password != getpass.getpass("Repite la contraseña: "):
        raise ValueError("Las contraseñas no coinciden.")
    return password


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m app.cli", description="Venta Anticuario")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser(
        "init-db", help="crea las tablas y carga el catálogo y el usuario de prueba"
    )
    new_user = commands.add_parser("create-user", help="crea un usuario")
    new_user.add_argument("email")
    new_user.add_argument("--name", help="nombre que se muestra al iniciar sesión")
    change = commands.add_parser("set-password", help="cambia la contraseña de un usuario")
    change.add_argument("email")
    args = parser.parse_args(argv)

    try:
        if args.command == "init-db":
            init_db()
            return 0
        password = ask_password()
        with get_session_factory()() as db:
            if args.command == "create-user":
                user = create_user(db, email=args.email, password=password, full_name=args.name)
                done = "creado"
            else:
                user = set_password(db, email=args.email, password=password)
                done = "actualizado, con sus sesiones cerradas"
            db.commit()
        print(f"Usuario {user.email} {done}.")
        return 0
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
