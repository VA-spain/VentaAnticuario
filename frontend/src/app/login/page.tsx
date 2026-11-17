import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { getCurrentUser } from "@/lib/session";

import { LoginForm } from "./login-form";

export const metadata: Metadata = {
  title: "Iniciar sesión",
  robots: { index: false },
};

export default function LoginPage() {
  return (
    <section className="mx-auto max-w-md px-5 py-16 sm:py-24">
      <h1 className="font-display text-4xl font-semibold sm:text-5xl">Iniciar sesión</h1>
      <p className="mt-3 text-ink-soft">Accede con tu nombre de usuario y tu contraseña.</p>
      <LoginForm />
      <p className="mt-8 text-sm text-ink-soft">
        ¿No tienes cuenta?{" "}
        <Link href="/register" className="font-medium text-oxblood underline underline-offset-4">
          Crea una
        </Link>
      </p>
      <Suspense fallback={null}>
        <RedirectIfSignedIn />
      </Suspense>
    </section>
  );
}

/** Quien ya tiene una sesión válida no necesita el formulario. */
async function RedirectIfSignedIn() {
  if (await getCurrentUser()) {
    redirect("/signed-in");
  }
  return null;
}
