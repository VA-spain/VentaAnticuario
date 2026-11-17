import "server-only";

import { SESSION_COOKIE } from "./session";

const COOKIE_VALUE = /^[A-Za-z0-9._+-]+$/;

/** En producción la cookie solo viaja por HTTPS. SESSION_COOKIE_SECURE=false lo desactiva. */
function cookieIsSecure(): boolean {
  const configured = process.env.SESSION_COOKIE_SECURE;
  return configured ? configured !== "false" : process.env.NODE_ENV === "production";
}

/**
 * Cabecera Set-Cookie de la sesión, escrita a mano para que el valor quede literal
 * (`nombre+0987654321`): `cookies().set()` de Next.js lo codificaría como `nombre%2B0987654321`.
 */
export function sessionSetCookie(value: string, maxAgeSeconds: number): string {
  if (!COOKIE_VALUE.test(value)) {
    throw new Error("El backend devolvió un valor de cookie con caracteres no válidos.");
  }
  const parts = [
    `${SESSION_COOKIE}=${value}`,
    "Path=/",
    `Max-Age=${Math.floor(maxAgeSeconds)}`,
    "HttpOnly",
    "SameSite=Lax",
  ];
  if (cookieIsSecure()) {
    parts.push("Secure");
  }
  return parts.join("; ");
}

/** Respuesta 303: tras un POST, el navegador pide la página de destino con un GET. */
export function seeOther(location: string, setCookie?: string): Response {
  const headers = new Headers({ Location: location });
  if (setCookie) {
    headers.append("Set-Cookie", setCookie);
  }
  return new Response(null, { status: 303, headers });
}
