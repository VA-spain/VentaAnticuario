import Link from "next/link";
import { type ReactNode, Suspense } from "react";

import { ActiveLink } from "./active-link";
import { navLinkClass } from "./nav-style";

/**
 * Enlace del menú. Saber si es la página actual exige leer la URL, que en las rutas con
 * parámetros (/admin/users/[username]) solo se conoce al pedir la página: mientras tanto se
 * muestra el mismo enlace sin marcar.
 */
export function NavLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <Suspense
      fallback={
        <Link href={href} className={navLinkClass(false)}>
          {children}
        </Link>
      }
    >
      <ActiveLink href={href}>{children}</ActiveLink>
    </Suspense>
  );
}
