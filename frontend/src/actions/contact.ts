"use server";

import { backendFetch } from "@/lib/backend";

export type ContactInput = { name: string; email: string; subject: string; message: string };

export type ContactResult = { ok: true } | { ok: false; error: string };

/**
 * Guarda un mensaje de la página de contacto. La validación la hace el formulario en el
 * navegador antes de llamar aquí; de momento el servidor no la repite.
 */
export async function sendContactMessage(input: ContactInput): Promise<ContactResult> {
  try {
    const response = await backendFetch("/api/contact", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(input),
    });
    if (response.ok) {
      return { ok: true };
    }
    console.error(`El backend respondió ${response.status} al guardar un mensaje de contacto.`);
    return { ok: false, error: "No hemos podido enviar el mensaje. Revísalo y vuelve a probar." };
  } catch (error) {
    console.error("No se pudo contactar con el backend para guardar el mensaje:", error);
    return {
      ok: false,
      error: "No hemos podido conectar con el servidor. Inténtalo de nuevo en unos minutos.",
    };
  }
}
