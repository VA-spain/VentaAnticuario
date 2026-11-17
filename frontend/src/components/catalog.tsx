import { getProducts } from "@/lib/products";

import { ProductCard } from "./product-card";

const gridClass = "grid gap-x-8 gap-y-14 sm:grid-cols-2 lg:grid-cols-3";

/** Las piezas en venta. Pide el catálogo al backend: va siempre dentro de <Suspense>. */
export async function Catalog() {
  const products = await getProducts();

  if (products === null) {
    return (
      <p role="status" className="rounded-sm border border-line bg-paper-deep px-5 py-4 text-ink-soft">
        Ahora mismo no podemos mostrar el catálogo. Vuelve a intentarlo en unos minutos.
      </p>
    );
  }

  if (products.length === 0) {
    return <p className="text-ink-soft">Todavía no hay piezas en el catálogo.</p>;
  }

  return (
    <>
      <p className="mb-8 text-sm text-ink-soft">
        {products.length} {products.length === 1 ? "pieza" : "piezas"} a la venta
      </p>
      <div className={gridClass}>
        {products.map((product, index) => (
          // Las tres primeras fotos se ven nada más entrar: se cargan sin esperar al scroll.
          <ProductCard key={product.id} product={product} eager={index < 3} />
        ))}
      </div>
    </>
  );
}

/** Siluetas de las tarjetas mientras llega el catálogo. */
export function CatalogSkeleton() {
  return (
    <div className={gridClass} aria-busy="true" aria-label="Cargando el catálogo">
      {[0, 1, 2, 3, 4, 5].map((item) => (
        <div key={item} className="animate-pulse">
          <div className="aspect-square rounded-sm bg-paper-deep ring-1 ring-line" />
          <div className="mt-5 h-3 w-24 rounded-sm bg-paper-deep" />
          <div className="mt-3 h-6 w-3/4 rounded-sm bg-paper-deep" />
          <div className="mt-3 h-4 w-1/2 rounded-sm bg-paper-deep" />
        </div>
      ))}
    </div>
  );
}
