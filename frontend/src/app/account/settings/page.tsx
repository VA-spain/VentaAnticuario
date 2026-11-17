import type { Metadata } from "next";

import { SelfPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Configuración",
  robots: { index: false },
};

export default function Page(props: PageProps<"/account/settings">) {
  return <SelfPortalPage section="settings" searchParams={props.searchParams} />;
}
