import Link from "next/link";

import { formatDateTime, formatDay, formatPrice } from "@/lib/format";
import { getFavorites, getOrders, getProfile } from "@/lib/shop";

type Props = { target: string; base: string; welcome: boolean };

export async function PortalOverview({ target, base, welcome }: Props) {
  const [orders, favorites, profile] = await Promise.all([
    getOrders(target),
    getFavorites(target),
    getProfile(target),
  ]);
  const spent = orders
    .filter((order) => order.status !== "cancelled")
    .reduce((sum, order) => sum + order.unit_price_cents * order.quantity, 0);
  const completed = [
    profile.first_name,
    profile.last_name,
    profile.email,
    profile.passport_number,
    profile.card_number,
  ].filter(Boolean).length;

  const cards = [
    {
      href: `${base}/orders`,
      title: "Compras",
      value: String(orders.length),
      detail: orders.length ? `${formatPrice(spent)} en total` : "Todavía no hay compras",
    },
    {
      href: `${base}/favorites`,
      title: "Favoritos",
      value: String(favorites.length),
      detail: favorites.length === 1 ? "pieza guardada" : "piezas guardadas",
    },
    {
      href: `${base}/settings`,
      title: "Configuración",
      value: `${completed}/5`,
      detail: "datos completados",
    },
  ];

  return (
    <>
      {welcome && (
        <p role="status" className="notice-ok mb-8">
          Tu cuenta y tu portal están listos. Ya puedes comprar y guardar tus piezas favoritas.
        </p>
      )}
      <div className="grid gap-5 sm:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="group rounded-sm border border-line bg-white p-6 transition-colors hover:border-oxblood"
          >
            <p className="text-sm font-medium text-ink-soft group-hover:text-oxblood">
              {card.title}
            </p>
            <p className="mt-2 font-display text-4xl font-semibold">{card.value}</p>
            <p className="mt-1 text-sm text-ink-soft">{card.detail}</p>
          </Link>
        ))}
      </div>
      <p className="mt-8 text-sm text-ink-soft">
        Usuario <strong className="font-medium text-ink">{profile.username}</strong>
        {profile.is_admin ? " (administrador)" : ""} · cuenta creada el{" "}
        {formatDay(profile.created_at)}
        {profile.last_login_at ? ` · último acceso: ${formatDateTime(profile.last_login_at)}` : ""}
      </p>
    </>
  );
}
