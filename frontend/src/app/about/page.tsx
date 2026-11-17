import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { getProducts } from "@/lib/products";

export const metadata: Metadata = {
  title: "Sobre nosotros",
  description:
    "Venta Anticuario es una tienda de antigüedades especializada en piezas de origen alemán.",
};

// Las licencias Creative Commons piden enlazar su texto junto al nombre del autor.
const LICENSE_URLS: Record<string, string> = {
  "CC0 1.0": "https://creativecommons.org/publicdomain/zero/1.0/deed.es",
  "CC BY 3.0": "https://creativecommons.org/licenses/by/3.0/deed.es",
  "CC BY 4.0": "https://creativecommons.org/licenses/by/4.0/deed.es",
  "CC BY-SA 3.0": "https://creativecommons.org/licenses/by-sa/3.0/deed.es",
  "CC BY-SA 4.0": "https://creativecommons.org/licenses/by-sa/4.0/deed.es",
  "CC BY-SA 2.0 DE": "https://creativecommons.org/licenses/by-sa/2.0/de/deed.es",
};

const headingClass = "mt-14 font-display text-3xl font-semibold";
const paragraphClass = "mt-4 leading-relaxed text-ink-soft";

export default function AboutPage() {
  return (
    <article className="mx-auto max-w-3xl px-5 py-16 sm:px-8 sm:py-24">
      <p className="eyebrow">Sobre nosotros</p>
      <h1 className="mt-4 font-display text-4xl font-semibold leading-[1.1] sm:text-6xl">
        Una tienda dedicada a las antigüedades alemanas
      </h1>
      <p className="mt-6 text-lg leading-relaxed text-ink-soft">
        Venta Anticuario reúne muebles, porcelana, relojes y objetos fabricados en Alemania entre
        el siglo XVIII y mediados del XX: piezas hechas para durar, con oficio y con historia.
      </p>

      <h2 className={headingClass}>Qué encontrarás</h2>
      <p className={paragraphClass}>
        El catálogo recorre los oficios que dieron fama a los talleres alemanes: la ebanistería
        sobria del Biedermeier, la porcelana de Meissen, los relojes tallados de la Selva Negra,
        el peltre modernista, los juguetes de hojalata de Märklin, el grabado y la mecánica de
        precisión de casas como Leitz o Adler.
      </p>

      <h2 className={headingClass}>Cómo presentamos cada pieza</h2>
      <p className={paragraphClass}>
        Cada ficha indica qué es el objeto, su época aproximada y su región de origen, y describe
        sus materiales y su estado en lenguaje llano. Si de una pieza no se sabe algo, no se
        afirma.
      </p>
      <p className={paragraphClass}>
        Puedes ver todas las piezas disponibles en el{" "}
        <Link href="/" className="text-oxblood underline underline-offset-4">
          catálogo
        </Link>
        .
      </p>

      <h2 id="creditos" className={`${headingClass} scroll-mt-8`}>
        Créditos de las fotografías
      </h2>
      <p className={paragraphClass}>
        Las fotografías del catálogo son imágenes de dominio público o de licencia libre
        procedentes de Wikimedia Commons, que ilustran cada tipo de pieza. Se han redimensionado
        para la web y, en algún caso, recortado.
      </p>
      <Suspense fallback={<p className={paragraphClass}>Cargando los créditos…</p>}>
        <ImageCredits />
      </Suspense>
    </article>
  );
}

/** Autor, licencia y original de cada foto, leídos del catálogo. */
async function ImageCredits() {
  const products = await getProducts();

  if (products === null) {
    return (
      <p role="status" className={paragraphClass}>
        Ahora mismo no podemos mostrar los créditos. Vuelve a intentarlo en unos minutos.
      </p>
    );
  }

  return (
    <ul className="mt-6 divide-y divide-line border-y border-line text-sm">
      {products.map((product) => (
        <li key={product.id} className="py-3">
          <span className="font-medium text-ink">{product.name}.</span>{" "}
          <span className="text-ink-soft">
            Foto: {product.image_author}. Licencia:{" "}
            {LICENSE_URLS[product.image_license] ? (
              <a
                href={LICENSE_URLS[product.image_license]}
                target="_blank"
                rel="noopener noreferrer license"
                className="underline underline-offset-4"
              >
                {product.image_license}
              </a>
            ) : (
              product.image_license
            )}
            .{" "}
            <a
              href={product.image_source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-oxblood underline underline-offset-4"
            >
              Ver el original
            </a>
          </span>
        </li>
      ))}
    </ul>
  );
}
