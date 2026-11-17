import Link from "next/link";
import type { ReactNode } from "react";

export type PortalSection = "overview" | "orders" | "favorites" | "settings";
export type PortalScope = "self" | "admin";

const TABS: { section: PortalSection; label: string; path: string }[] = [
  { section: "overview", label: "Resumen", path: "" },
  { section: "orders", label: "Compras", path: "/orders" },
  { section: "favorites", label: "Favoritos", path: "/favorites" },
  { section: "settings", label: "Configuración", path: "/settings" },
];

/** El portal propio cuelga de /account; el de un cliente visto por un administrador, de /admin. */
export function portalBase(scope: PortalScope, username: string): string {
  return scope === "self" ? "/account" : `/admin/users/${encodeURIComponent(username)}`;
}

type Props = {
  scope: PortalScope;
  username: string;
  title: string;
  active: PortalSection;
  children: ReactNode;
};

export function PortalShell({ scope, username, title, active, children }: Props) {
  const base = portalBase(scope, username);

  return (
    <>
      {scope === "admin" && (
        <p className="notice-ok mb-8">
          Estás viendo el portal de <strong className="font-semibold">{username}</strong> como
          administrador: puedes modificar sus pedidos, sus favoritos y sus datos.{" "}
          <Link href="/admin" className="font-medium text-oxblood underline underline-offset-4">
            Volver a todos los usuarios
          </Link>
        </p>
      )}
      <p className="eyebrow">{scope === "self" ? "Mi portal" : "Portal de cliente"}</p>
      <h1 className="mt-3 font-display text-4xl font-semibold sm:text-5xl">{title}</h1>
      <nav
        aria-label="Secciones del portal"
        className="mt-8 flex gap-x-6 overflow-x-auto border-b border-line text-sm"
      >
        {TABS.map((tab) => {
          const current = tab.section === active;
          return (
            <Link
              key={tab.section}
              href={`${base}${tab.path}`}
              aria-current={current ? "page" : undefined}
              className={`-mb-px whitespace-nowrap border-b-2 py-3 transition-colors ${
                current
                  ? "border-oxblood font-medium text-oxblood"
                  : "border-transparent text-ink-soft hover:text-ink"
              }`}
            >
              {tab.label}
            </Link>
          );
        })}
      </nav>
      <div className="mt-10">{children}</div>
    </>
  );
}
