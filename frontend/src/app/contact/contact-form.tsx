"use client";

import { type FormEvent, useState, useTransition } from "react";

import { sendContactMessage } from "@/actions/contact";

type Values = { name: string; email: string; subject: string; message: string };
type Errors = Partial<Record<keyof Values, string>>;

const EMPTY: Values = { name: "", email: "", subject: "", message: "" };
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const MESSAGE_MIN = 10;
const MESSAGE_MAX = 2000;

/** Validación del formulario. De momento solo se hace aquí, en el navegador. */
function validate(values: Values): Errors {
  const errors: Errors = {};
  const name = values.name.trim();
  if (name.length < 2) {
    errors.name = "Escribe tu nombre.";
  } else if (name.length > 120) {
    errors.name = "El nombre no puede pasar de 120 caracteres.";
  }
  const email = values.email.trim();
  if (!email) {
    errors.email = "Escribe tu correo electrónico.";
  } else if (email.length > 254 || !EMAIL_PATTERN.test(email)) {
    errors.email = "Ese correo no parece válido. Revísalo.";
  }
  if (values.subject.trim().length > 200) {
    errors.subject = "El asunto no puede pasar de 200 caracteres.";
  }
  const message = values.message.trim();
  if (message.length < MESSAGE_MIN) {
    errors.message = `Cuéntanos un poco más: al menos ${MESSAGE_MIN} caracteres.`;
  } else if (message.length > MESSAGE_MAX) {
    errors.message = `El mensaje no puede pasar de ${MESSAGE_MAX} caracteres.`;
  }
  return errors;
}

export function ContactForm() {
  const [values, setValues] = useState<Values>(EMPTY);
  const [errors, setErrors] = useState<Errors>({});
  // Tras el primer intento de envío, los errores se corrigen según se escribe.
  const [attempted, setAttempted] = useState(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);
  const [pending, startTransition] = useTransition();

  function update(name: keyof Values, value: string) {
    const next = { ...values, [name]: value };
    setValues(next);
    if (attempted) {
      setErrors(validate(next));
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const found = validate(values);
    setErrors(found);
    setAttempted(true);
    setSendError(null);

    const firstInvalid = (Object.keys(found) as (keyof Values)[])[0];
    if (firstInvalid) {
      const input = event.currentTarget.elements.namedItem(firstInvalid);
      if (input instanceof HTMLElement) {
        input.focus();
      }
      return;
    }

    const clean: Values = {
      name: values.name.trim(),
      email: values.email.trim(),
      subject: values.subject.trim(),
      message: values.message.trim(),
    };
    startTransition(async () => {
      const result = await sendContactMessage(clean);
      if (result.ok) {
        setSent(true);
        setValues(EMPTY);
        setAttempted(false);
      } else {
        setSendError(result.error);
      }
    });
  }

  if (sent) {
    return (
      <div role="status" className="notice-ok mt-10 flex flex-col items-start gap-4 p-6">
        <p className="text-base">
          Hemos recibido tu mensaje. Gracias por escribirnos: te contestaremos por correo.
        </p>
        <button type="button" onClick={() => setSent(false)} className="btn btn-outline">
          Enviar otro mensaje
        </button>
      </div>
    );
  }

  const messageLength = values.message.trim().length;

  return (
    <form noValidate onSubmit={handleSubmit} className="mt-10 flex flex-col gap-6">
      {sendError && (
        <p role="alert" className="notice-error">
          {sendError}
        </p>
      )}

      <div className="grid gap-6 sm:grid-cols-2">
        <TextField
          label="Nombre"
          name="name"
          value={values.name}
          error={errors.name}
          onChange={update}
          autoComplete="name"
        />
        <TextField
          label="Correo electrónico"
          name="email"
          type="email"
          value={values.email}
          error={errors.email}
          onChange={update}
          autoComplete="email"
        />
      </div>

      <TextField
        label="Asunto (opcional)"
        name="subject"
        value={values.subject}
        error={errors.subject}
        onChange={update}
      />

      <label className="field">
        Mensaje
        <textarea
          name="message"
          rows={6}
          value={values.message}
          onChange={(event) => update("message", event.target.value)}
          aria-invalid={errors.message ? true : undefined}
          aria-describedby="message-help"
          className="input resize-y"
        />
        <span id="message-help" className={errors.message ? "field-error" : "field-hint"}>
          {errors.message ?? `${messageLength} de ${MESSAGE_MAX} caracteres`}
        </span>
      </label>

      <div>
        <button type="submit" disabled={pending} className="btn btn-primary px-8 py-3">
          {pending ? "Enviando…" : "Enviar mensaje"}
        </button>
      </div>
    </form>
  );
}

function TextField({
  label,
  name,
  value,
  error,
  onChange,
  type = "text",
  autoComplete,
}: {
  label: string;
  name: keyof Values;
  value: string;
  error?: string;
  onChange: (name: keyof Values, value: string) => void;
  type?: string;
  autoComplete?: string;
}) {
  const errorId = `${name}-error`;
  return (
    <label className="field">
      {label}
      <input
        type={type}
        name={name}
        value={value}
        onChange={(event) => onChange(name, event.target.value)}
        autoComplete={autoComplete}
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        className="input"
      />
      {error && (
        <span id={errorId} className="field-error">
          {error}
        </span>
      )}
    </label>
  );
}
