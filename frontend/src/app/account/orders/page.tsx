import type { Metadata } from "next";

import { SelfPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Mis compras",
  robots: { index: false },
};

export default function Page(props: PageProps<"/account/orders">) {
  return <SelfPortalPage section="orders" searchParams={props.searchParams} />;
}
