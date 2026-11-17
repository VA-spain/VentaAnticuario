import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-5 py-8 text-sm text-ink-soft sm:flex-row sm:px-8">
        <p>
          <span className="font-display text-lg text-ink">Venta Anticuario</span> · Antigüedades
          alemanas
        </p>
        <Link
          href="/about#creditos"
          className="underline decoration-line underline-offset-4 hover:text-oxblood"
        >
          Créditos de las fotografías
        </Link>
      </div>
    </footer>
  );
}
