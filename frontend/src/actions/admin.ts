"use server";

import { refresh } from "next/cache";

import { field } from "@/lib/form";
import { authFetch } from "@/lib/session";
import { ORDER_STATUS_LABELS } from "@/lib/types";

function orderIdFrom(formData: FormData): number {
  const orderId = Number(field(formData, "orderId"));
  if (!Number.isInteger(orderId) || orderId <= 0) {
    throw new Error("Pedido no válido.");
  }
  return orderId;
}

/** Cambia cantidad, precio por unidad o estado de un pedido. Solo administradores. */
export async function updateOrder(formData: FormData): Promise<void> {
  const quantity = Number(field(formData, "quantity"));
  const price = Number(field(formData, "price").replace(",", "."));
  const status = field(formData, "status");

  const patch: Record<string, number | string> = {};
  if (Number.isInteger(quantity) && quantity >= 1) {
    patch.quantity = quantity;
  }
  if (Number.isFinite(price) && price >= 0) {
    patch.unit_price_cents = Math.round(price * 100);
  }
  if (Object.hasOwn(ORDER_STATUS_LABELS, status)) {
    patch.status = status;
  }

  const response = await authFetch(`/api/orders/${orderIdFrom(formData)}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!response.ok) {
    throw new Error(`El backend respondió ${response.status} al modificar el pedido.`);
  }
  refresh();
}

export async function deleteOrder(formData: FormData): Promise<void> {
  const response = await authFetch(`/api/orders/${orderIdFrom(formData)}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`El backend respondió ${response.status} al borrar el pedido.`);
  }
  refresh();
}
