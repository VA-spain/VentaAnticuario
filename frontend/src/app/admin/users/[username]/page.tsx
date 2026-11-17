import type { Metadata } from "next";

import { AdminPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Portal de cliente",
  robots: { index: false },
};

export default function Page(props: PageProps<"/admin/users/[username]">) {
  return <AdminPortalPage section="overview" params={props.params} />;
}
