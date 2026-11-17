import "server-only";

import { cookies } from "next/headers";
import { notFound, redirect, unstable_rethrow } from "next/navigation";
import { cache } from "react";

import { backendFetch } from "./backend";
import type { SessionUser } from "./types";

/**
 * Cookie de sesión. Su valor es `nombre+0987654321` para un cliente y `0987654321+nombre` para
 * un administrador; el backend la interpreta y decide qué puede hacer cada uno.
 */
export const SESSION_COOKIE = "va_session";

export async function getSessionValue(): Promise<string | null> {
  return (await cookies()).get(SESSION_COOKIE)?.value || null;
}

/**
 * Usuario de la sesión actual, o null si no hay sesión válida.
 *
 * Lee la cookie, así que solo puede usarse en componentes que estén dentro de <Suspense>.
 * `cache` hace que la cabecera y la página compartan una sola consulta por petición.
 */
export const getCurrentUser = cache(async (): Promise<SessionUser | null> => {
  const session = await getSessionValue();
  if (!session) {
    return null;
  }
  try {
    const response = await backendFetch("/api/auth/me", {
      headers: { Authorization: `Bearer ${session}` },
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

/** Usuario de la sesión, o a /login si no hay. */
export async function requireUser(): Promise<SessionUser> {
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }
  return user;
}

/** Administrador de la sesión. A quien no lo es, la página no le existe. */
export async function requireAdmin(): Promise<SessionUser> {
  const user = await requireUser();
  if (!user.is_admin) {
    notFound();
  }
  return user;
}

type AuthInit = Omit<RequestInit, "headers"> & { headers?: Record<string, string> };

/**
 * Llama al backend con la cookie de sesión del navegador. Sin sesión, o si el backend la
 * rechaza, manda a la página de inicio de sesión.
 */
export async function authFetch(
  path: string,
  init: AuthInit = {},
  loginPath = "/login",
): Promise<Response> {
  const session = await getSessionValue();
  if (!session) {
    redirect(loginPath);
  }
  const response = await backendFetch(path, {
    ...init,
    headers: { ...init.headers, Authorization: `Bearer ${session}` },
  });
  if (response.status === 401) {
    redirect(loginPath);
  }
  return response;
}
