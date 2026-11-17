"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

/** Enlace del menú que se marca cuando es la página en la que estás. */
export function NavLink({ href, children }: { href: string; children: ReactNode }) {
  const isCurrent = usePathname() === href;

  return (
    <Link
      href={href}
      aria-current={isCurrent ? "page" : undefined}
      className={`rounded-sm px-3 py-2 transition-colors hover:text-oxblood ${
        isCurrent ? "text-oxblood underline decoration-1 underline-offset-8" : "text-ink"
      }`}
    >
      {children}
    </Link>
  );
}
