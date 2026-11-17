"use server";

import { cookies, headers } from "next/headers";
import { redirect } from "next/navigation";

import { backendFetch } from "./backend";
import { SESSION_COOKIE } from "./session";

export type LoginState = {
  error: string | null;
  /** El email escrito, para no obligar a teclearlo otra vez tras un error. */
  email: string;
};

type LoginResponse = {
  token: string;
  expires_in_seconds: number;
};

const WRONG_CREDENTIALS = "Email o contraseña incorrectos.";

function field(formData: FormData, name: string): string {
  const value = formData.get(name);
  return typeof value === "string" ? value : "";
}

/** En producción la cookie solo viaja por HTTPS. SESSION_COOKIE_SECURE=false lo desactiva. */
function cookieIsSecure(): boolean {
  const configured = process.env.SESSION_COOKIE_SECURE;
  return configured ? configured !== "false" : process.env.NODE_ENV === "production";
}

export async function login(_previous: LoginState, formData: FormData): Promise<LoginState> {
  const email = field(formData, "email").trim();
  const password = field(formData, "password");

  if (!email || !password) {
    return { error: "Escribe tu email y tu contraseña.", email };
  }
  if (email.length > 254 || password.length > 1024) {
    return { error: WRONG_CREDENTIALS, email };
  }

  // La dirección de quien inicia sesión se pasa al backend, que la usa para frenar los intentos.
  const forwardedFor = (await headers()).get("x-forwarded-for");

  let response: Response;
  try {
    response = await backendFetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(forwardedFor ? { "X-Forwarded-For": forwardedFor } : {}),
      },
      body: JSON.stringify({ email, password }),
    });
  } catch (error) {
    console.error("No se pudo contactar con el backend para iniciar sesión:", error);
    return {
      error: "No hemos podido conectar con el servidor. Inténtalo de nuevo en unos minutos.",
      email,
    };
  }

  if (response.status === 401) {
    return { error: WRONG_CREDENTIALS, email };
  }
  if (response.status === 429) {
    return {
      error: "Demasiados intentos fallidos. Espera unos minutos y vuelve a probar.",
      email,
    };
  }
  if (!response.ok) {
    console.error(`El backend respondió ${response.status} al iniciar sesión.`);
    return { error: "No hemos podido iniciar la sesión. Inténtalo de nuevo.", email };
  }

  const session = (await response.json()) as LoginResponse;
  (await cookies()).set(SESSION_COOKIE, session.token, {
    httpOnly: true,
    sameSite: "lax",
    secure: cookieIsSecure(),
    path: "/",
    maxAge: session.expires_in_seconds,
  });

  // Fuera de cualquier try/catch: redirect funciona lanzando una excepción.
  redirect("/signed-in");
}

export async function logout(): Promise<void> {
  const cookieStore = await cookies();
  const token = cookieStore.get(SESSION_COOKIE)?.value;

  if (token) {
    try {
      await backendFetch("/api/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch (error) {
      // Si el backend no contesta, la cookie se borra igualmente y la sesión caduca sola.
      console.error("No se pudo cerrar la sesión en el backend:", error);
    }
    cookieStore.delete(SESSION_COOKIE);
  }

  redirect("/");
}
