import Image from "next/image";
import Link from "next/link";

import { deleteOrder, updateOrder } from "@/actions/admin";
import { formatDateTime, formatPrice } from "@/lib/format";
import { getOrders } from "@/lib/shop";
import { ORDER_STATUS_LABELS, type Order, type OrderStatus } from "@/lib/types";

import { SubmitButton } from "../submit-button";

type Props = { target: string; canEdit: boolean; highlight?: number };

/** Compras de un usuario. Con `canEdit` (administrador) cada pedido se puede modificar o borrar. */
export async function OrdersView({ target, canEdit, highlight }: Props) {
  const orders = await getOrders(target);

  if (orders.length === 0) {
    return canEdit ? (
      <p className="text-ink-soft">Este cliente todavía no ha comprado nada.</p>
    ) : (
      <p className="notice">
        Todavía no has comprado nada.{" "}
        <Link href="/" className="font-medium text-oxblood underline underline-offset-4">
          Echa un vistazo al catálogo
        </Link>
        .
      </p>
    );
  }

  const bought = highlight ? orders.find((order) => order.id === highlight) : undefined;
  const total = orders
    .filter((order) => order.status !== "cancelled")
    .reduce((sum, order) => sum + order.unit_price_cents * order.quantity, 0);

  return (
    <>
      {bought && (
        <p role="status" className="notice-ok mb-6">
          Compra realizada: «{bought.product.name}» por {formatPrice(bought.unit_price_cents)}. Ya
          la tienes en tu lista de compras.
        </p>
      )}
      <p className="text-sm text-ink-soft">
        {orders.length} {orders.length === 1 ? "pedido" : "pedidos"} · {formatPrice(total)} en
        total, sin contar los cancelados
      </p>
      <ul className="mt-4 divide-y divide-line border-y border-line">
        {orders.map((order) => (
          <OrderRow
            key={order.id}
            order={order}
            canEdit={canEdit}
            highlighted={order.id === highlight}
          />
        ))}
      </ul>
    </>
  );
}

function OrderRow({
  order,
  canEdit,
  highlighted,
}: {
  order: Order;
  canEdit: boolean;
  highlighted: boolean;
}) {
  return (
    <li
      className={`flex flex-col gap-4 py-5 sm:flex-row sm:items-start ${
        highlighted ? "-mx-3 bg-brass/10 px-3" : ""
      }`}
    >
      <div className="relative size-20 shrink-0 overflow-hidden rounded-sm bg-white ring-1 ring-line">
        <Image
          src={order.product.image_path}
          alt=""
          fill
          sizes="80px"
          className="object-contain p-1.5"
        />
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-display text-xl font-semibold leading-tight">{order.product.name}</p>
        <p className="mt-1 text-sm text-ink-soft">
          Pedido n.º {order.id} · {formatDateTime(order.created_at)}
        </p>
        {canEdit ? (
          <AdminOrderForm order={order} />
        ) : (
          <p className="mt-2 flex flex-wrap items-center gap-2 text-sm">
            {order.quantity} × {formatPrice(order.unit_price_cents)}
            <StatusBadge status={order.status} />
          </p>
        )}
      </div>
      {!canEdit && (
        <p className="font-display text-xl font-semibold sm:text-right">
          {formatPrice(order.quantity * order.unit_price_cents)}
        </p>
      )}
    </li>
  );
}

function StatusBadge({ status }: { status: OrderStatus }) {
  const tone =
    status === "cancelled"
      ? "bg-oxblood/10 text-oxblood-deep"
      : "bg-paper-deep text-ink-soft ring-1 ring-line";
  return (
    <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${tone}`}>
      {ORDER_STATUS_LABELS[status]}
    </span>
  );
}

function AdminOrderForm({ order }: { order: Order }) {
  return (
    <form action={updateOrder} className="mt-3 flex flex-wrap items-end gap-3">
      <input type="hidden" name="orderId" value={order.id} />
      <label className="field w-24">
        Cantidad
        <input
          type="number"
          name="quantity"
          min={1}
          max={999}
          step={1}
          required
          defaultValue={order.quantity}
          className="input"
        />
      </label>
      <label className="field w-36">
        Precio unidad (€)
        <input
          type="number"
          name="price"
          min={0}
          step="0.01"
          required
          defaultValue={(order.unit_price_cents / 100).toFixed(2)}
          className="input"
        />
      </label>
      <label className="field w-40">
        Estado
        <select name="status" defaultValue={order.status} className="input">
          {Object.entries(ORDER_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </label>
      <SubmitButton className="btn btn-primary" pendingLabel="Guardando…">
        Guardar
      </SubmitButton>
      <SubmitButton
        formAction={deleteOrder}
        className="btn btn-outline"
        confirmMessage={`¿Borrar el pedido n.º ${order.id}? No se puede deshacer.`}
      >
        Borrar
      </SubmitButton>
    </form>
  );
}
