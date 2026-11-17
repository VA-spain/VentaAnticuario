import type { Metadata } from "next";

import { ContactForm } from "./contact-form";

export const metadata: Metadata = {
  title: "Contacto",
  description: "Escribe a Venta Anticuario sobre cualquier pieza, envío o encargo.",
};

export default function ContactPage() {
  return (
    <section className="mx-auto max-w-2xl px-5 py-16 sm:px-8 sm:py-24">
      <p className="eyebrow">Contacto</p>
      <h1 className="mt-4 font-display text-4xl font-semibold leading-[1.1] sm:text-5xl">
        Escríbenos
      </h1>
      <p className="mt-5 text-lg leading-relaxed text-ink-soft">
        Pregúntanos por cualquier pieza del catálogo, por los envíos o por algo que estés buscando.
      </p>
      <ContactForm />
    </section>
  );
}
