import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Página no encontrada",
};

export default function NotFound() {
  return (
    <section className="mx-auto flex max-w-xl flex-col items-center px-5 py-20 text-center sm:py-28">
      <p className="eyebrow">Error 404</p>
      <h1 className="mt-4 font-display text-4xl font-semibold sm:text-5xl">Página no encontrada</h1>
      <p className="mt-4 text-lg text-ink-soft">
        La página que buscas no existe o ha cambiado de sitio.
      </p>
      <Link href="/" className="btn btn-primary mt-10">
        Volver al catálogo
      </Link>
    </section>
  );
}
