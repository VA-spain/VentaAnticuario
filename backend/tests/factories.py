from app.models import Product


def make_product(slug: str, sort_order: int = 0, *, price_cents: int = 120_000) -> Product:
    return Product(
        slug=slug,
        name=f"Pieza {slug}",
        category="Relojes",
        period="c. 1900",
        origin="Selva Negra",
        description="Descripción de prueba.",
        price_cents=price_cents,
        image_path=f"/products/{slug}.jpg",
        image_alt="Foto de prueba",
        image_author="Autora de prueba",
        image_license="CC0 1.0",
        image_source_url="https://commons.wikimedia.org/wiki/File:Prueba.jpg",
        sort_order=sort_order,
    )
