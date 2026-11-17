"use server";

import { refresh } from "next/cache";

import { field } from "@/lib/form";
import { authFetch } from "@/lib/session";

export type ProfileState = { status: "idle" | "saved" | "error"; message: string | null };

const PROFILE_FIELDS = [
  "first_name",
  "last_name",
  "email",
  "passport_number",
  "card_number",
  "card_expiry",
  "card_cvv",
] as const;

/** Guarda la página de configuración. `target` es «me» o, para un administrador, otro usuario. */
export async function updateProfile(
  _previous: ProfileState,
  formData: FormData,
): Promise<ProfileState> {
  const target = field(formData, "target") || "me";
  const payload = Object.fromEntries(
    PROFILE_FIELDS.map((name) => [name, field(formData, name).trim()]),
  );

  const response = await authFetch(`/api/users/${encodeURIComponent(target)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (response.status === 422) {
    return { status: "error", message: "Algún dato es demasiado largo. Revísalo y vuelve a guardar." };
  }
  if (!response.ok) {
    console.error(`El backend respondió ${response.status} al guardar la configuración.`);
    return { status: "error", message: "No hemos podido guardar los datos. Inténtalo de nuevo." };
  }

  refresh();
  return { status: "saved", message: "Datos guardados." };
}
