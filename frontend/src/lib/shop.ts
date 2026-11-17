import "server-only";

import { notFound, unstable_rethrow } from "next/navigation";

import { backendFetch } from "./backend";
import { authFetch, getSessionValue } from "./session";
import type { AdminUserRow, Order, Product, Profile } from "./types";

/** `target` es «me» (quien tiene la sesión) o el nombre de otro usuario (solo administradores). */
function userPath(target: string): string {
  return `/api/users/${encodeURIComponent(target)}`;
}

async function read<T>(response: Response, what: string): Promise<T> {
  // Un usuario que no existe, o que no es tuyo, simplemente no existe para ti.
  if (response.status === 403 || response.status === 404) {
    notFound();
  }
  if (!response.ok) {
    throw new Error(`El backend respondió ${response.status} al pedir ${what}.`);
  }
  return (await response.json()) as T;
}

export async function getOrders(target: string): Promise<Order[]> {
  return read(await authFetch(`${userPath(target)}/orders`), "los pedidos");
}

export async function getFavorites(target: string): Promise<Product[]> {
  return read(await authFetch(`${userPath(target)}/favorites`), "los favoritos");
}

export async function getProfile(target: string): Promise<Profile> {
  return read(await authFetch(userPath(target)), "los datos del usuario");
}

export async function getAdminUsers(): Promise<AdminUserRow[]> {
  return read(await authFetch("/api/users"), "la lista de usuarios");
}

/** Piezas favoritas de quien tiene la sesión. Si algo falla, ninguna: el catálogo se ve igual. */
export async function getMyFavoriteIds(): Promise<Set<number>> {
  const session = await getSessionValue();
  if (!session) {
    return new Set();
  }
  try {
    const response = await backendFetch("/api/users/me/favorites", {
      headers: { Authorization: `Bearer ${session}` },
    });
    if (!response.ok) {
      return new Set();
    }
    return new Set(((await response.json()) as Product[]).map((product) => product.id));
  } catch (error) {
    unstable_rethrow(error);
    console.error("No se pudieron leer los favoritos:", error);
    return new Set();
  }
}
