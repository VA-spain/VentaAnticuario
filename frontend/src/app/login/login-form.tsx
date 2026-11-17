"use client";

import { usePendingSubmit } from "@/components/use-pending-submit";
import { useUrlParams } from "@/components/use-url-params";
import { pick } from "@/lib/form";

const ERRORS: Record<string, string> = {
  missing: "Escribe tu nombre de usuario y tu contraseña.",
  credentials: "Nombre de usuario o contraseña incorrectos.",
  throttled: "Demasiados intentos fallidos. Espera unos minutos y vuelve a probar.",
  server: "No hemos podido conectar con el servidor. Inténtalo de nuevo en unos minutos.",
};

const REASONS: Record<string, string> = {
  buy: "Para comprar hay que iniciar sesión. Si aún no tienes cuenta, créala en un momento.",
  favorite: "Inicia sesión para guardar piezas en favoritos.",
};

/**
 * Se envía con un POST normal a /session/login, que deja la cookie y lleva a /signed-in. Si algo
 * falla, vuelve aquí con el motivo y el nombre de usuario en la URL.
 */
export function LoginForm() {
  const pending = usePendingSubmit();
  const params = useUrlParams();
  const error = pick(ERRORS, params.get("error") ?? undefined);
  const notice = pick(REASONS, params.get("reason") ?? undefined);
  const username = params.get("username") ?? "";

  return (
    <form
      method="post"
      action="/session/login"
      onSubmit={pending.start}
      className="mt-8 flex flex-col gap-5"
    >
      {notice && <p className="notice">{notice}</p>}
      {error && (
        <p role="alert" className="notice-error">
          {error}
        </p>
      )}

      <label className="field">
        Nombre de usuario
        <input
          // La clave cambia solo si la URL trae un nombre (tras un error): entonces se rellena.
          key={username}
          name="username"
          autoComplete="username"
          autoCapitalize="none"
          spellCheck={false}
          required
          maxLength={30}
          defaultValue={username}
          className="input"
        />
      </label>

      <label className="field">
        Contraseña
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          required
          maxLength={1024}
          className="input"
        />
      </label>

      <button type="submit" disabled={pending.active} className="btn btn-primary mt-2 py-3">
        {pending.active ? "Entrando…" : "Iniciar sesión"}
      </button>
    </form>
  );
}
