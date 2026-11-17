import { Suspense } from "react";

import { Catalog, CatalogSkeleton } from "@/components/catalog";

export default function HomePage() {
  return (
    <>
      <section className="border-b border-line bg-paper-deep">
        <div className="mx-auto max-w-6xl px-5 py-16 sm:px-8 sm:py-24">
          <p className="eyebrow">Antigüedades alemanas</p>
          <h1 className="mt-4 max-w-3xl font-display text-4xl font-semibold leading-[1.1] sm:text-6xl">
            Piezas con historia, elegidas una a una
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-relaxed text-ink-soft">
            Muebles, porcelana, relojes y objetos de los siglos XVIII al XX llegados de Alemania.
          </p>
        </div>
      </section>

      <section
        aria-labelledby="catalogo"
        className="mx-auto max-w-6xl px-5 py-14 sm:px-8 sm:py-20"
      >
        <h2 id="catalogo" className="font-display text-3xl font-semibold sm:text-4xl">
          Catálogo
        </h2>
        <div className="mt-3">
          {/* El catálogo se pide al backend en cada visita; mientras llega se ven las siluetas. */}
          <Suspense fallback={<CatalogSkeleton />}>
            <Catalog />
          </Suspense>
        </div>
      </section>
    </>
  );
}
