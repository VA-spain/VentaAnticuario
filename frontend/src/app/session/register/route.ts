import { backendFetch } from "@/lib/backend";
import { field } from "@/lib/form";
import { seeOther, sessionSetCookie } from "@/lib/session-cookie";
import {
  MAX_PASSWORD_LENGTH,
  MIN_PASSWORD_LENGTH,
  USERNAME_PATTERN,
  normalizeUsername,
} from "@/lib/validation";

type SessionResponse = { cookie_value: string; expires_in_seconds: number };

/**
 * Recibe el formulario de /register: crea la cuenta, deja la sesión iniciada y lleva al portal
 * recién creado. Es una ruta para poder escribir la cookie literal (ver lib/session-cookie.ts).
 */
export async function POST(request: Request): Promise<Response> {
  const form = await request.formData();
  const username = normalizeUsername(field(form, "username"));
  const password = field(form, "password");
  const back = (error: string) =>
    seeOther(`/register?${new URLSearchParams({ error, username })}`);

  if (!USERNAME_PATTERN.test(username)) {
    return back("username");
  }
  if (password.length < MIN_PASSWORD_LENGTH) {
    return back("password-short");
  }
  if (password.length > MAX_PASSWORD_LENGTH) {
    return back("password-long");
  }

  let response: Response;
  try {
    response = await backendFetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  } catch (error) {
    console.error("No se pudo contactar con el backend para registrar al usuario:", error);
    return back("server");
  }

  if (response.status === 409) {
    return back("taken");
  }
  if (response.status === 422) {
    return back("invalid");
  }
  if (!response.ok) {
    console.error(`El backend respondió ${response.status} al registrar al usuario.`);
    return back("server");
  }

  const session = (await response.json()) as SessionResponse;
  return seeOther(
    "/account?welcome=1",
    sessionSetCookie(session.cookie_value, session.expires_in_seconds),
  );
}
