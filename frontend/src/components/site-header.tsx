import Link from "next/link";
import { Suspense } from "react";

import { NavLink } from "./nav-link";
import { SessionNav, SessionNavFallback } from "./session-nav";

export function SiteHeader() {
  return (
    <header className="border-b border-line">
      <div className="mx-auto flex max-w-6xl flex-col items-center gap-3 px-5 py-4 sm:flex-row sm:justify-between sm:px-8">
        <Link href="/" className="font-display text-2xl font-semibold tracking-wide sm:text-3xl">
          Venta Anticuario
        </Link>
        <nav
          aria-label="Principal"
          className="flex flex-wrap items-center justify-center gap-y-2 text-sm"
        >
          <NavLink href="/">Catálogo</NavLink>
          <NavLink href="/about">Sobre nosotros</NavLink>
          <Suspense fallback={<SessionNavFallback />}>
            <SessionNav />
          </Suspense>
        </nav>
      </div>
    </header>
  );
}
