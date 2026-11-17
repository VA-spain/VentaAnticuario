import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { getCurrentUser } from "@/lib/session";

import { RegisterForm } from "./register-form";

export const metadata: Metadata = {
  title: "Crear cuenta",
  robots: { index: false },
};

export default function RegisterPage() {
  return (
    <section className="mx-auto max-w-md px-5 py-16 sm:py-24">
      <h1 className="font-display text-4xl font-semibold sm:text-5xl">Crear cuenta</h1>
      <p className="mt-3 text-ink-soft">
        Elige tu nombre de usuario y una contraseña. Con la cuenta tendrás tu propio portal, con
        tus compras, tus favoritos y tus datos.
      </p>
      <RegisterForm />
      <p className="mt-8 text-sm text-ink-soft">
        ¿Ya tienes cuenta?{" "}
        <Link href="/login" className="font-medium text-oxblood underline underline-offset-4">
          Inicia sesión
        </Link>
      </p>
      <Suspense fallback={null}>
        <RedirectIfSignedIn />
      </Suspense>
    </section>
  );
}

async function RedirectIfSignedIn() {
  if (await getCurrentUser()) {
    redirect("/account");
  }
  return null;
}
