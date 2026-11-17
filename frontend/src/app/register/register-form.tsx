"use client";

import { usePendingSubmit } from "@/components/use-pending-submit";
import { useUrlParams } from "@/components/use-url-params";
import { pick } from "@/lib/form";
import { MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH, USERNAME_HINT } from "@/lib/validation";

import { UsernameField } from "./username-field";

const ERRORS: Record<string, string> = {
  username: `Ese nombre de usuario no vale. ${USERNAME_HINT}`,
  "password-short": `La contraseña debe tener al menos ${MIN_PASSWORD_LENGTH} caracteres.`,
  "password-long": `La contraseña no puede pasar de ${MAX_PASSWORD_LENGTH} caracteres.`,
  taken: "Ese nombre de usuario ya existe. Prueba con otro.",
  invalid: "Revisa el nombre de usuario y la contraseña.",
  server: "No hemos podido conectar con el servidor. Inténtalo de nuevo en unos minutos.",
};

/**
 * Se envía con un POST normal a /session/register, que crea la cuenta y lleva al portal. Si algo
 * falla, vuelve aquí con el motivo y el nombre elegido en la URL.
 */
export function RegisterForm() {
  const pending = usePendingSubmit();
  const params = useUrlParams();
  const error = pick(ERRORS, params.get("error") ?? undefined);
  const username = params.get("username") ?? "";

  return (
    <form
      method="post"
      action="/session/register"
      onSubmit={pending.start}
      className="mt-8 flex flex-col gap-5"
    >
      {error && (
        <p role="alert" className="notice-error">
          {error}
        </p>
      )}

      {/* La clave cambia solo si la URL trae un nombre (tras un error): entonces se rellena. */}
      <UsernameField key={username} defaultValue={username} />

      <label className="field">
        Contraseña
        <input
          type="password"
          name="password"
          autoComplete="new-password"
          required
          minLength={MIN_PASSWORD_LENGTH}
          maxLength={MAX_PASSWORD_LENGTH}
          aria-describedby="password-hint"
          className="input"
        />
        <span id="password-hint" className="field-hint">
          Al menos {MIN_PASSWORD_LENGTH} caracteres.
        </span>
      </label>

      <button type="submit" disabled={pending.active} className="btn btn-primary mt-2 py-3">
        {pending.active ? "Creando tu cuenta…" : "Crear cuenta"}
      </button>
    </form>
  );
}
