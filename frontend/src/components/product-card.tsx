import Image from "next/image";
import Link from "next/link";

import { buyProduct, setFavorite } from "@/actions/shop";
import { formatPrice } from "@/lib/format";
import type { Product } from "@/lib/types";

import { HeartIcon } from "./icons";
import { SubmitButton } from "./submit-button";

type Props = {
  product: Product;
  signedIn: boolean;
  isFavorite: boolean;
  eager?: boolean;
};

export function ProductCard({ product, signedIn, isFavorite, eager = false }: Props) {
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
        <FavoriteToggle product={product} signedIn={signedIn} isFavorite={isFavorite} />
      </div>
      <p className="mt-5 text-xs font-medium uppercase tracking-[0.18em] text-brass">
        {product.category}
      </p>
      <h3 className="mt-1 font-display text-2xl font-semibold leading-tight">{product.name}</h3>
      <p className="mt-1 text-sm text-ink-soft">
        {product.period} · {product.origin}
      </p>
      <p className="mt-3 flex-1 text-sm leading-relaxed text-ink-soft">{product.description}</p>
      <div className="mt-4 flex items-center justify-between gap-4">
        <p className="font-display text-2xl font-semibold">{formatPrice(product.price_cents)}</p>
        {signedIn ? (
          <form action={buyProduct}>
            <input type="hidden" name="productId" value={product.id} />
            <SubmitButton className="btn btn-primary" pendingLabel="Comprando…">
              Comprar
            </SubmitButton>
          </form>
        ) : (
          // Solo los usuarios registrados compran: sin sesión, primero hay que iniciarla.
          <Link href="/login?reason=buy" className="btn btn-primary">
            Comprar
          </Link>
        )}
      </div>
    </article>
  );
}

const heartClass =
  "flex size-10 cursor-pointer items-center justify-center rounded-full bg-white/90 text-oxblood shadow-sm ring-1 ring-line transition-colors hover:bg-white disabled:cursor-wait";

function FavoriteToggle({
  product,
  signedIn,
  isFavorite,
}: {
  product: Product;
  signedIn: boolean;
  isFavorite: boolean;
}) {
  if (!signedIn) {
    return (
      <Link
        href="/login?reason=favorite"
        aria-label={`Guardar «${product.name}» en favoritos (hay que iniciar sesión)`}
        className={`absolute right-3 top-3 ${heartClass}`}
      >
        <HeartIcon filled={false} />
      </Link>
    );
  }
  return (
    <form action={setFavorite} className="absolute right-3 top-3">
      <input type="hidden" name="productId" value={product.id} />
      <input type="hidden" name="favorite" value={String(!isFavorite)} />
      <SubmitButton
        aria-pressed={isFavorite}
        aria-label={
          isFavorite
            ? `Quitar «${product.name}» de favoritos`
            : `Guardar «${product.name}» en favoritos`
        }
        className={heartClass}
      >
        <HeartIcon filled={isFavorite} />
      </SubmitButton>
    </form>
  );
}
