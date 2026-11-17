import { type ReactNode, Suspense } from "react";

import { firstParam } from "@/lib/form";
import { requireAdmin, requireUser } from "@/lib/session";
import { getProfile } from "@/lib/shop";

import { FavoritesView } from "./favorites-view";
import { OrdersView } from "./orders-view";
import { PortalOverview } from "./overview";
import { type PortalSection, PortalShell, portalBase } from "./portal-shell";
import { ProfileForm } from "./profile-form";

type SearchParams = Record<string, string | string[] | undefined>;

function Frame({ children }: { children: ReactNode }) {
  return <section className="mx-auto max-w-5xl px-5 py-12 sm:px-8 sm:py-16">{children}</section>;
}

function Loading() {
  return (
    <p role="status" className="text-ink-soft">
      Cargando el portal…
    </p>
  );
}

/** Portal del usuario con la sesión iniciada (/account/...). */
export function SelfPortalPage({
  section,
  searchParams,
}: {
  section: PortalSection;
  searchParams: Promise<SearchParams>;
}) {
  return (
    <Frame>
      <Suspense fallback={<Loading />}>
        <SelfPortal section={section} searchParams={searchParams} />
      </Suspense>
    </Frame>
  );
}

/** Portal de cualquier usuario visto por un administrador (/admin/users/NOMBRE/...). */
export function AdminPortalPage({
  section,
  params,
}: {
  section: PortalSection;
  params: Promise<{ username: string }>;
}) {
  return (
    <Frame>
      <Suspense fallback={<Loading />}>
        <AdminPortal section={section} params={params} />
      </Suspense>
    </Frame>
  );
}

async function SelfPortal({
  section,
  searchParams,
}: {
  section: PortalSection;
  searchParams: Promise<SearchParams>;
}) {
  const user = await requireUser();
  const params = await searchParams;

  return (
    <PortalShell
      scope="self"
      username={user.username}
      title={`Hola, ${user.first_name || user.username}`}
      active={section}
    >
      <SectionContent section={section} target="me" base="/account" canEdit={false} params={params} />
    </PortalShell>
  );
}

async function AdminPortal({
  section,
  params,
}: {
  section: PortalSection;
  params: Promise<{ username: string }>;
}) {
  await requireAdmin();
  const { username } = await params;

  return (
    <PortalShell scope="admin" username={username} title={username} active={section}>
      <SectionContent
        section={section}
        target={username}
        base={portalBase("admin", username)}
        canEdit
        params={{}}
      />
    </PortalShell>
  );
}

async function SectionContent({
  section,
  target,
  base,
  canEdit,
  params,
}: {
  section: PortalSection;
  target: string;
  base: string;
  canEdit: boolean;
  params: SearchParams;
}) {
  switch (section) {
    case "overview":
      return (
        <PortalOverview target={target} base={base} welcome={firstParam(params.welcome) === "1"} />
      );
    case "orders":
      return (
        <OrdersView
          target={target}
          canEdit={canEdit}
          highlight={Number(firstParam(params.bought)) || undefined}
        />
      );
    case "favorites":
      return <FavoritesView target={target} canEdit={canEdit} />;
    case "settings":
      return <ProfileForm profile={await getProfile(target)} target={target} />;
  }
}
