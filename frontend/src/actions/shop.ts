"use server";

import { refresh } from "next/cache";
import { redirect } from "next/navigation";

import { field } from "@/lib/form";
import { authFetch } from "@/lib/session";

function productIdFrom(formData: FormData): number {
  const productId = Number(field(formData, "productId"));
  if (!Number.isInteger(productId) || productId <= 0) {
    throw new Error("Pieza no válida.");
  }
  return productId;
}

/** Compra con un clic. Sin sesión, pide iniciarla; con ella, lleva al pedido en el portal. */
export async function buyProduct(formData: FormData): Promise<void> {
  const productId = productIdFrom(formData);
  const response = await authFetch(
    "/api/users/me/orders",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ product_id: productId }),
    },
    "/login?reason=buy",
  );
  if (!response.ok) {
    throw new Error(`El backend respondió ${response.status} al comprar.`);
  }
  const order = (await response.json()) as { id: number };
  redirect(`/account/orders?bought=${order.id}`);
}

/**
 * Marca o desmarca una pieza como favorita. `target` es «me» o, desde el portal de otro usuario,
 * su nombre (solo lo acepta el backend si quien lo pide es administrador).
 */
export async function setFavorite(formData: FormData): Promise<void> {
  const productId = productIdFrom(formData);
  const favorite = field(formData, "favorite") === "true";
  const target = field(formData, "target") || "me";
  const response = await authFetch(
    `/api/users/${encodeURIComponent(target)}/favorites/${productId}`,
    { method: favorite ? "PUT" : "DELETE" },
    "/login?reason=favorite",
  );
  if (!response.ok) {
    throw new Error(`El backend respondió ${response.status} al cambiar un favorito.`);
  }
  refresh();
}
