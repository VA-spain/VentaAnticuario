import type { Metadata } from "next";

import { AdminPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Datos del cliente",
  robots: { index: false },
};

export default function Page(props: PageProps<"/admin/users/[username]/settings">) {
  return <AdminPortalPage section="settings" params={props.params} />;
}
