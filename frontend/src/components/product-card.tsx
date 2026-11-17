import Image from "next/image";

import { formatPrice } from "@/lib/format";
import type { Product } from "@/lib/products";

export function ProductCard({ product, eager }: { product: Product; eager: boolean }) {
  return (
    <article className="flex flex-col">
      {/* Marco cuadrado y foto entera, sin recortar: sirve igual para fotos altas y apaisadas. */}
      <div className="relative aspect-square overflow-hidden rounded-sm bg-white ring-1 ring-line">
        <Image
          src={product.image_path}
          alt={product.image_alt}
          fill
          sizes="(min-width: 1024px) 352px, (min-width: 640px) 46vw, 92vw"
          loading={eager ? "eager" : "lazy"}
          className="object-contain p-4"
        />
      </div>
      <p className="mt-5 text-xs font-medium uppercase tracking-[0.18em] text-brass">
        {product.category}
      </p>
      <h3 className="mt-1 font-display text-2xl font-semibold leading-tight">{product.name}</h3>
      <p className="mt-1 text-sm text-ink-soft">
        {product.period} · {product.origin}
      </p>
      <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-soft">{product.description}</p>
      <p className="mt-4 font-display text-2xl font-semibold">{formatPrice(product.price_cents)}</p>
    </article>
  );
}
