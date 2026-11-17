import Link from "next/link";

import { logout } from "@/lib/actions";
import { getCurrentUser } from "@/lib/session";

import { NavLink } from "./nav-link";

/** Parte del menú que depende de la sesión. Lee la cookie: va siempre dentro de <Suspense>. */
export async function SessionNav() {
  const user = await getCurrentUser();

  if (!user) {
    return (
      <Link href="/login" className="btn btn-outline ml-2">
        Iniciar sesión
      </Link>
    );
  }

  return (
    <>
      <NavLink href="/signed-in">Mi cuenta</NavLink>
      <form action={logout} className="ml-2">
        <button type="submit" className="btn btn-outline">
          Cerrar sesión
        </button>
      </form>
    </>
  );
}

/** Hueco del mismo tamaño mientras se comprueba la sesión, para que el menú no dé un salto. */
export function SessionNavFallback() {
  return (
    <span aria-hidden="true" className="btn btn-outline invisible ml-2">
      Iniciar sesión
    </span>
  );
}
