"use client"; // Los límites de error tienen que ser componentes de cliente.

import { useEffect } from "react";

export default function ErrorPage({ error, retry }: { error: unknown; retry: () => void }) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <section className="mx-auto flex max-w-xl flex-col items-center px-5 py-20 text-center sm:py-28">
      <h1 className="font-display text-4xl font-semibold sm:text-5xl">Algo ha salido mal</h1>
      <p className="mt-4 text-lg text-ink-soft">No hemos podido cargar esta página.</p>
      <button type="button" onClick={() => retry()} className="btn btn-primary mt-10">
        Volver a intentarlo
      </button>
    </section>
  );
}
