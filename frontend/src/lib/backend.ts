import "server-only";

// Dirección del backend en Python. Solo la usa el servidor de Next.js: el navegador nunca
// habla con el backend directamente. Con 127.0.0.1 y no «localhost», porque Node resuelve
// «localhost» primero por IPv6 y el backend escucha en IPv4.
const BACKEND_URL = (process.env.BACKEND_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");

const TIMEOUT_MS = 8_000;

/** Llama al backend y corta la espera si no contesta a tiempo. */
export function backendFetch(path: string, init: RequestInit = {}): Promise<Response> {
  return fetch(`${BACKEND_URL}${path}`, {
    ...init,
    signal: init.signal ?? AbortSignal.timeout(TIMEOUT_MS),
  });
}
