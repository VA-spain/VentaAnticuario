import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { logout } from "@/lib/actions";
import { getCurrentUser } from "@/lib/session";

export const metadata: Metadata = {
  title: "Sesión iniciada",
  robots: { index: false },
};

export default function SignedInPage() {
  return (
    <section className="mx-auto flex max-w-xl flex-col items-center px-5 py-20 text-center sm:py-28">
      <Suspense
        fallback={
          <p role="status" className="text-ink-soft">
            Comprobando tu sesión…
          </p>
        }
      >
        <SignedIn />
      </Suspense>
    </section>
  );
}

/** Solo se muestra con una sesión que el backend dé por válida; si no, se va al login. */
async function SignedIn() {
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }

  return (
    <>
      <span className="flex size-16 items-center justify-center rounded-full bg-oxblood text-paper">
        <svg
          aria-hidden="true"
          viewBox="0 0 24 24"
          className="size-8"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M5 12.5l4.5 4.5L19 7.5" />
        </svg>
      </span>
      <h1 className="mt-8 font-display text-4xl font-semibold leading-tight sm:text-5xl">
        Has iniciado sesión correctamente
      </h1>
      <p className="mt-4 text-lg text-ink-soft">
        Sesión iniciada como <strong className="font-medium text-ink">{user.email}</strong>
      </p>
      <div className="mt-10 flex flex-wrap items-center justify-center gap-3">
        <Link href="/" className="btn btn-primary">
          Ver el catálogo
        </Link>
        <form action={logout}>
          <button type="submit" className="btn btn-outline">
            Cerrar sesión
          </button>
        </form>
      </div>
    </>
  );
}
