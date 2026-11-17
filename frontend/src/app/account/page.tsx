import type { Metadata } from "next";

import { SelfPortalPage } from "@/components/portal/portal-pages";

export const metadata: Metadata = {
  title: "Mi portal",
  robots: { index: false },
};

export default function Page(props: PageProps<"/account">) {
  return <SelfPortalPage section="overview" searchParams={props.searchParams} />;
}
