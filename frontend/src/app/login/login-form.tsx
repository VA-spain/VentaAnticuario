"use client";

import { useActionState } from "react";

import { login, type LoginState } from "@/lib/actions";

const initialState: LoginState = { error: null, email: "" };

const inputClass =
  "mt-2 w-full rounded-sm border border-line bg-white px-3.5 py-2.5 text-ink placeholder:text-ink-soft/60 focus:border-oxblood";

export function LoginForm() {
  const [state, formAction, pending] = useActionState(login, initialState);

  return (
    <form action={formAction} className="mt-8 flex flex-col gap-5">
      {state.error && (
        <p
          role="alert"
          className="rounded-sm border border-oxblood/40 bg-oxblood/5 px-4 py-3 text-sm text-oxblood-deep"
        >
          {state.error}
        </p>
      )}

      <label className="text-sm font-medium">
        Email
        <input
          type="email"
          name="email"
          autoComplete="username"
          required
          maxLength={254}
          defaultValue={state.email}
          placeholder="tu@email.com"
          className={inputClass}
        />
      </label>

      <label className="text-sm font-medium">
        Contraseña
        <input
          type="password"
          name="password"
          autoComplete="current-password"
          required
          maxLength={1024}
          className={inputClass}
        />
      </label>

      <button type="submit" disabled={pending} className="btn btn-primary mt-2 py-3">
        {pending ? "Entrando…" : "Iniciar sesión"}
      </button>
    </form>
  );
}
