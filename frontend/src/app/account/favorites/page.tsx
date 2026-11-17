import type { Metadata } from "next";

import { SelfPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Mis favoritos",
  robots: { index: false },
};

export default function Page(props: PageProps<"/account/favorites">) {
  return <SelfPortalPage section="favorites" searchParams={props.searchParams} />;
}
