import "server-only";

import { cookies } from "next/headers";
import { unstable_rethrow } from "next/navigation";
import { cache } from "react";

import { backendFetch } from "./backend";

/** Cookie que guarda el token de sesión. Es httpOnly: el JavaScript de la página no la ve. */
export const SESSION_COOKIE = "va_session";

export type SessionUser = {
  email: string;
  full_name: string | null;
};

/**
 * Usuario de la sesión actual, o null si no hay sesión válida.
 *
 * La validez la decide el backend en cada petición, no la mera presencia de la cookie: una
 * sesión caducada o cerrada deja de valer aunque el navegador conserve la cookie.
 *
 * Lee la cookie, así que solo puede usarse en componentes que estén dentro de <Suspense>.
 * `cache` hace que la cabecera y la página compartan una sola consulta por petición.
 */
export const getCurrentUser = cache(async (): Promise<SessionUser | null> => {
  const token = (await cookies()).get(SESSION_COOKIE)?.value;
  if (!token) {
    return null;
  }
  try {
    const response = await backendFetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      return null;
    }
    return (await response.json()) as SessionUser;
  } catch (error) {
    unstable_rethrow(error);
    console.error("No se pudo comprobar la sesión en el backend:", error);
    return null;
  }
});
