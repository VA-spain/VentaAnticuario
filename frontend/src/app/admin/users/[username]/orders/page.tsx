import type { Metadata } from "next";

import { AdminPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Compras del cliente",
  robots: { index: false },
};

export default function Page(props: PageProps<"/admin/users/[username]/orders">) {
  return <AdminPortalPage section="orders" params={props.params} />;
}
