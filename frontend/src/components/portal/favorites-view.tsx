import Image from "next/image";
import Link from "next/link";

import { setFavorite } from "@/actions/shop";
import { formatPrice } from "@/lib/format";
import { getProducts } from "@/lib/products";
import { getFavorites } from "@/lib/shop";

import { ProductCard } from "../product-card";
import { SubmitButton } from "../submit-button";

type Props = { target: string; canEdit: boolean };

/** Favoritos de un usuario: como tarjetas del catálogo para él, como lista editable para el admin. */
export async function FavoritesView({ target, canEdit }: Props) {
  if (!canEdit) {
    const favorites = await getFavorites(target);
    if (favorites.length === 0) {
      return (
        <p className="notice">
          Todavía no has guardado ninguna pieza. Pulsa el corazón de cualquier pieza del{" "}
          <Link href="/" className="font-medium text-oxblood underline underline-offset-4">
            catálogo
          </Link>{" "}
          y aparecerá aquí.
        </p>
      );
    }
    return (
      <div className="grid gap-x-8 gap-y-14 sm:grid-cols-2 lg:grid-cols-3">
        {favorites.map((product) => (
          <ProductCard key={product.id} product={product} signedIn isFavorite />
        ))}
      </div>
    );
  }

  const [favorites, products] = await Promise.all([getFavorites(target), getProducts()]);
  const favoriteIds = new Set(favorites.map((product) => product.id));
  const others = (products ?? []).filter((product) => !favoriteIds.has(product.id));

  return (
    <>
      {favorites.length === 0 ? (
        <p className="text-ink-soft">Este cliente no tiene piezas en favoritos.</p>
      ) : (
        <ul className="divide-y divide-line border-y border-line">
          {favorites.map((product) => (
            <li key={product.id} className="flex items-center gap-4 py-4">
              <div className="relative size-16 shrink-0 overflow-hidden rounded-sm bg-white ring-1 ring-line">
                <Image
                  src={product.image_path}
                  alt=""
                  fill
                  sizes="64px"
                  className="object-contain p-1"
                />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-medium">{product.name}</p>
                <p className="text-sm text-ink-soft">{formatPrice(product.price_cents)}</p>
              </div>
              <form action={setFavorite}>
                <input type="hidden" name="productId" value={product.id} />
                <input type="hidden" name="favorite" value="false" />
                <input type="hidden" name="target" value={target} />
                <SubmitButton className="btn btn-outline btn-sm" pendingLabel="Quitando…">
                  Quitar
                </SubmitButton>
              </form>
            </li>
          ))}
        </ul>
      )}

      {others.length > 0 && (
        <form action={setFavorite} className="mt-8 flex flex-wrap items-end gap-3">
          <input type="hidden" name="favorite" value="true" />
          <input type="hidden" name="target" value={target} />
          <label className="field min-w-64 flex-1">
            Añadir una pieza a sus favoritos
            <select name="productId" required defaultValue="" className="input">
              <option value="" disabled>
                Elige una pieza…
              </option>
              {others.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </label>
          <SubmitButton className="btn btn-primary" pendingLabel="Añadiendo…">
            Añadir
          </SubmitButton>
        </form>
      )}
    </>
  );
}
