"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { navLinkClass } from "./nav-style";

/** Enlace que se marca cuando estás en esa página o en una de sus subpáginas. */
export function ActiveLink({ href, children }: { href: string; children: ReactNode }) {
  const pathname = usePathname();
  const isCurrent = pathname === href || (href !== "/" && pathname.startsWith(`${href}/`));

  return (
    <Link href={href} aria-current={isCurrent ? "page" : undefined} className={navLinkClass(isCurrent)}>
      {children}
    </Link>
  );
}
