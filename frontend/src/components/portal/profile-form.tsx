"use client";

import { type ComponentProps, useActionState } from "react";

import { type ProfileState, updateProfile } from "@/actions/account";
import type { Profile } from "@/lib/types";

const initialState: ProfileState = { status: "idle", message: null };

type FieldProps = Omit<ComponentProps<"input">, "name" | "defaultValue" | "className"> & {
  label: string;
  name: keyof Profile;
  profile: Profile;
  className?: string;
};

function Field({ label, name, profile, className = "", ...input }: FieldProps) {
  const value = profile[name];
  return (
    <label className={`field ${className}`}>
      {label}
      <input
        name={name}
        defaultValue={typeof value === "string" ? value : ""}
        className="input"
        {...input}
      />
    </label>
  );
}

/** Configuración del usuario. `target` es «me» o, para un administrador, el cliente que edita. */
export function ProfileForm({ profile, target }: { profile: Profile; target: string }) {
  const [state, formAction, pending] = useActionState(updateProfile, initialState);

  return (
    <form action={formAction} className="flex max-w-3xl flex-col gap-10">
      <input type="hidden" name="target" value={target} />

      <fieldset className="grid gap-5 sm:grid-cols-2">
        <legend className="mb-5 font-display text-2xl font-semibold">Datos personales</legend>
        <Field label="Nombre" name="first_name" profile={profile} maxLength={80} autoComplete="given-name" />
        <Field
          label="Apellidos"
          name="last_name"
          profile={profile}
          maxLength={120}
          autoComplete="family-name"
        />
        <Field
          label="Correo electrónico"
          name="email"
          type="email"
          profile={profile}
          maxLength={254}
          autoComplete="email"
        />
        <Field
          label="Número de pasaporte"
          name="passport_number"
          profile={profile}
          maxLength={40}
          autoComplete="off"
        />
      </fieldset>

      {/* autoComplete="off": que el navegador no rellene aquí la tarjeta real de quien prueba. */}
      <fieldset className="grid gap-5 sm:grid-cols-[2fr_1fr_1fr]">
        <legend className="mb-5 font-display text-2xl font-semibold">Tarjeta bancaria</legend>
        <Field
          label="Número de tarjeta"
          name="card_number"
          profile={profile}
          inputMode="numeric"
          maxLength={32}
          autoComplete="off"
        />
        <Field
          label="Caducidad"
          name="card_expiry"
          profile={profile}
          placeholder="MM/AA"
          maxLength={7}
          autoComplete="off"
        />
        <Field
          label="CVV"
          name="card_cvv"
          profile={profile}
          inputMode="numeric"
          maxLength={4}
          autoComplete="off"
        />
      </fieldset>

      {state.message && (
        <p
          role={state.status === "error" ? "alert" : "status"}
          className={state.status === "error" ? "notice-error" : "notice-ok"}
        >
          {state.message}
        </p>
      )}

      <div>
        <button type="submit" disabled={pending} className="btn btn-primary">
          {pending ? "Guardando…" : "Guardar cambios"}
        </button>
      </div>
    </form>
  );
}
