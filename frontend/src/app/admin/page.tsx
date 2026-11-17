import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { formatDay } from "@/lib/format";
import { requireAdmin } from "@/lib/session";
import { getAdminUsers } from "@/lib/shop";

export const metadata: Metadata = {
  title: "Administración",
  robots: { index: false },
};

export default function AdminPage() {
  return (
    <section className="mx-auto max-w-6xl px-5 py-12 sm:px-8 sm:py-16">
      <Suspense
        fallback={
          <p role="status" className="text-ink-soft">
            Cargando los usuarios…
          </p>
        }
      >
        <UsersList />
      </Suspense>
    </section>
  );
}

const cell = "px-4 py-3";

/** Todos los usuarios del sistema, con acceso al portal de cada uno. */
async function UsersList() {
  await requireAdmin();
  const users = await getAdminUsers();

  return (
    <>
      <p className="eyebrow">Administración</p>
      <h1 className="mt-3 font-display text-4xl font-semibold sm:text-5xl">Usuarios</h1>
      <p className="mt-4 max-w-2xl text-ink-soft">
        {users.length} {users.length === 1 ? "cuenta" : "cuentas"}. Entra en el portal de cualquiera
        para ver y modificar sus pedidos, sus favoritos y sus datos.
      </p>

      <div className="mt-8 overflow-x-auto rounded-sm border border-line bg-white">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="border-b border-line bg-paper-deep text-xs uppercase tracking-wider text-ink-soft">
            <tr>
              <th className={`${cell} font-medium`}>Usuario</th>
              <th className={`${cell} font-medium`}>Nombre</th>
              <th className={`${cell} font-medium`}>Correo</th>
              <th className={`${cell} text-right font-medium`}>Compras</th>
              <th className={`${cell} text-right font-medium`}>Favoritos</th>
              <th className={`${cell} font-medium`}>Alta</th>
              <th className={cell}>
                <span className="sr-only">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {users.map((user) => {
              const fullName = [user.first_name, user.last_name].filter(Boolean).join(" ");
              return (
                <tr key={user.username}>
                  <td className={cell}>
                    <span className="font-medium">{user.username}</span>
                    {user.is_admin && (
                      <span className="ml-2 rounded-full bg-oxblood px-2 py-0.5 text-xs text-paper">
                        Admin
                      </span>
                    )}
                    {!user.is_active && (
                      <span className="ml-2 rounded-full bg-paper-deep px-2 py-0.5 text-xs text-ink-soft">
                        Desactivado
                      </span>
                    )}
                  </td>
                  <td className={cell}>{fullName || "—"}</td>
                  <td className={cell}>{user.email ?? "—"}</td>
                  <td className={`${cell} text-right tabular-nums`}>{user.orders_count}</td>
                  <td className={`${cell} text-right tabular-nums`}>{user.favorites_count}</td>
                  <td className={`${cell} whitespace-nowrap`}>{formatDay(user.created_at)}</td>
                  <td className={`${cell} text-right`}>
                    <Link
                      href={`/admin/users/${encodeURIComponent(user.username)}`}
                      className="btn btn-outline btn-sm whitespace-nowrap"
                    >
                      Ver portal
                    </Link>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </>
  );
}
