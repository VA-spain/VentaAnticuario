"use server";

import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { backendFetch } from "@/lib/backend";
import { SESSION_COOKIE } from "@/lib/session";

export type UsernameCheck = {
  /** null: no se ha podido comprobar ahora; se comprobará al enviar el formulario. */
  available: boolean | null;
  message: string | null;
};

/** Comprueba, mientras se escribe en el registro, si un nombre de usuario está libre. */
export async function checkUsername(username: string): Promise<UsernameCheck> {
  try {
    const query = new URLSearchParams({ username: username.slice(0, 100) });
    const response = await backendFetch(`/api/auth/username-available?${query}`);
    if (!response.ok) {
      return { available: null, message: null };
    }
    const body = (await response.json()) as { available: boolean; reason: string | null };
    return { available: body.available, message: body.reason };
  } catch (error) {
    console.error("No se pudo comprobar el nombre de usuario:", error);
    return { available: null, message: null };
  }
}

export async function logout(): Promise<void> {
  // La sesión vive solo en la cookie: cerrarla es borrarla. Path=/ explícito, porque sin él el
  // navegador la buscaría en la carpeta de la página desde la que se pulsa el botón.
  (await cookies()).set(SESSION_COOKIE, "", { path: "/", maxAge: 0 });
  redirect("/");
}
