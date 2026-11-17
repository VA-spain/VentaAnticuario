import type { Metadata } from "next";

import { AdminPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Favoritos del cliente",
  robots: { index: false },
};

export default function Page(props: PageProps<"/admin/users/[username]/favorites">) {
  return <AdminPortalPage section="favorites" params={props.params} />;
}
