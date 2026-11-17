import { backendFetch } from "@/lib/backend";
import { field } from "@/lib/form";
import { seeOther, sessionSetCookie } from "@/lib/session-cookie";
import { normalizeUsername } from "@/lib/validation";

type SessionResponse = { cookie_value: string; expires_in_seconds: number };

/**
 * Recibe el formulario de /login. Es una ruta y no una acción de servidor porque tiene que escribir
 * la cabecera Set-Cookie a mano (ver lib/session-cookie.ts).
 */
export async function POST(request: Request): Promise<Response> {
  const form = await request.formData();
  const username = normalizeUsername(field(form, "username"));
  const password = field(form, "password");
  const back = (error: string) => seeOther(`/login?${new URLSearchParams({ error, username })}`);

  if (!username || !password) {
    return back("missing");
  }

  let response: Response;
  try {
    response = await backendFetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  } catch (error) {
    console.error("No se pudo contactar con el backend para iniciar sesión:", error);
    return back("server");
  }

  if (response.status === 401 || response.status === 422) {
    return back("credentials");
  }
  if (response.status === 429) {
    return back("throttled");
  }
  if (!response.ok) {
    console.error(`El backend respondió ${response.status} al iniciar sesión.`);
    return back("server");
  }

  const session = (await response.json()) as SessionResponse;
  return seeOther("/signed-in", sessionSetCookie(session.cookie_value, session.expires_in_seconds));
}
